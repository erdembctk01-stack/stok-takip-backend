from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:TqSSkvbFirlm8lyb@cluster0.o27rfmv.mongodb.net/?appName=Cluster0" 

client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- GELİŞMİŞ YÖNETİM PANELİ ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>StokTakip Pro | Depo Yönetimi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 font-sans p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-center">
            <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
                <p class="text-slate-400 text-[10px] font-black uppercase tracking-widest">Toplam Çeşit</p>
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
            <h3 class="font-black text-slate-800 mb-6 flex items-center gap-2">
                <i class="fas fa-plus-circle text-blue-600"></i> YENİ PARÇA KAYDI
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                <input id="in-code" type="text" placeholder="Ürün Kodu" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:border-blue-500 transition-all">
                <input id="in-name" type="text" placeholder="Ürün İsmi" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:border-blue-500 transition-all">
                <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:border-blue-500 transition-all">
                <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:border-blue-500 transition-all">
                <button onclick="hizliEkle()" class="bg-blue-600 hover:bg-blue-700 text-white font-black rounded-xl shadow-lg transition-all active:scale-95">VERİTABANINA GÖNDER</button>
            </div>
        </div>

        <div class="relative mb-6">
            <i class="fas fa-search absolute left-5 top-5 text-slate-400"></i>
            <input id="search" oninput="yukle()" type="text" placeholder="Ürün ismi veya kodu ile ara..." class="w-full pl-14 pr-6 py-4 bg-white rounded-2xl shadow-sm outline-none font-bold border-2 border-transparent focus:border-blue-200 transition-all">
        </div>

        <div class="bg-white rounded-[2.5rem] shadow-sm border border-slate-100 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase">
                    <tr>
                        <th class="px-10 py-6">Ürün Bilgisi</th>
                        <th class="px-10 py-6">Kategori</th>
                        <th class="px-10 py-6 text-center">Stok Durumu</th>
                        <th class="px-10 py-6 text-right">İşlem</th>
                    </tr>
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
                
                let tStock = 0; let tVal = 0; let crit = 0; let count = 0;
                
                const filteredData = data.filter(i => 
                    (i.name || "").toLowerCase().includes(query) || 
                    (i.code || "").toLowerCase().includes(query)
                );

                list.innerHTML = filteredData.map(i => {
                    const isCrit = i.stock <= 10;
                    if(isCrit) crit++;
                    tStock += i.stock;
                    tVal += (i.stock * (i.price || 0));
                    count++;
                    
                    return `
                    <tr class="\${isCrit ? 'bg-red-50/50' : 'hover:bg-slate-50'} transition-all">
                        <td class="px-10 py-6">
                            <div class="text-[10px] font-black text-blue-600 tracking-tighter uppercase">\${i.code || 'KODSUZ'}</div>
                            <div class="font-black text-slate-800 uppercase text-lg">\${i.name}</div>
                        </td>
                        <td class="px-10 py-6 font-bold text-slate-500 uppercase text-sm">\${i.category || '-'}</td>
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

                document.getElementById('stat-total-items').innerText = count;
                document.getElementById('stat-crit-count').innerText = crit;
                document.getElementById('stat-total-val').innerText = '₺' + tVal.toLocaleString();
            } catch (e) { console.log("Veriler yükleniyor..."); }
        }

        async function hizliEkle() {
            const code = document.getElementById('in-code').value;
            const name = document.getElementById('in-name').value;
            const cat = document.getElementById('in-cat').value;
            const price = document.getElementById('in-price').value;

            if(!name) { alert("Lütfen en azından bir isim girin!"); return; }

            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    code: code,
                    name: name,
                    category: cat,
                    price: parseFloat(price || 0),
                    stock: 0
                })
            });

            // Formu temizle
            document.getElementById('in-code').value = '';
            document.getElementById('in-name').value = '';
            document.getElementById('in-cat').value = '';
            document.getElementById('in-price').value = '';
            yukle();
        }

        async function stokGuncelle(id, m) {
            await fetch(\`/api/products/\${id}/stock\`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change: m})
            });
            yukle();
        }

        async function sil(id) {
            if(confirm('Ürün silinsin mi?')) { await fetch('/api/products/'+id, {method: 'DELETE'}); yukle(); }
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

