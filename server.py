from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
# NOT: localhost linki Render'da çalışmaz, ama istediğin gibi yerleştirdim.
MONGO_URI = "mongodb://localhost:27017" 

client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- GÖRSEL PANEL TASARIMI (index.html buraya gömüldü) ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>StokTakip Pro - Canlı Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 font-sans">
    <nav class="bg-white border-b px-8 py-4 flex justify-between items-center shadow-sm">
        <h1 class="text-xl font-black text-blue-600 italic">StokTakip Pro</h1>
        <div class="text-sm font-bold text-slate-500">Durum: <span class="text-green-500 font-black">● CANLI</span></div>
    </nav>

    <div class="max-w-6xl mx-auto p-6 md:p-10">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 text-center">
            <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
                <p class="text-slate-400 text-[10px] font-black uppercase">Toplam Çeşit</p>
                <h2 id="total-count" class="text-5xl font-black text-slate-800 mt-2">0</h2>
            </div>
            <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-red-100">
                <p class="text-red-400 text-[10px] font-black uppercase">Kritik Stok</p>
                <h2 id="crit-count" class="text-5xl font-black text-red-500 mt-2">0</h2>
            </div>
            <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
                <p class="text-slate-400 text-[10px] font-black uppercase">Depo Değeri</p>
                <h2 id="total-val" class="text-5xl font-black text-emerald-500 mt-2">₺0</h2>
            </div>
        </div>

        <div class="bg-white p-10 rounded-[2.5rem] shadow-xl border border-slate-50 mb-12">
            <h3 class="text-xl font-black mb-8 text-slate-800 italic">Yeni Parça Kaydı</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <input id="n" type="text" placeholder="Parça Adı" class="p-5 bg-slate-50 rounded-2xl outline-none font-bold">
                <input id="c" type="text" placeholder="Kategori" class="p-5 bg-slate-50 rounded-2xl outline-none font-bold">
                <input id="s" type="number" placeholder="Stok" class="p-5 bg-slate-50 rounded-2xl outline-none font-bold">
                <input id="p" type="number" placeholder="Fiyat" class="p-5 bg-slate-50 rounded-2xl outline-none font-bold">
                <input id="l" type="number" placeholder="Limit" class="p-5 bg-slate-50 rounded-2xl outline-none font-bold">
            </div>
            <button onclick="kaydet()" class="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-black text-lg shadow-lg transition-all active:scale-95">
                VERİTABANINA GÖNDER
            </button>
        </div>

        <div class="bg-white rounded-[2.5rem] shadow-sm border border-slate-100 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 text-slate-400 text-[10px] font-black uppercase">
                    <tr><th class="px-10 py-6">Detay</th><th class="px-10 py-6">Kategori</th><th class="px-10 py-6">Stok</th><th class="px-10 py-6 text-right">İşlem</th></tr>
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
                const list = document.getElementById('list');
                let val = 0; let crit = 0;
                document.getElementById('total-count').innerText = data.length;
                list.innerHTML = data.map(i => {
                    const isCrit = i.stock <= (i.critical_limit || 10);
                    if(isCrit) crit++;
                    val += (i.stock * (i.price || 0));
                    return `<tr class="${isCrit ? 'bg-red-50' : ''}">
                        <td class="px-10 py-6 font-bold text-slate-700">${i.name}</td>
                        <td class="px-10 py-6 text-xs font-black text-blue-500 uppercase">${i.category}</td>
                        <td class="px-10 py-6 font-black">${i.stock} ${isCrit ? '⚠️' : ''}</td>
                        <td class="px-10 py-6 text-right"><button onclick="sil('${i._id}')" class="text-red-300 hover:text-red-600 px-4"><i class="fas fa-trash"></i></button></td>
                    </tr>`;
                }).join('');
                document.getElementById('crit-count').innerText = crit;
                document.getElementById('total-val').innerText = '₺' + val.toLocaleString();
            } catch(e) { console.error("Veri yuklenemedi"); }
        }

        async function kaydet() {
            const d = {
                name: document.getElementById('n').value,
                category: document.getElementById('c').value,
                stock: parseInt(document.getElementById('s').value || 0),
                price: parseFloat(document.getElementById('p').value || 0),
                critical_limit: parseInt(document.getElementById('l').value || 10)
            };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(d) });
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

@app.route('/api/products/<id>', methods=['DELETE'])
def del_p(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
