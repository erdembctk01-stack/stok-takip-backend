from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

# --- SİSTEM AYARLARI ---
app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- KULLANICI ARAYÜZÜ (HTML/JS) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO SERVİS | Profesyonel Yönetim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; overflow: hidden; }
        
        /* Sol Panel Güzelleştirme */
        .sidebar { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
        .sidebar-link { 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            color: #94a3b8; 
            border-radius: 1.25rem;
            margin-bottom: 0.5rem;
        }
        .sidebar-link:hover { 
            background: rgba(249, 115, 22, 0.1); 
            color: #fb923c; 
            transform: translateX(8px);
        }
        .sidebar-active { 
            background: #f97316 !important; 
            color: white !important; 
            box-shadow: 0 10px 20px -5px rgba(249, 115, 22, 0.5);
        }

        /* Çevrimiçi Işığı */
        .online-dot {
            width: 8px;
            height: 8px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #22c55e;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }

        .page-content { display: none; height: 100vh; overflow-y: auto; }
        .active-section { display: block; animation: slideUp 0.4s ease-out; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .custom-card { border-radius: 2.5rem; background: white; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .critical-row { background-color: #fff1f2 !important; border-left: 5px solid #ef4444 !important; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[300] flex items-center justify-center bg-[#0f172a]">
        <div class="bg-white p-12 rounded-[4rem] shadow-2xl w-full max-w-md border-b-[16px] border-orange-500">
            <div class="text-center mb-10">
                <div class="w-20 h-20 bg-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-orange-500/40 rotate-6">
                    <i class="fas fa-car-side text-4xl text-white"></i>
                </div>
                <h1 class="text-3xl font-black text-slate-800 tracking-tighter uppercase italic">ÖZCAN OTO PRO</h1>
                <p class="text-slate-400 font-bold uppercase text-[10px] tracking-[0.3em] mt-3">Yetkili Giriş Sistemi</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500">
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-5 rounded-2xl shadow-xl transition-all active:scale-95 uppercase tracking-widest">GİRİŞ</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex h-screen">
        
        <aside class="w-80 sidebar text-white flex-shrink-0 flex flex-col z-50">
            <div class="p-10">
                <div class="flex flex-col gap-1">
                    <h2 class="text-2xl font-black italic tracking-tighter leading-none">ÖZCAN OTO</h2>
                    <h2 class="text-3xl font-black italic tracking-tighter text-orange-500 leading-none">SERVİS</h2>
                </div>
                <div class="mt-6 py-2 px-4 bg-white/5 border border-white/10 rounded-2xl inline-flex items-center gap-3">
                    <span class="online-dot"></span>
                    <span class="text-[11px] font-black uppercase tracking-widest text-emerald-400">Sistem Çevrimiçi</span>
                </div>
            </div>

            <nav class="flex-1 px-6 space-y-2 mt-4">
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mb-4 tracking-widest">Menü</p>
                <div onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-5 font-bold">
                    <i class="fas fa-chart-pie"></i> Dashboard
                </div>
                <div onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-5 font-bold">
                    <i class="fas fa-layer-group"></i> Parça Yönetimi
                </div>
                <div onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-5 font-bold">
                    <i class="fas fa-address-book"></i> Cari Kayıtlar
                </div>
                <div onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-5 font-bold">
                    <i class="fas fa-wallet"></i> Gider Takibi
                </div>
            </nav>

            <div class="p-8">
                <button onclick="handleLogout()" class="w-full p-4 text-red-400 font-bold border border-red-500/20 rounded-2xl hover:bg-red-500 hover:text-white transition-all flex items-center justify-center gap-3">
                    <i class="fas fa-power-off text-sm"></i> OTURUMU KAPAT
                </button>
            </div>
        </aside>

        <main class="flex-1 relative overflow-hidden">
            
            <div id="page-dashboard" class="page-content active-section p-10 lg:p-16">
                <div class="mb-12">
                    <h3 class="text-4xl font-black text-slate-800 uppercase italic">Genel Durum</h3>
                    <p id="current-date" class="text-slate-400 font-bold mt-2 text-lg"></p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                    <div class="custom-card p-10 border-b-8 border-orange-500">
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Envanter</p>
                        <h4 id="dash-count" class="text-5xl font-black text-slate-800 mt-2">0</h4>
                    </div>
                    <div class="custom-card p-10 border-b-8 border-red-500">
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Kritik Limit</p>
                        <h4 id="dash-crit" class="text-5xl font-black text-red-600 mt-2">0</h4>
                    </div>
                    <div class="custom-card p-10 border-b-8 border-emerald-500">
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Müşteriler</p>
                        <h4 id="dash-cari" class="text-5xl font-black text-slate-800 mt-2">0</h4>
                    </div>
                </div>

                <div class="bg-slate-900 p-12 rounded-[3.5rem] shadow-2xl text-white">
                    <h4 class="text-2xl font-black mb-8 uppercase italic text-orange-500">Raporlama Merkezi</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <button onclick="exportStokListesi()" class="p-8 bg-white/10 border border-white/20 rounded-[2rem] font-black hover:bg-orange-500 transition-all flex items-center justify-center gap-5 text-lg">
                            <i class="fas fa-download text-3xl"></i> LİSTEYİ İNDİR (TEMİZ FORMAT)
                        </button>
                        <button onclick="sendGmailReport()" class="p-8 bg-white/10 border border-white/20 rounded-[2rem] font-black hover:bg-blue-600 transition-all flex items-center justify-center gap-5 text-lg">
                            <i class="fas fa-envelope text-3xl"></i> GMAIL'E GÖNDER
                        </button>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content p-10 lg:p-16">
                <div class="flex flex-col lg:flex-row justify-between items-center mb-12 gap-6">
                    <h3 class="text-4xl font-black text-slate-800 italic uppercase">Parça Yönetimi</h3>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Hızlı ara..." class="p-5 bg-white rounded-3xl border-2 border-slate-100 outline-none w-full lg:w-96 font-bold shadow-sm focus:border-orange-500 transition-all">
                </div>

                <div class="custom-card p-10 mb-10">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-5">
                        <input id="in-code" type="text" placeholder="Kod" class="p-5 bg-slate-50 rounded-2xl font-bold focus:ring-2 focus:ring-orange-500 outline-none">
                        <input id="in-name" type="text" placeholder="Parça Adı" class="p-5 bg-slate-50 rounded-2xl font-bold focus:ring-2 focus:ring-orange-500 outline-none">
                        <input id="in-cat" type="text" placeholder="Kategori" class="p-5 bg-slate-50 rounded-2xl font-bold focus:ring-2 focus:ring-orange-500 outline-none">
                        <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-5 bg-slate-50 rounded-2xl font-bold focus:ring-2 focus:ring-orange-500 outline-none">
                        <input id="in-stock" type="number" placeholder="Adet" class="p-5 bg-slate-50 rounded-2xl font-bold focus:ring-2 focus:ring-orange-500 outline-none">
                        <button onclick="hizliEkle()" class="lg:col-span-5 bg-orange-500 text-white font-black rounded-2xl py-6 hover:bg-orange-600 shadow-xl transition-all uppercase tracking-widest text-lg">LİSTEYE EKLE</button>
                    </div>
                </div>

                <div class="bg-white rounded-[3.5rem] shadow-xl border border-slate-100 overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-900 text-white uppercase text-[11px] font-black tracking-widest">
                            <tr>
                                <th class="px-10 py-8 italic">PARÇA / KOD</th>
                                <th class="px-10 py-8 text-center">STOK</th>
                                <th class="px-10 py-8 text-right">FİYAT</th>
                                <th class="px-10 py-8 text-right">SİL</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content p-10 lg:p-16">
                <h3 class="text-4xl font-black text-slate-800 mb-10 uppercase italic">Müşteri Rehberi</h3>
                <div class="custom-card p-12 mb-10 flex flex-col lg:flex-row gap-6">
                    <input id="cari-ad" type="text" placeholder="Müşteri/Firma Adı" class="flex-1 p-6 bg-slate-50 rounded-2xl font-bold outline-none focus:ring-2 focus:ring-orange-500">
                    <input id="cari-tel" type="text" placeholder="Telefon" class="flex-1 p-6 bg-slate-50 rounded-2xl font-bold outline-none focus:ring-2 focus:ring-orange-500">
                    <button onclick="cariEkle()" class="px-12 bg-slate-900 text-white font-black rounded-2xl hover:bg-black transition-all uppercase shadow-lg">KAYDET</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"></div>
            </div>

            <div id="page-gider" class="page-content p-10 lg:p-16">
                <h3 class="text-4xl font-black text-slate-800 mb-10 uppercase italic text-red-600">Harcama Kayıtları</h3>
                <div class="custom-card p-12 mb-10 flex flex-col lg:flex-row gap-6 border-l-8 border-red-500">
                    <input id="gid-ad" type="text" placeholder="Harcama Açıklaması" class="flex-1 p-6 bg-slate-50 rounded-2xl font-bold outline-none">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="w-full lg:w-72 p-6 bg-slate-50 rounded-2xl font-bold outline-none">
                    <button onclick="giderEkle()" class="px-12 bg-red-500 text-white font-black rounded-2xl hover:bg-red-600 transition-all uppercase shadow-lg shadow-red-100">GİDERİ İŞLE</button>
                </div>
                <div id="gider-list" class="space-y-6"></div>
            </div>

        </main>
    </div>

    <script>
        let products = []; let totalVal = 0;

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('pro_session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
            } else alert("Erişim Engellendi!");
        }
        function handleLogout() { localStorage.clear(); location.reload(); }

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'dashboard') yukleDashboard();
            if(pageId === 'stok') yukleStok();
            if(pageId === 'cari') yukleCari();
            if(pageId === 'gider') yukleGider();
        }

        // --- RAPORLAMA (KARAKTER HATASIZ) ---
        function exportStokListesi() {
            if(products.length === 0) return alert("Veri yok!");
            let r = `ÖZCAN OTO GÜNLÜK RAPOR - ${new Date().toLocaleDateString('tr-TR')}\n----------------------------------\n\n`;
            products.forEach(p => {
                r += `PARÇA: ${p.name.toUpperCase()}\nKOD: ${p.code}\nSTOK: ${p.stock} ADET\nFİYAT: ₺${p.price.toLocaleString('tr-TR')}\n----------------------------------\n`;
            });
            r += `\nTOPLAM DEPO DEĞERİ: ₺${totalVal.toLocaleString('tr-TR')}`;
            const b = new Blob([r], { type: 'text/plain;charset=utf-8' });
            const u = window.URL.createObjectURL(b);
            const a = document.createElement('a'); a.href = u; a.download = `OzcanOto_Rapor.txt`; a.click();
        }

        function sendGmailReport() {
            let body = `ÖZCAN OTO RAPOR - ${new Date().toLocaleDateString('tr-TR')}\n\n`;
            products.forEach(p => body += `PARÇA: ${p.name.toUpperCase()}\nKOD: ${p.code}\nSTOK: ${p.stock} ADET\nFİYAT: ₺${p.price.toLocaleString('tr-TR')}\n--------------------------\n`);
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Rapor&body=${encodeURIComponent(body)}`;
        }

        // --- VERİ TABANI İŞLEMLERİ ---
        async function yukleStok() {
            const res = await fetch('/api/products'); products = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            let tV = 0;
            document.getElementById('stok-list').innerHTML = products
                .filter(i => (i.name + i.code).toLowerCase().includes(q)).reverse()
                .map(i => {
                    tV += (i.stock * i.price); const isCrit = i.stock <= 2;
                    return `<tr class="${isCrit ? 'critical-row' : ''} transition-all">
                        <td class="px-10 py-8"><b class="text-xl text-slate-800 block uppercase">${i.name}</b><span class="text-xs font-black text-orange-500 uppercase">${i.code}</span></td>
                        <td class="px-10 py-8 text-center font-black text-2xl">${i.stock}</td>
                        <td class="px-10 py-8 text-right font-black text-slate-700 text-xl italic">₺${i.price.toLocaleString('tr-TR')}</td>
                        <td class="px-10 py-8 text-right"><button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash-alt text-xl"></i></button></td>
                    </tr>`;
                }).join('');
            totalVal = tV;
        }

        async function yukleDashboard() {
            const [pRes, gRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/customers')]);
            const p = await pRes.json(); const g = await gRes.json(); const c = await cRes.json();
            products = p;
            document.getElementById('dash-count').innerText = p.length;
            document.getElementById('dash-crit').innerText = p.filter(x => x.stock <= 2).length;
            document.getElementById('dash-cari').innerText = c.length;
            document.getElementById('current-date').innerText = new Date().toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            totalVal = 0; p.forEach(i => totalVal += (i.stock * i.price));
        }

        async function hizliEkle() {
            const n = document.getElementById('in-name').value; if(!n) return alert("İsim gir!");
            const obj = { code: document.getElementById('in-code').value || 'KODSUZ', name: n, category: document.getElementById('in-cat').value || 'GENEL', price: parseFloat(document.getElementById('in-price').value || 0), stock: parseInt(document.getElementById('in-stock').value || 1) };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(obj) });
            ['in-name', 'in-code', 'in-price', 'in-cat', 'in-stock'].forEach(id => document.getElementById(id).value = '');
            yukleStok();
        }

        async function cariEkle() {
            const ad = document.getElementById('cari-ad').value; if(!ad) return alert("İsim gir!");
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ad, tel: document.getElementById('cari-tel').value, tarih: new Date().toLocaleDateString('tr-TR')}) });
            document.getElementById('cari-ad').value = ''; document.getElementById('cari-tel').value = ''; yukleCari();
        }

        async function yukleCari() {
            const r = await fetch('/api/customers'); const d = await r.json();
            document.getElementById('cari-list').innerHTML = d.map(i => `
                <div class="custom-card p-10 flex items-center justify-between group hover:border-orange-500 transition-all">
                    <div><b class="text-xl font-black block uppercase text-slate-800">${i.ad}</b><span class="text-slate-400 font-bold tracking-widest">${i.tel || '-'}</span></div>
                    <button onclick="sil('${i._id}','customers')" class="text-red-400 opacity-0 group-hover:opacity-100"><i class="fas fa-trash-alt"></i></button>
                </div>`).join('');
        }

        async function giderEkle() {
            const ad = document.getElementById('gid-ad').value; const t = parseFloat(document.getElementById('gid-tutar').value);
            if(!ad || !t) return alert("Eksik!");
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ad, tutar: t, tarih: new Date().toLocaleDateString('tr-TR')}) });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = ''; yukleGider();
        }

        async function yukleGider() {
            const r = await fetch('/api/expenses'); const d = await r.json();
            document.getElementById('gider-list').innerHTML = d.map(i => `
                <div class="custom-card p-10 flex justify-between items-center border-l-8 border-red-500">
                    <div><b class="text-2xl font-black block uppercase">${i.ad}</b><span class="text-xs text-slate-400 font-bold">${i.tarih}</span></div>
                    <div class="flex items-center gap-8"><b class="text-3xl text-red-500 italic font-black">₺${i.tutar.toLocaleString('tr-TR')}</b>
                    <button onclick="sil('${i._id}','expenses')" class="text-slate-200 hover:text-red-500"><i class="fas fa-trash-alt"></i></button></div>
                </div>`).join('');
        }

        async function sil(id, col) { if(confirm('Silinsin mi usta?')) { await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); showPage(col === 'products' ? 'stok' : col === 'customers' ? 'cari' : 'gider'); } }

        window.onload = () => { if(localStorage.getItem('pro_session')) { document.getElementById('login-section').classList.add('hidden'); document.getElementById('main-section').classList.remove('hidden'); showPage('dashboard'); } };
    </script>
</body>
</html>
"""

# --- BACKEND ---
@app.route('/')
def index(): return render_template_string(HTML_PANEL)

@app.route('/api/<col>', methods=['GET', 'POST'])
def handle_api(col):
    if request.method == 'GET':
        items = list(db[col].find()); [i.update({'_id': str(i['_id'])}) for i in items]
        return jsonify(items)
    db[col].insert_one(request.json); return jsonify({"ok": True})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    db[col].delete_one({"_id": ObjectId(id)}); return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
