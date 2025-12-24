from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import sys

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.stok_veritabani
    client.admin.command('ping')
    print("MongoDB Bağlantısı Başarılı! ✅")
except Exception as e:
    print(f"MongoDB Bağlantı Hatası: {e}")
    sys.exit(1)

# --- PANEL TASARIMI ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Özcan Oto Servis | Stok Takip</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .modal { transition: opacity 0.25s ease; }
        body.modal-active { overflow: hidden; }
    </style>
</head>
<body class="bg-slate-50 font-sans p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <h1 class="text-3xl font-black text-slate-800 tracking-tighter uppercase italic">
                <i class="fas fa-tools text-blue-600"></i> ÖZCAN OTO SERVİS
            </h1>
            <div class="flex gap-4 w-full md:w-auto">
                <div class="bg-white px-6 py-3 rounded-2xl shadow-sm border border-slate-100 flex-1 text-center">
                    <p class="text-[9px] font-black text-slate-400 uppercase">Kritik Parçalar</p>
                    <h2 id="stat-crit-count" class="text-xl font-black text-red-500">0</h2>
                </div>
                <button onclick="toggleModal()" class="bg-emerald-600 hover:bg-emerald-700 px-6 py-3 rounded-2xl shadow-lg flex-1 text-center text-white transition-all active:scale-95 group">
                    <p class="text-[9px] font-black uppercase opacity-80 group-hover:opacity-100">Kasa Durumu</p>
                    <h2 class="text-xl font-black">TOPLAM DEĞER <i class="fas fa-chevron-right ml-1 text-sm"></i></h2>
                </button>
            </div>
        </div>

        <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8">
            <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:ring-2 ring-blue-500">
                <input id="in-name" type="text" placeholder="Parça İsmi" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:ring-2 ring-blue-500">
                <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:ring-2 ring-blue-500">
                <input id="in-price" type="number" placeholder="Birim Fiyat (₺)" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border focus:ring-2 ring-blue-500">
                <button onclick="hizliEkle()" class="bg-blue-600 hover:bg-blue-700 text-white font-black rounded-xl shadow-lg transition-all">SİSTEME EKLE</button>
            </div>
        </div>

        <div class="relative mb-6">
            <i class="fas fa-search absolute left-5 top-5 text-slate-400"></i>
            <input id="search" oninput="yukle()" type="text" placeholder="Parça adı veya koduyla hızlı ara..." class="w-full pl-14 pr-6 py-4 bg-white rounded-2xl shadow-sm outline-none font-bold border-2 border-transparent focus:border-blue-200">
        </div>

        <div class="bg-white rounded-[2.5rem] shadow-sm border border-slate-100 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase">
                    <tr>
                        <th class="px-10 py-6">Parça Bilgisi</th>
                        <th class="px-10 py-6">Kategori</th>
                        <th class="px-10 py-6 text-center">Stok</th>
                        <th class="px-10 py-6 text-right">İşlem</th>
                    </tr>
                </thead>
                <tbody id="list" class="divide-y divide-slate-50"></tbody>
            </table>
        </div>
    </div>

    <div id="modal" class="modal opacity-0 pointer-events-none fixed w-full h-full top-0 left-0 flex items-center justify-center z-50">
        <div onclick="toggleModal()" class="modal-overlay absolute w-full h-full bg-slate-900 opacity-50"></div>
        <div class="modal-container bg-white w-11/12 md:max-w-md mx-auto rounded-[2.5rem] shadow-2xl z-50 overflow-y-auto border-4 border-emerald-500">
            <div class="modal-content py-10 px-8 text-center">
                <div class="bg-emerald-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <i class="fas fa-wallet text-3xl text-emerald-600"></i>
                </div>
                <h3 class="text-slate-400 font-black uppercase tracking-widest text-xs mb-2">Depo Toplam Değeri</h3>
                <div id="total-val-display" class="text-5xl font-black text-slate-800 tracking-tighter mb-8">₺0</div>
                <button onclick="toggleModal()" class="w-full bg-slate-800 text-white font-black py-4 rounded-2xl hover:bg-slate-700 transition-all">PENCEREYİ KAPAT</button>
            </div>
        </div>
    </div>

    <script>
        let currentTotalVal = 0;

        function toggleModal() {
            const modal = document.getElementById('modal');
            modal.classList.toggle('opacity-0');
            modal.classList.toggle('pointer-events-none');
            document.body.classList.toggle('modal-active');
            document.getElementById('total-val-display').innerText = '₺' + currentTotalVal.toLocaleString();
        }

        async function yukle() {
            try {
                const res = await fetch('/api/products');
                const data = await res.json();
                const query = document.getElementById('search').value.toLowerCase();
                const list = document.getElementById('list');
                
                let tVal = 0, crit = 0;
                
                list.innerHTML = data.filter(i => 
                    (i.name || "").toLowerCase().includes(query) || 
                    (i.code || "").toLowerCase().includes(query)
                ).map(i => {
                    const stock = i.stock || 0;
                    const price = i.price || 0;
                    const isVeryLow = stock <= 2;
                    
                    if(stock <= 10) crit++;
                    tVal += (stock * price);

                    return `
                    <tr class="${isVeryLow ? 'bg-red-50' : 'hover:bg-slate-50'} transition-all">
                        <td class="px-10 py-6">
                            <div class="flex flex-col">
                                <span class="text-[11px] font-black text-slate-900 bg-yellow-400 w-fit px-2 rounded mb-1 uppercase tracking-tighter">Birim: ₺${price.toLocaleString()}</span>
                                <span class="text-[11px] font-bold text-blue-600 uppercase tracking-tight">${i.code || 'KODSUZ'}</span>
                                <span class="font-black uppercase text-lg leading-tight ${isVeryLow ? 'text-red-600 underline decoration-2' : 'text-slate-800'}">${i.name}</span>
                            </div>
                        </td>
                        <td class="px-10 py-6 font-bold text-slate-500 uppercase text-xs">${i.category || '-'}</td>
                        <td class="px-10 py-6 text-center">
                            <div class="flex items-center justify-center gap-4 bg-white border rounded-2xl p-1 w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('${i._id}', -1)" class="w-10 h-10 text-red-500 font-bold hover:bg-red-50 rounded-xl">-</button>
                                <span class="w-10 font-black text-xl">${stock}</span>
                                <button onclick="stokGuncelle('${i._id}', 1)" class="w-10 h-10 text-green-500 font-bold hover:bg-green-50 rounded-xl">+</button>
                            </div>
                        </td>
                        <td class="px-10 py-6 text-right">
                            <button onclick="sil('${i._id}')" class="text-slate-200 hover:text-red-600 p-3 transition-colors"><i class="fas fa-trash-alt text-lg"></i></button>
                        </td>
                    </tr>`;
                }).join('');

                currentTotalVal = tVal;
                document.getElementById('stat-crit-count').innerText = crit;
            } catch (e) { console.error("Veri hatası:", e); }
        }

        async function hizliEkle() {
            const payload = {
                code: document.getElementById('in-code').value,
                name: document.getElementById('in-name').value,
                category: document.getElementById('in-cat').value,
                price: parseFloat(document.getElementById('in-price').value || 0),
                stock: 0
            };
            if(!payload.name) return alert("Parça ismini yazın!");
            const res = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if(res.ok) {
                document.querySelectorAll('input:not(#search)').forEach(i => i.value = '');
                yukle();
            }
        }

        async function stokGuncelle(id, m) {
            await fetch(`/api/products/${id}/stock`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change: m})
            });
            yukle();
        }

        async function sil(id) {
            if(confirm('Parçayı sileyim mi?')) { await fetch('/api/products/'+id, {method: 'DELETE'}); yukle(); }
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
    return jsonify({"ok": True}), 201

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
