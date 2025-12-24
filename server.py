from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
# Senin linkini ve şifreni buraya hatasız şekilde yerleştirdim knk.
MONGO_URI = "mongodb+srv://erdembctk01_db_user:TqSSkvbFirlm8lyb@cluster0.o27rfmv.mongodb.net/?appName=Cluster0" 

client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- GÖRSEL PANEL (Yeni İsteklerine Göre Güncellendi) ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>StokTakip Pro - Yönetim Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 font-sans p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-center">
            <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
                <p class="text-slate-400 text-[10px] font-black uppercase tracking-widest">Toplam Stok</p>
                <h2 id="stat-total-items" class="text-4xl font-black text-slate-800 mt-2">0</h2>
            </div>
            <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-red-100">
                <p class="text-red-400 text-[10px] font-black uppercase tracking-widest">Kritik Stok</p>
                <h2 id="stat-crit-count" class="text-4xl font-black text-red-500 mt-2">0</h2>
            </div>
            <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-emerald-100">
                <p class="text-emerald-400 text-[10px] font-black uppercase tracking-widest">Toplam Değer</p>
                <h2 id="stat-total-val" class="text-4xl font-black text-emerald-600 mt-2">₺0</h2>
            </div>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8">
            <div class="flex flex-col md:flex-row gap-4">
                <div class="relative flex-1">
                    <i class="fas fa-search absolute left-5 top-5 text-slate-400"></i>
                    <input id="search" oninput="yukle()" type="text" placeholder="Hızlı ara..." class="w-full pl-14 pr-6 py-4 bg-slate-50 rounded-2xl outline-none font-bold">
                </div>
                <button onclick="document.getElementById('ekle-form').classList.toggle('hidden')" class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-2xl font-black shadow-lg transition-all active:scale-95">
                    + YENİ PARÇA EKLE
                </button>
            </div>

            <div id="ekle-form" class="hidden mt-8 grid grid-cols-1 md:grid-cols-4 gap-4 border-t pt-8">
                <input id="in-name" type="text" placeholder="Parça Adı / Kod" class="p-4 bg-slate-50 rounded-xl outline-none font-bold">
                <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-xl outline-none font-bold">
                <input id="in-price" type="number" placeholder="Birim Fiyat (₺)" class="p-4 bg-slate-50 rounded-xl outline-none font-bold">
                <button onclick="hizliEkle()" class="bg-emerald-500 hover:bg-emerald-600 text-white font-black rounded-xl">KAYDET</button>
            </div>
        </div>

        <div class="bg-white rounded-[2.5rem] shadow-sm border border-slate-100 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase">
                    <tr><th class="px-10 py-6">Parça & Kategori</th><th class="px-10 py-6 text-center">Stok</th><th class="px-10 py-6 text-right">İşlem</th></tr>
                </thead>
                <tbody id="list" class="divide-y divide-slate-50"></tbody>
            </table>
        </div>
    </div>

    <script>
        async function yukle() {
            try {
                const res = await fetch('/api/products');
                const data = await res.json();
                const query = document.getElementById('search').value.toLowerCase();
                const list = document.getElementById('list');
                let tStock = 0; let tVal = 0; let crit = 0;
                
                list.innerHTML = data.filter(i => i.name.toLowerCase().includes(query)).map(i => {
                    const isCrit = i.stock <= 10;
                    if(isCrit) crit++;
                    tStock += i.stock;
                    tVal += (i.stock * (i.price || 0));
                    return `
                    <tr class="\${isCrit ? 'bg-red-50/50' : 'hover:bg-slate-50'} transition-all">
                        <td class="px-10 py-6">
                            <div class="font-black text-slate-800 uppercase text-lg">\${i.name}</div>
                            <div class="text-[10px] font-bold text-blue-500 uppercase">\${i.category || 'GENEL'}</div>
                        </td>
                        <td class="px-10 py-6 text-center">
                            <div class="flex items-center justify-center gap-4 bg-white border rounded-2xl p-1 w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('\${i._id}', -1)" class="w-10 h-10 hover:bg-red-50 text-red-500 font-bold">-</button>
                                <span class="w-10 font-black text-xl">\${i.stock}</span>
                                <button onclick="stokGuncelle('\${i._id}', 1)" class="w-10 h-10 hover:bg-green-50 text-green-500 font-bold">+</button>
                            </div>
                        </td>
                        <td class="px-10 py-6 text-right">
                            <button onclick="sil('\${i._id}')" class="text-slate-300 hover:text-red-600 p-3"><i class="fas fa-trash-alt text-lg"></i></button>
                        </td>
                    </tr>`;
                }).join('');

                document.getElementById('stat-total-items').innerText = tStock;
                document.getElementById('stat-crit-count').innerText = crit;
                document.getElementById('stat-total-val').innerText = '₺' + tVal.toLocaleString();
            } catch (e) { console.log("Bağlantı kuruluyor..."); }
        }

        async function hizliEkle() {
            const name = document.getElementById('in-name').value;
            const category = document.getElementById('in-cat').value;
            const price = document.getElementById('in-price').value;

            if(!name) { alert("Lütfen parça adı girin!"); return; }

            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: name, 
                    category: category, 
                    price: parseFloat(price || 0), 
                    stock: 0
                })
            });
            
            // Kutuları temizle ve gizle
            document.getElementById('in-name').value = '';
            document.getElementById('in-cat').value = '';
            document.getElementById('in-price').value = '';
            document.getElementById('ekle-form').classList.add('hidden');
            yukle();
        }

        async function stokGuncelle(id, miktar) {
            await fetch(\`/api/products/\${id}/stock\`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change: miktar})
            });
            yukle();
        }

        async function sil(id) {
            if(confirm('Silinsin mi?')) { await fetch('/api/products/'+id, {method: 'DELETE'}); yukle(); }
        }
        yukle();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PANEL)

@app.route('/api/products', methods=['GET'])
def get_p():
    items = list(db.products.find())
    for i in items: i['_id'] = str(i['_id'])
    return jsonify(items)

@app.route('/api/products', methods=['POST'])
def add_p():
    db.products.insert_one(request.json)
    return jsonify({"ok": True})

@app.route('/api/products/<id>/stock', methods=['PUT'])
def update_stock(id):
    change = request.json.get('change', 0)
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

@app.route('/api/products/<id>', methods=['DELETE'])
def del_p(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
