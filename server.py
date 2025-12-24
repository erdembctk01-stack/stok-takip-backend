from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import sys

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI (En Sağlam Format) ---
# Buradaki linki ve şifreyi senin bilgilerine göre güncelledim
MONGO_URI = "mongodb+srv://erdembctk01_db_user:TqSSkvbFirlm8lyb@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.stok_veritabani
    # Bağlantıyı test et
    client.admin.command('ping')
    print("MongoDB Bağlantısı Başarılı! ✅")
except Exception as e:
    print(f"MongoDB Bağlantı Hatası: {e}")
    sys.exit(1)

# --- PANEL TASARIMI (Gelişmiş Hata Takibi İle) ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>StokTakip Pro | Yönetim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-center">
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                <p class="text-slate-400 text-[10px] font-black uppercase">Toplam Çeşit</p>
                <h2 id="stat-total-items" class="text-4xl font-black text-slate-800 mt-2">0</h2>
            </div>
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-red-100">
                <p class="text-red-400 text-[10px] font-black uppercase">Kritik Stok</p>
                <h2 id="stat-crit-count" class="text-4xl font-black text-red-500 mt-2">0</h2>
            </div>
            <div class="bg-white p-6 rounded-3xl shadow-sm border border-emerald-100">
                <p class="text-emerald-400 text-[10px] font-black uppercase">Toplam Değer</p>
                <h2 id="stat-total-val" class="text-4xl font-black text-emerald-600 mt-2">₺0</h2>
            </div>
        </div>

        <div class="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 mb-8">
            <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                <input id="in-code" type="text" placeholder="Kod" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                <input id="in-name" type="text" placeholder="Ürün İsmi" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                <input id="in-price" type="number" placeholder="Fiyat" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                <button onclick="hizliEkle()" class="bg-blue-600 text-white font-black rounded-xl hover:bg-blue-700 transition-all">KAYDET</button>
            </div>
        </div>

        <input id="search" oninput="yukle()" type="text" placeholder="İsim veya kodla ara..." class="w-full p-4 mb-6 bg-white rounded-2xl shadow-sm outline-none font-bold border">

        <div class="bg-white rounded-3xl shadow-sm border overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase">
                    <tr><th class="px-10 py-6">Ürün</th><th class="px-10 py-6">Kategori</th><th class="px-10 py-6 text-center">Stok</th><th class="px-10 py-6 text-right">Sil</th></tr>
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
                
                let tStock = 0, tVal = 0, crit = 0, count = 0;
                
                list.innerHTML = data.filter(i => 
                    (i.name || "").toLowerCase().includes(query) || 
                    (i.code || "").toLowerCase().includes(query)
                ).map(i => {
                    if(i.stock <= 10) crit++;
                    tStock += (i.stock || 0);
                    tVal += ((i.stock || 0) * (i.price || 0));
                    count++;
                    return `
                    <tr class="hover:bg-slate-50">
                        <td class="px-10 py-6">
                            <div class="text-[10px] font-bold text-blue-600 uppercase">\${i.code || 'KODSUZ'}</div>
                            <div class="font-black text-slate-800 uppercase">\${i.name}</div>
                        </td>
                        <td class="px-10 py-6 font-bold text-slate-400 uppercase text-xs">\${i.category || '-'}</td>
                        <td class="px-10 py-6">
                            <div class="flex items-center justify-center gap-2">
                                <button onclick="stokGuncelle('\${i._id}', -1)" class="w-8 h-8 bg-slate-100 rounded-lg">-</button>
                                <span class="font-bold w-8 text-center">\${i.stock}</span>
                                <button onclick="stokGuncelle('\${i._id}', 1)" class="w-8 h-8 bg-slate-100 rounded-lg">+</button>
                            </div>
                        </td>
                        <td class="px-10 py-6 text-right">
                            <button onclick="sil('\${i._id}')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>`;
                }).join('');

                document.getElementById('stat-total-items').innerText = count;
                document.getElementById('stat-crit-count').innerText = crit;
                document.getElementById('stat-total-val').innerText = '₺' + tVal.toLocaleString();
            } catch (e) { console.error("Yükleme hatası:", e); }
        }

        async function hizliEkle() {
            const payload = {
                code: document.getElementById('in-code').value,
                name: document.getElementById('in-name').value,
                category: document.getElementById('in-cat').value,
                price: parseFloat(document.getElementById('in-price').value || 0),
                stock: 0
            };

            if(!payload.name) return alert("İsim şart!");

            const res = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            if(res.ok) {
                document.querySelectorAll('input').forEach(i => i.id !== 'search' ? i.value = '' : null);
                yukle();
            } else {
                alert("Kayıt sırasında hata oluştu!");
            }
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
            if(confirm('Sil?')) { await fetch('/api/products/'+id, {method: 'DELETE'}); yukle(); }
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
    try:
        db.products.insert_one(request.json)
        return jsonify({"ok": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    app.run(host='0.0.0.0', port=port, debug=False)
