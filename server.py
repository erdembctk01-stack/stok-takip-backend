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
    <title>Özcan Oto | Ön Muhasebe & Stok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .sidebar-link:hover { background-color: #334155; }
        .active-section { display: block !important; }
        .sidebar-active { background-color: #2563eb !important; color: white !important; }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-900">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900">
        <div class="bg-white p-10 rounded-3xl shadow-2xl w-full max-w-md border-t-8 border-blue-600">
            <div class="text-center mb-8">
                <h1 class="text-2xl font-bold text-slate-800 uppercase tracking-tighter">Özcan Oto Muhasebe</h1>
                <p class="text-slate-400 text-sm mt-1">Giriş Bilgilerinizi Yazın</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold">
                <button onclick="handleLogin()" class="w-full bg-blue-600 text-white font-bold py-4 rounded-2xl shadow-lg transition-all active:scale-95">PANELİ AÇ</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <div class="w-64 bg-slate-800 text-white flex-shrink-0 flex flex-col border-r border-slate-700">
            <div class="p-6">
                <h2 class="text-xl font-black italic text-blue-400">ÖZCAN OTO</h2>
            </div>
            <nav class="flex-1 px-4 space-y-2">
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link sidebar-active w-full flex items-center gap-3 p-3 rounded-xl font-bold transition-all text-left">
                    <i class="fas fa-boxes w-6"></i> Stok Yönetimi
                </button>
                <button onclick="showPage('fatura')" id="btn-fatura" class="sidebar-link w-full flex items-center gap-3 p-3 rounded-xl font-bold text-slate-300 transition-all text-left">
                    <i class="fas fa-file-invoice-dollar w-6"></i> Faturalar
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-3 p-3 rounded-xl font-bold text-slate-300 transition-all text-left">
                    <i class="fas fa-minus-circle w-6"></i> Gider Takibi
                </button>
                <div class="pt-6 border-t border-slate-700 mt-6">
                    <button onclick="sendDailyReport()" class="w-full flex items-center gap-3 p-3 text-emerald-400 font-bold text-left">
                        <i class="fas fa-envelope-open-text w-6"></i> Gün Sonu Yedek
                    </button>
                    <button onclick="handleLogout()" class="w-full flex items-center gap-3 p-3 text-red-400 font-bold text-left">
                        <i class="fas fa-power-off w-6"></i> Çıkış Yap
                    </button>
                </div>
            </nav>
        </div>

        <main class="flex-1 p-8 overflow-y-auto">
            
            <div id="page-stok" class="page-content hidden active-section">
                <h3 class="text-2xl font-bold mb-6">Stok Envanteri</h3>
                <div class="bg-white p-6 rounded-3xl shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
                    <input id="in-code" type="text" placeholder="Kod" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                    <input id="in-name" type="text" placeholder="Parça Adı" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                    <input id="in-price" type="number" placeholder="Fiyat" class="p-4 bg-slate-50 rounded-xl outline-none font-bold border">
                    <button onclick="hizliEkle()" class="bg-blue-600 text-white font-bold rounded-xl">Ekle</button>
                </div>
                <div class="bg-white rounded-3xl shadow-sm border overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 text-[10px] font-black uppercase">
                            <tr><th class="px-8 py-4">Parça</th><th class="px-8 py-4 text-center">Stok</th><th class="px-8 py-4 text-right">Sil</th></tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-fatura" class="page-content hidden">
                <h3 class="text-2xl font-bold mb-6">Satış Faturaları</h3>
                <div class="bg-white p-6 rounded-3xl shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
                    <input id="fat-musteri" type="text" placeholder="Müşteri Adı" class="p-4 bg-slate-50 rounded-xl border font-bold">
                    <input id="fat-tutar" type="number" placeholder="Tutar (₺)" class="p-4 bg-slate-50 rounded-xl border font-bold">
                    <input id="fat-not" type="text" placeholder="Açıklama" class="p-4 bg-slate-50 rounded-xl border font-bold">
                    <button onclick="faturaEkle()" class="bg-emerald-600 text-white font-bold rounded-xl">Fatura Kes</button>
                </div>
                <div id="fatura-list" class="space-y-3"></div>
            </div>

            <div id="page-gider" class="page-content hidden">
                <h3 class="text-2xl font-bold mb-6">İşletme Giderleri</h3>
                <div class="bg-white p-6 rounded-3xl shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
                    <input id="gid-ad" type="text" placeholder="Gider Adı (Kira vb.)" class="p-4 bg-slate-50 rounded-xl border font-bold">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="p-4 bg-slate-50 rounded-xl border font-bold">
                    <button onclick="giderEkle()" class="md:col-span-2 bg-red-500 text-white font-bold rounded-xl">Gider Kaydet</button>
                </div>
                <div id="gider-list" class="space-y-3"></div>
            </div>

        </main>
    </div>

    <script>
        // SAYFA YÖNETİMİ
        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'stok') yukleStok();
            if(pageId === 'fatura') yukleFatura();
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

        // STOK İŞLEMLERİ
        async function yukleStok() {
            const res = await fetch('/api/products');
            const data = await res.json();
            document.getElementById('stok-list').innerHTML = data.map(i => `
                <tr>
                    <td class="px-8 py-4"><span class="text-emerald-600 font-bold block text-xs">₺${i.price}</span><b>${i.name}</b><br><small>${i.code}</small></td>
                    <td class="px-8 py-4 text-center">
                        <button onclick="stokGuncelle('${i._id}',-1,${i.stock})" class="bg-slate-100 px-2 rounded">-</button>
                        <span class="mx-3 font-bold">${i.stock}</span>
                        <button onclick="stokGuncelle('${i._id}',1,${i.stock})" class="bg-slate-100 px-2 rounded">+</button>
                    </td>
                    <td class="px-8 py-4 text-right"><button onclick="sil('${i._id}','products')" class="text-red-400"><i class="fas fa-trash"></i></button></td>
                </tr>
            `).join('');
        }

        // FATURA VE GİDER İŞLEMLERİ (Özetlenmiş)
        async function hizliEkle() {
            const p = { code: document.getElementById('in-code').value, name: document.getElementById('in-name').value, price: parseFloat(document.getElementById('in-price').value), stock: 0 };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            yukleStok();
        }

        async function faturaEkle() {
            const f = { musteri: document.getElementById('fat-musteri').value, tutar: parseFloat(document.getElementById('fat-tutar').value), not: document.getElementById('fat-not').value };
            await fetch('/api/invoices', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(f) });
            yukleFatura();
        }

        async function yukleFatura() {
            const res = await fetch('/api/invoices');
            const data = await res.json();
            document.getElementById('fatura-list').innerHTML = data.map(i => `
                <div class="bg-white p-4 rounded-2xl border border-l-8 border-l-emerald-500 flex justify-between items-center shadow-sm">
                    <div><b class="text-lg">${i.musteri}</b><p class="text-xs text-slate-400">${i.not}</p></div>
                    <div class="text-right font-black text-emerald-600">₺${i.tutar.toLocaleString()}</div>
                </div>
            `).join('');
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
                <div class="bg-white p-4 rounded-2xl border border-l-8 border-l-red-500 flex justify-between items-center shadow-sm">
                    <b class="text-lg">${i.ad}</b>
                    <div class="text-right font-black text-red-500">₺${i.tutar.toLocaleString()}</div>
                </div>
            `).join('');
        }

        async function stokGuncelle(id, change, current) {
            if(change === -1 && current <= 0) return;
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Silinsin mi?')) { await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); yukleStok(); }
        }

        function sendDailyReport() {
            alert("Rapor Hazırlanıyor... Mail uygulamasına yönlendiriliyorsunuz.");
            window.location.href = "mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Gun Sonu&body=Stoklar ve Muhasebe Kayitlari Ektedir.";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PANEL)

# --- GENEL API YAPISI ---
def get_col(name): return db[name]

@app.route('/api/<collection>', methods=['GET', 'POST'])
def handle_api(collection):
    col = get_col(collection)
    if request.method == 'GET':
        items = list(col.find())
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    col.insert_one(request.json)
    return jsonify({"ok": True})

@app.route('/api/<collection>/<id>', methods=['DELETE'])
def handle_delete(collection, id):
    get_col(collection).delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

@app.route('/api/products/<id>/stock', methods=['PUT'])
def update_stock(id):
    change = request.json.get('change', 0)
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
