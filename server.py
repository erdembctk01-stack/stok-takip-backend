from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- PANEL TASARIMI (ULTRA PRO TURUNCU) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO ULTIMATE | Pro Yönetim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .sidebar-link { transition: all 0.2s; color: #cbd5e1; }
        .sidebar-link:hover { background-color: #f97316; color: white; }
        .sidebar-active { background-color: #f97316 !important; color: white !important; border-radius: 1rem; }
        .page-content { display: none; }
        .active-section { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .orange-card { border-left: 8px solid #f97316; }
        .custom-scroll::-webkit-scrollbar { width: 5px; }
        .custom-scroll::-webkit-scrollbar-track { background: #f1f1f1; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #f97316; border-radius: 10px; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <div id="qr-modal" class="hidden fixed inset-0 z-[300] bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm">
        <div class="bg-white p-10 rounded-[3rem] text-center max-w-xs w-full">
            <h3 id="qr-title" class="font-black mb-6 uppercase italic"></h3>
            <div id="qrcode" class="flex justify-center mb-6"></div>
            <button onclick="closeQR()" class="w-full py-4 bg-orange-500 text-white font-black rounded-2xl">KAPAT</button>
        </div>
    </div>

    <div id="login-section" class="fixed inset-0 z-[250] flex items-center justify-center bg-slate-950">
        <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-md border-b-[15px] border-orange-500 text-center">
             <i class="fas fa-tools text-6xl text-orange-500 mb-6"></i>
             <h1 class="text-3xl font-black text-slate-800 italic uppercase">ÖZCAN OTO PRO</h1>
             <div class="mt-8 space-y-4 text-left">
                <input id="log-user" type="text" placeholder="Kullanıcı" class="w-full p-5 bg-slate-50 border-2 rounded-2xl font-bold focus:border-orange-500 outline-none">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 rounded-2xl font-bold focus:border-orange-500 outline-none">
                <button onclick="handleLogin()" class="w-full bg-orange-500 py-5 text-white font-black rounded-2xl shadow-xl hover:bg-orange-600 transition-all">SİSTEMİ AÇ</button>
             </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen overflow-hidden">
        <aside class="w-72 bg-slate-900 text-white flex-shrink-0 flex flex-col shadow-2xl z-50">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-2xl font-black italic text-orange-500 tracking-tighter">ÖZCAN OTO</h2>
                <p class="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em] mt-1">Ultimate v5.0 Admin</p>
            </div>
            <nav class="flex-1 px-4 py-8 space-y-2 overflow-y-auto custom-scroll">
                <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left"><i class="fas fa-th-large"></i> Dashboard</button>
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left"><i class="fas fa-boxes"></i> Envanter (Stok)</button>
                <button onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left"><i class="fas fa-address-book"></i> Veresiye & Cari</button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left"><i class="fas fa-file-invoice-dollar"></i> Gider Takibi</button>
                <div class="pt-10">
                    <button onclick="openFinanceModal()" class="w-full flex items-center gap-4 p-4 rounded-xl font-black text-orange-500 bg-orange-500/10 hover:bg-orange-500 hover:text-white transition-all text-left">
                        <i class="fas fa-chart-pie"></i> FİNANSAL RAPOR
                    </button>
                </div>
            </nav>
            <div class="p-6 bg-slate-950">
                <button onclick="handleLogout()" class="w-full p-3 text-red-400 font-bold border border-red-900/30 rounded-xl hover:bg-red-500 hover:text-white transition-all">ÇIKIŞ YAP</button>
            </div>
        </aside>

        <main class="flex-1 p-8 overflow-y-auto custom-scroll">
            
            <div id="page-dashboard" class="page-content active-section">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic">Genel Durum</h3>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-orange-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Toplam Parça</p>
                        <h4 id="dash-count" class="text-4xl font-black text-slate-800">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-red-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Kritik Stok</p>
                        <h4 id="dash-crit" class="text-4xl font-black text-red-600">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-emerald-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Toplam Cari</p>
                        <h4 id="dash-cari" class="text-4xl font-black text-slate-800">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-blue-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Veresiye Toplamı</p>
                        <h4 id="dash-borc" class="text-4xl font-black text-blue-600">₺0</h4>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-end mb-10">
                    <h3 class="text-3xl font-black text-slate-800">Parça Havuzu</h3>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Hızlı ara..." class="p-4 bg-white rounded-2xl border-2 border-slate-100 outline-none focus:border-orange-500 w-80 font-bold shadow-sm">
                </div>
                <div class="bg-white p-8 rounded-[3rem] shadow-sm border border-slate-100 mb-10 grid grid-cols-1 md:grid-cols-5 gap-4">
                    <input id="in-code" type="text" placeholder="KOD" class="p-4 bg-slate-50 rounded-2xl font-bold focus:ring-2 ring-orange-500 outline-none">
                    <input id="in-name" type="text" placeholder="İSİM" class="p-4 bg-slate-50 rounded-2xl font-bold focus:ring-2 ring-orange-500 outline-none">
                    <select id="in-cat" class="p-4 bg-slate-50 rounded-2xl font-bold focus:ring-2 ring-orange-500 outline-none">
                        <option>Motor</option><option>Fren</option><option>Yağlar</option><option>Elektrik</option><option>Kaporta</option>
                    </select>
                    <input id="in-price" type="number" placeholder="FİYAT" class="p-4 bg-slate-50 rounded-2xl font-bold focus:ring-2 ring-orange-500 outline-none">
                    <button onclick="hizliEkle()" class="bg-orange-500 text-white font-black rounded-2xl hover:bg-orange-600 transition-all uppercase">EKLE</button>
                </div>
                <div class="bg-white rounded-[3rem] shadow-xl border border-slate-100 overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 text-slate-400 text-[10px] font-black uppercase tracking-widest">
                            <tr>
                                <th class="px-8 py-6">Parça Bilgisi</th>
                                <th class="px-8 py-6 text-center">Stok</th>
                                <th class="px-8 py-6 text-right">Birim Fiyat</th>
                                <th class="px-8 py-6 text-right">İşlem</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic">Veresiye Defteri</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border mb-10 flex gap-4">
                    <input id="cari-ad" type="text" placeholder="Müşteri Adı" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold outline-none border-2 border-slate-100 focus:border-orange-500">
                    <input id="cari-tel" type="text" placeholder="Telefon" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold outline-none border-2 border-slate-100 focus:border-orange-500">
                    <button onclick="cariEkle()" class="px-10 bg-slate-900 text-white font-black rounded-2xl uppercase">Kayıt Aç</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic">Harcamalar</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border mb-10 flex gap-4">
                    <input id="gid-ad" type="text" placeholder="Açıklama" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-100 focus:border-red-500 outline-none">
                    <input id="gid-tutar" type="number" placeholder="Tutar" class="w-48 p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-100 focus:border-red-500 outline-none">
                    <button onclick="giderEkle()" class="px-10 bg-red-500 text-white font-black rounded-2xl uppercase">İşle</button>
                </div>
                <div id="gider-list" class="space-y-4"></div>
            </div>

        </main>
    </div>

    <div id="finance-modal" class="hidden fixed inset-0 z-[200] bg-slate-900/90 flex items-center justify-center p-6 backdrop-blur-md">
        <div class="bg-white w-full max-w-lg rounded-[4rem] shadow-2xl overflow-hidden">
            <div class="bg-orange-500 p-12 text-white text-center">
                <h2 class="text-3xl font-black uppercase italic italic">Dükkan Hesabı</h2>
            </div>
            <div class="p-12 space-y-4">
                <div class="flex justify-between p-6 bg-slate-50 rounded-3xl"><b>Stok Değeri:</b> <span id="fin-stok" class="font-black text-emerald-600">₺0</span></div>
                <div class="flex justify-between p-6 bg-slate-50 rounded-3xl"><b>Toplam Gider:</b> <span id="fin-gider" class="font-black text-red-500">₺0</span></div>
                <div class="flex justify-between p-6 bg-slate-900 text-white rounded-3xl"><b>Net Varlık:</b> <span id="fin-net" class="font-black text-orange-400">₺0</span></div>
                <button onclick="exportExcel()" class="w-full py-5 bg-emerald-600 text-white font-black rounded-2xl mt-4">EXCEL RAPORU İNDİR (.CSV)</button>
                <button onclick="closeFinanceModal()" class="w-full py-5 bg-slate-200 text-slate-800 font-black rounded-2xl">KAPAT</button>
            </div>
        </div>
    </div>

    <script>
        let products = []; let customers = []; let expenses = [];

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'stok') yukleStok();
            if(pageId === 'cari') yukleCari();
            if(pageId === 'gider') yukleGider();
            if(pageId === 'dashboard') yukleDash();
        }

        async function yukleStok() {
            const res = await fetch('/api/products');
            products = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            document.getElementById('stok-list').innerHTML = products.filter(i => (i.name+i.code).toLowerCase().includes(q)).map(i => `
                <tr class="hover:bg-orange-50/50 transition-all group">
                    <td class="px-8 py-6">
                        <div class="font-black text-slate-800 uppercase">${i.name}</div>
                        <div class="flex gap-2 text-[10px] font-bold text-orange-500 uppercase"><span>${i.code}</span> | <span class="text-slate-400">${i.category}</span></div>
                    </td>
                    <td class="px-8 py-6 text-center">
                        <div class="flex items-center justify-center gap-2">
                            <button onclick="stokGuncelle('${i._id}',-1)" class="w-8 h-8 bg-slate-100 rounded-lg font-bold">-</button>
                            <span class="font-black text-xl w-10 text-center ${i.stock <= 0 ? 'text-red-500' : ''}">${i.stock}</span>
                            <button onclick="stokGuncelle('${i._id}',1)" class="w-8 h-8 bg-slate-100 rounded-lg font-bold">+</button>
                        </div>
                    </td>
                    <td class="px-8 py-6 text-right font-black">₺${i.price.toLocaleString()}</td>
                    <td class="px-8 py-6 text-right space-x-2">
                        <button onclick="showQR('${i.code}','${i.name}')" class="text-slate-300 hover:text-blue-500"><i class="fas fa-qrcode"></i></button>
                        <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>`).join('');
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            customers = await res.json();
            document.getElementById('cari-list').innerHTML = customers.map(i => `
                <div class="bg-white p-8 rounded-[2.5rem] border group transition-all hover:border-orange-500">
                    <div class="flex justify-between items-start mb-6">
                        <div><b class="text-xl uppercase block">${i.ad}</b><span class="text-slate-400 font-bold">${i.tel}</span></div>
                        <div class="text-right"><span class="text-[10px] font-black uppercase text-slate-400">Bakiye</span><div class="text-2xl font-black text-blue-600">₺${(i.borc || 0).toLocaleString()}</div></div>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <button onclick="borcGuncelle('${i._id}', 100)" class="bg-red-50 text-red-600 p-3 rounded-xl font-bold text-xs">+ Borç Ekle</button>
                        <button onclick="borcGuncelle('${i._id}', -100)" class="bg-emerald-50 text-emerald-600 p-3 rounded-xl font-bold text-xs">Ödeme Al</button>
                    </div>
                    <button onclick="sil('${i._id}','customers')" class="mt-4 text-[10px] font-black text-slate-300 hover:text-red-500 uppercase">Kaydı Kapat</button>
                </div>`).join('');
        }

        async function borcGuncelle(id, miktar) {
            let tutar = prompt("İşlem miktarını girin:", Math.abs(miktar));
            if(!tutar) return;
            let val = miktar > 0 ? parseFloat(tutar) : -parseFloat(tutar);
            await fetch(`/api/customers/${id}/borc`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change: val}) });
            yukleCari();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            expenses = await res.json();
            document.getElementById('gider-list').innerHTML = expenses.map(i => `
                <div class="bg-white p-6 rounded-[2rem] border-l-[10px] border-red-500 flex justify-between items-center shadow-sm">
                    <b class="uppercase">${i.ad}</b>
                    <div class="font-black text-red-500 text-2xl">₺${i.tutar.toLocaleString()}</div>
                </div>`).join('');
        }

        async function yukleDash() {
            const [pRes, gRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/customers')]);
            const p = await pRes.json(); const g = await gRes.json(); const c = await cRes.json();
            document.getElementById('dash-count').innerText = p.length;
            document.getElementById('dash-crit').innerText = p.filter(x => x.stock <= 5).length;
            document.getElementById('dash-cari').innerText = c.length;
            let totalBorc = c.reduce((acc, curr) => acc + (curr.borc || 0), 0);
            document.getElementById('dash-borc').innerText = '₺' + totalBorc.toLocaleString();
        }

        async function hizliEkle() {
            const p = { code: document.getElementById('in-code').value, name: document.getElementById('in-name').value, category: document.getElementById('in-cat').value, price: parseFloat(document.getElementById('in-price').value), stock: 0 };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            yukleStok();
        }

        async function cariEkle() {
            const c = { ad: document.getElementById('cari-ad').value, tel: document.getElementById('cari-tel').value, borc: 0 };
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(c) });
            yukleCari();
        }

        async function giderEkle() {
            const g = { ad: document.getElementById('gid-ad').value, tutar: parseFloat(document.getElementById('gid-tutar').value) };
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(g) });
            yukleGider();
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) { if(confirm('Silinsin mi?')) { await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); showPage(col === 'products' ? 'stok' : col === 'customers' ? 'cari' : 'gider'); } }

        function showQR(code, name) {
            document.getElementById('qr-modal').classList.remove('hidden');
            document.getElementById('qr-title').innerText = name;
            document.getElementById('qrcode').innerHTML = "";
            new QRCode(document.getElementById("qrcode"), { text: code, width: 150, height: 150 });
        }
        function closeQR() { document.getElementById('qr-modal').classList.add('hidden'); }

        function openFinanceModal() {
            document.getElementById('finance-modal').classList.remove('hidden');
            let tV = products.reduce((a, b) => a + (b.stock * b.price), 0);
            let tG = expenses.reduce((a, b) => a + b.tutar, 0);
            document.getElementById('fin-stok').innerText = '₺' + tV.toLocaleString();
            document.getElementById('fin-gider').innerText = '₺' + tG.toLocaleString();
            document.getElementById('fin-net').innerText = '₺' + (tV - tG).toLocaleString();
        }
        function closeFinanceModal() { document.getElementById('finance-modal').classList.add('hidden'); }

        function exportExcel() {
            let csv = "Parça Adı,Stok,Fiyat\n";
            products.forEach(p => { csv += `${p.name},${p.stock},${p.price}\n`; });
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('href', url);
            a.setAttribute('download', 'OzcanOto_Stok_Rapor.csv');
            a.click();
        }

        function handleLogin() { if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") { localStorage.setItem('pro_auth', '1'); document.getElementById('login-section').classList.add('hidden'); document.getElementById('main-section').classList.remove('hidden'); showPage('dashboard'); } }
        function handleLogout() { localStorage.clear(); location.reload(); }
        if(localStorage.getItem('pro_auth')) { document.getElementById('login-section').classList.add('hidden'); document.getElementById('main-section').classList.remove('hidden'); showPage('dashboard'); }
    </script>
</body>
</html>
"""

# --- BACKEND API ---
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
    change = request.json['change']
    product = db.products.find_one({"_id": ObjectId(id)})
    if change == -1 and product['stock'] <= 0: return jsonify({"ok": False})
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

@app.route('/api/customers/<id>/borc', methods=['PUT'])
def update_borc(id):
    change = request.json['change']
    db.customers.update_one({"_id": ObjectId(id)}, {"$inc": {"borc": change}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
