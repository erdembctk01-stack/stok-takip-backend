from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- PANEL TASARIMI ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO | Stok Takip</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .sidebar-link:hover { background-color: #334155; }
        .sidebar-active { background-color: #2563eb !important; color: white !important; }
        .page-content { display: none; }
        .active-section { display: block; }
    </style>
</head>
<body class="bg-slate-100 font-sans min-h-screen">

    <div id="login-section" class="flex items-center justify-center min-h-screen">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl w-full max-w-md border-4 border-blue-600">
            <div class="text-center mb-8">
                <i class="fas fa-user-shield text-5xl text-blue-600 mb-4"></i>
                <h1 class="text-3xl font-black text-slate-800 italic uppercase">ÖZCAN OTO</h1>
                <p class="text-slate-400 font-bold uppercase text-xs tracking-widest mt-2">Yönetim Girişi</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold focus:border-blue-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold focus:border-blue-500">
                <button onclick="handleLogin()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-2xl transition-all shadow-lg active:scale-95 text-lg">SİSTEME GİR</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <div class="w-64 bg-slate-800 text-white flex-shrink-0 flex flex-col border-r border-slate-700">
            <div class="p-6">
                <h2 class="text-xl font-black italic text-blue-400 uppercase">ÖZCAN OTO</h2>
            </div>
            <nav class="flex-1 px-4 space-y-2">
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link sidebar-active w-full flex items-center gap-3 p-3 rounded-xl font-bold transition-all text-left">
                    <i class="fas fa-boxes w-6"></i> Parça Listesi
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-3 p-3 rounded-xl font-bold text-slate-300 transition-all text-left">
                    <i class="fas fa-receipt w-6"></i> Giderler / Fatura
                </button>
                <div class="pt-6 border-t border-slate-700 mt-6">
                    <button onclick="sendDailyReport()" class="w-full flex items-center gap-3 p-3 text-emerald-400 font-bold text-left">
                        <i class="fas fa-envelope-open-text w-6"></i> GÜN SONU YEDEK
                    </button>
                    <button onclick="handleLogout()" class="w-full flex items-center gap-3 p-3 text-red-400 font-bold text-left">
                        <i class="fas fa-power-off w-6"></i> ÇIKIŞ YAP
                    </button>
                </div>
            </nav>
        </div>

        <main class="flex-1 p-8 overflow-y-auto">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="bg-white p-6 rounded-3xl shadow-sm border-b-4 border-emerald-500">
                    <p class="text-xs font-black text-slate-400 uppercase">Toplam Depo Değeri</p>
                    <h2 id="total-val" class="text-4xl font-black text-slate-800 tracking-tighter">₺0</h2>
                </div>
                <div class="bg-white p-6 rounded-3xl shadow-sm border-b-4 border-red-500">
                    <p class="text-xs font-black text-slate-400 uppercase">Kritik Stok Uyarısı</p>
                    <h2 id="stat-crit-count" class="text-4xl font-black text-red-500 tracking-tighter">0</h2>
                </div>
            </div>

            <div id="page-stok" class="page-content active-section">
                <div class="bg-white p-6 rounded-3xl shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-4 gap-3">
                    <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                    <input id="in-name" type="text" placeholder="Parça İsmi" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                    <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                    <button onclick="hizliEkle()" class="bg-blue-600 text-white font-black rounded-xl hover:bg-blue-700 transition-all">EKLE</button>
                </div>

                <div class="bg-white rounded-[2rem] shadow-sm border overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase">
                            <tr><th class="px-8 py-6">Parça Detayı</th><th class="px-8 py-6 text-center">Stok</th><th class="px-8 py-6 text-right">Sil</th></tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-gider" class="page-content">
                <div class="bg-white p-6 rounded-3xl shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input id="gid-ad" type="text" placeholder="Gider/Fatura Adı" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black rounded-xl">KAYDET</button>
                </div>
                <div id="gider-list" class="space-y-3"></div>
            </div>

        </main>
    </div>

    <script>
        let currentProducts = [];
        let totalVal = 0;

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'stok') yukleStok();
            if(pageId === 'gider') yukleGider();
        }

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                yukleStok();
            } else { alert("Hatalı Giriş!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        async function yukleStok() {
            const res = await fetch('/api/products');
            currentProducts = await res.json();
            let tVal = 0; let critCount = 0;

            document.getElementById('stok-list').innerHTML = currentProducts.map(i => {
                const isCrit = i.stock <= 2;
                if(i.stock <= 10) critCount++;
                tVal += (i.stock * i.price);
                return `
                <tr class="${isCrit ? 'bg-red-50' : 'hover:bg-slate-50'}">
                    <td class="px-8 py-6">
                        <div class="text-[10px] font-black text-white bg-emerald-500 w-fit px-2 rounded mb-1 uppercase tracking-tighter">₺${i.price.toLocaleString()}</div>
                        <div class="font-black ${isCrit ? 'text-red-600 underline' : 'text-slate-800'} uppercase text-lg leading-tight">${i.name}</div>
                        <div class="text-[10px] text-slate-400 font-bold tracking-widest mt-1">${i.code}</div>
                    </td>
                    <td class="px-8 py-6 text-center">
                        <div class="flex items-center justify-center gap-2 bg-white border p-1 rounded-xl w-fit mx-auto shadow-sm">
                            <button onclick="stokGuncelle('${i._id}', -1, ${i.stock})" class="w-8 h-8 text-red-500 font-bold">-</button>
                            <span class="w-8 text-center font-black">${i.stock}</span>
                            <button onclick="stokGuncelle('${i._id}', 1, ${i.stock})" class="w-8 h-8 text-green-500 font-bold">+</button>
                        </div>
                    </td>
                    <td class="px-8 py-6 text-right">
                        <button onclick="sil('${i._id}','products')" class="text-red-400 hover:text-red-600"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>`;
            }).join('');
            totalVal = tVal;
            document.getElementById('total-val').innerText = '₺' + totalVal.toLocaleString();
            document.getElementById('stat-crit-count').innerText = critCount;
        }

        async function hizliEkle() {
            const p = { code: document.getElementById('in-code').value || 'KODSUZ', name: document.getElementById('in-name').value, price: parseFloat(document.getElementById('in-price').value || 0), stock: 0 };
            if(!p.name) return alert("Parça İsmi Şart!");
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            yukleStok();
        }

        async function giderEkle() {
            const g = { ad: document.getElementById('gid-ad').value, tutar: parseFloat(document.getElementById('gid-tutar').value) };
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(g) });
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            const data = await res.json();
            document.getElementById('gider-list').innerHTML = data.map(i => `
                <div class="bg-white p-4 rounded-2xl border-l-8 border-red-500 flex justify-between items-center shadow-sm">
                    <b class="uppercase">${i.ad}</b>
                    <div class="font-black text-red-500">₺${i.tutar.toLocaleString()}</div>
                </div>
            `).join('');
        }

        async function stokGuncelle(id, change, current) {
            if(change === -1 && current <= 0) return;
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Silsin mi usta?')) { await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); if(col==='products') yukleStok(); else yukleGider(); }
        }

        function sendDailyReport() {
            let body = "ÖZCAN OTO YEDEK\n\n";
            currentProducts.forEach(p => { body += `${p.name} | KOD: ${p.code} | STOK: ${p.stock} | FİYAT: ₺${p.price}\n`; });
            body += `\nTOPLAM DEPO: ₺${totalVal.toLocaleString()}`;
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Gun Sonu&body=${encodeURIComponent(body)}`;
        }

        if(localStorage.getItem('session')) {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
            yukleStok();
        }
    </script>
</body>
</html>
"""

# --- API ---
@app.route('/')
def index(): return render_template_string(HTML_PANEL)

@app.route('/api/<col>', methods=['GET', 'POST'])
def handle_api(col):
    if request.method == 'GET':
        items = list(db[col].find())
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    db[col].insert_one(request.json)
    return jsonify({"ok": True})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    db[col].delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

@app.route('/api/products/<id>/stock', methods=['PUT'])
def update_stock(id):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": request.json['change']}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
