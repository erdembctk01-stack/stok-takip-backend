from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
# ÖNEMLİ: localhost internette ÇALIŞMAZ. MongoDB Atlas'tan aldığın linki buraya koymalısın!
MONGO_URI = "mongodb://localhost:27017" 
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>StokTakip Pro - Hızlı Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 font-sans p-4 md:p-10">
    <div class="max-w-5xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4 mb-8">
            <div class="relative w-full md:w-96">
                <i class="fas fa-search absolute left-4 top-4 text-slate-400"></i>
                <input id="search" oninput="yukle()" type="text" placeholder="Parça ara..." class="w-full pl-12 pr-4 py-3 bg-white rounded-2xl shadow-sm outline-none border border-transparent focus:border-blue-500 font-bold">
            </div>
            <button onclick="hizliEkle()" class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-2xl font-black shadow-lg shadow-blue-100 transition-all active:scale-95">
                <i class="fas fa-plus mr-2"></i> YENİ PARÇA EKLE
            </button>
        </div>

        <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase tracking-widest">
                    <tr>
                        <th class="px-8 py-5">Eşya Adı</th>
                        <th class="px-8 py-5 text-center">Stok Yönetimi</th>
                        <th class="px-8 py-5 text-right">İşlem</th>
                    </tr>
                </thead>
                <tbody id="list" class="divide-y divide-slate-50"></tbody>
            </table>
        </div>
    </div>

    <script>
        async function yukle() {
            const res = await fetch('/api/products');
            let data = await res.json();
            const query = document.getElementById('search').value.toLowerCase();
            const list = document.getElementById('list');
            
            list.innerHTML = data.filter(i => i.name.toLowerCase().includes(query)).map(i => `
                <tr class="hover:bg-slate-50 transition-all">
                    <td class="px-8 py-6 font-black text-slate-700 uppercase">\${i.name}</td>
                    <td class="px-8 py-6">
                        <div class="flex items-center justify-center gap-4 bg-slate-100 w-fit mx-auto rounded-xl p-1">
                            <button onclick="stokGuncelle('\${i._id}', -1)" class="w-10 h-10 bg-white rounded-lg shadow-sm hover:bg-red-50 text-red-500 font-bold">-</button>
                            <span class="w-12 text-center font-black text-lg">\${i.stock}</span>
                            <button onclick="stokGuncelle('\${i._id}', 1)" class="w-10 h-10 bg-white rounded-lg shadow-sm hover:bg-green-50 text-green-500 font-bold">+</button>
                        </div>
                    </td>
                    <td class="px-8 py-6 text-right">
                        <button onclick="sil('\${i._id}')" class="text-slate-300 hover:text-red-500 transition-colors"><i class="fas fa-trash-alt text-xl"></i></button>
                    </td>
                </tr>`).join('');
        }

        async function hizliEkle() {
            const ad = prompt("Eklenecek parçanın adını yaz:");
            if(!ad) return;
            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: ad, stock: 0})
            });
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
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
