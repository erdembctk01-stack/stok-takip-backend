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

# --- KULLANICI ARAYÜZÜ ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO SERVİS | Profesyonel ERP</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; overflow: hidden; background: #f8fafc; }
        
        /* Sol Panel */
        .sidebar { background: #0f172a; border-right: 1px solid rgba(255,255,255,0.05); }
        .sidebar-link { transition: 0.3s; color: #94a3b8; border-radius: 1rem; cursor: pointer; }
        .sidebar-link:hover { background: rgba(249, 115, 22, 0.1); color: #fb923c; }
        .sidebar-active { background: #f97316 !important; color: white !important; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4); }

        .online-dot { width: 10px; height: 10px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

        .page-content { display: none; height: 100vh; overflow-y: auto; padding: 40px; }
        .active-section { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .custom-card { border-radius: 2rem; background: white; border: 1px solid #e2e8f0; transition: 0.3s; }
        .custom-card:hover { border-color: #fb923c; }
        
        .fatura-badge { background: #fff7ed; color: #c2410c; padding: 4px 12px; border-radius: 8px; font-weight: 800; font-size: 11px; }
    </style>
</head>
<body class="selection:bg-orange-100">

    <div id="login-section" class="fixed inset-0 z-[500] flex items-center justify-center bg-[#0f172a]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md text-center border-b-[12px] border-orange-500">
            <h1 class="text-3xl font-black text-slate-800 italic uppercase">ÖZCAN OTO PRO</h1>
            <div class="space-y-4 mt-10">
                <input id="log-user" type="text" placeholder="Kullanıcı" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500 transition-all">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500 transition-all">
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-5 rounded-2xl transition-all shadow-lg shadow-orange-100 uppercase italic">Sistemi Başlat</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex h-screen">
        
        <aside class="w-80 sidebar text-white flex flex-col p-8">
            <div class="mb-10">
                <h2 class="text-2xl font-black italic">ÖZCAN OTO</h2>
                <h2 class="text-3xl font-black italic text-orange-500">SERVİS</h2>
                <div class="mt-4 flex items-center gap-3 bg-white/5 p-3 rounded-2xl">
                    <span class="online-dot"></span>
                    <span class="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-400">Sistem Çevrimiçi</span>
                </div>
            </div>

            <nav class="flex-1 space-y-2">
                <div onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active p-5 flex items-center gap-4 font-bold">
                    <i class="fas fa-home"></i> Panel
                </div>
                <div onclick="showPage('fatura')" id="btn-fatura" class="sidebar-link p-5 flex items-center gap-4 font-bold">
                    <i class="fas fa-file-invoice-dollar"></i> Fatura Kes (Paraşüt)
                </div>
                <div onclick="showPage('stok')" id="btn-stok" class="sidebar-link p-5 flex items-center gap-4 font-bold">
                    <i class="fas fa-boxes"></i> Stok Takibi
                </div>
                <div onclick="showPage('cari')" id="btn-cari" class="sidebar-link p-5 flex items-center gap-4 font-bold">
                    <i class="fas fa-user-friends"></i> Müşteri / Cari
                </div>
            </nav>

            <button onclick="handleLogout()" class="mt-auto p-4 text-red-400 font-bold border border-red-500/20 rounded-2xl hover:bg-red-500 hover:text-white transition-all">
                <i class="fas fa-power-off"></i> ÇIKIŞ
            </button>
        </aside>

        <main class="flex-1 overflow-hidden relative">

            <div id="page-dashboard" class="page-content active-section">
                <h3 class="text-4xl font-black text-slate-800 italic mb-10">Özet Veriler</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="custom-card p-10 border-b-8 border-orange-500">
                        <span class="text-xs font-black text-slate-400 uppercase tracking-widest">Kayıtlı Parça</span>
                        <h4 id="dash-count" class="text-5xl font-black text-slate-800 mt-2">0</h4>
                    </div>
                    <div class="custom-card p-10 border-b-8 border-blue-500">
                        <span class="text-xs font-black text-slate-400 uppercase tracking-widest">Kesilen Faturalar</span>
                        <h4 id="dash-inv" class="text-5xl font-black text-blue-600 mt-2">0</h4>
                    </div>
                    <div class="custom-card p-10 border-b-8 border-emerald-500">
                        <span class="text-xs font-black text-slate-400 uppercase tracking-widest">Toplam Değer</span>
                        <h4 id="dash-total" class="text-3xl font-black text-emerald-600 mt-2">₺0</h4>
                    </div>
                </div>
            </div>

            <div id="page-fatura" class="page-content">
                <h3 class="text-4xl font-black text-slate-800 italic mb-8">Hızlı Satış & Fatura</h3>
                <div class="custom-card p-10 mb-10 border-l-8 border-orange-500">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase">Müşteri Seç</label>
                            <select id="inv-customer" class="w-full p-4 bg-slate-50 border-2 rounded-2xl font-bold outline-none"></select>
                        </div>
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase">Parça Seç</label>
                            <select id="inv-product" class="w-full p-4 bg-slate-50 border-2 rounded-2xl font-bold outline-none"></select>
                        </div>
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase">Miktar</label>
                            <input id="inv-qty" type="number" value="1" class="w-full p-4 bg-slate-50 border-2 rounded-2xl font-bold outline-none">
                        </div>
                        <button onclick="faturaKes()" class="md:col-span-3 bg-orange-500 text-white font-black py-5 rounded-2xl hover:bg-orange-600 transition-all shadow-lg text-lg uppercase">Faturayı Kes ve Stoktan Düş</button>
                    </div>
                </div>
                
                <div class="bg-white rounded-[2.5rem] shadow-xl overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-900 text-white text-[11px] font-black uppercase tracking-widest">
                            <tr>
                                <th class="px-8 py-6">Fatura No</th>
                                <th class="px-8 py-6">Müşteri</th>
                                <th class="px-8 py-6">İçerik</th>
                                <th class="px-8 py-6">Tarih</th>
                                <th class="px-8 py-6 text-right">İşlem</th>
                            </tr>
                        </thead>
                        <tbody id="fatura-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-center mb-10">
                    <h3 class="text-4xl font-black text-slate-800 italic">Envanter Kontrolü</h3>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Hızlı ara..." class="p-5 bg-white rounded-3xl border-2 border-slate-100 outline-none w-96 font-bold shadow-sm">
                </div>
                <div class="custom-card p-8 mb-10">
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <input id="in-code" placeholder="Kod" class="p-4 bg-slate-50 border-2 rounded-xl outline-none font-bold">
                        <input id="in-name" placeholder="Parça Adı" class="p-4 bg-slate-50 border-2 rounded-xl outline-none font-bold">
                        <input id="in-cat" placeholder="Kategori" class="p-4 bg-slate-50 border-2 rounded-xl outline-none font-bold">
                        <input id="in-price" type="number" placeholder="Fiyat" class="p-4 bg-slate-50 border-2 rounded-xl outline-none font-bold">
                        <input id="in-stock" type="number" placeholder="Adet" class="p-4 bg-slate-50 border-2 rounded-xl outline-none font-bold">
                        <button onclick="hizliEkle()" class="md:col-span-5 bg-slate-900 text-white font-black py-4 rounded-xl hover:bg-black transition-all">YENİ PARÇA KAYDET</button>
                    </div>
                </div>
                <div class="bg-white rounded-[2.5rem] shadow-xl overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase tracking-widest">
                            <tr>
                                <th class="px-8 py-6">Parça / Kod</th>
                                <th class="px-8 py-6 text-center">Stok (Manuel Müdahale)</th>
                                <th class="px-8 py-6 text-right">Birim Fiyat</th>
                                <th class="px-8 py-6 text-right">Sil</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-4xl font-black text-slate-800 italic mb-10 uppercase">Cari Rehber</h3>
                <div class="custom-card p-10 flex gap-6 mb-10">
                    <input id="cari-ad" placeholder="Müşteri Adı" class="flex-1 p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold">
                    <input id="cari-tel" placeholder="Telefon" class="flex-1 p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold">
                    <button onclick="cariEkle()" class="px-10 bg-orange-500 text-white font-black rounded-2xl hover:bg-orange-600 transition-all">EKLE</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-3 gap-6"></div>
            </div>

        </main>
    </div>

    <script>
        let products = []; let customers = []; let invoices = []; let totalVal = 0;

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('pro_session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
            } else alert("Hatalı Giriş!");
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
            if(pageId === 'fatura') yukleFatura();
        }

        // --- STOK YÜKLEME VE MANUEL GÜNCELLEME ---
        async function yukleStok() {
            const res = await fetch('/api/products');
            products = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            let tV = 0;
            document.getElementById('stok-list').innerHTML = products
                .filter(i => (i.name + i.code).toLowerCase().includes(q)).reverse()
                .map(i => {
                    tV += (i.stock * i.price);
                    return `
                    <tr class="hover:bg-slate-50 transition-all">
                        <td class="px-8 py-6">
                            <b class="text-lg text-slate-800 uppercase block">${i.name}</b>
                            <span class="text-xs font-bold text-orange-500">${i.code}</span>
                        </td>
                        <td class="px-8 py-6">
                            <div class="flex items-center justify-center gap-4 bg-white border p-2 rounded-2xl w-fit mx-auto shadow-sm">
                                <button onclick="stokDegistir('${i._id}',-1)" class="w-10 h-10 text-red-500 font-black hover:bg-red-50 rounded-xl">-</button>
                                <span class="w-10 text-center font-black text-xl">${i.stock}</span>
                                <button onclick="stokDegistir('${i._id}',1)" class="w-10 h-10 text-emerald-500 font-black hover:bg-emerald-50 rounded-xl">+</button>
                            </div>
                        </td>
                        <td class="px-8 py-6 text-right font-black text-slate-700">₺${i.price.toLocaleString('tr-TR')}</td>
                        <td class="px-8 py-6 text-right">
                            <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    </tr>`;
                }).join('');
            totalVal = tV;
        }

        async function stokDegistir(id, change) {
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        // --- FATURA SİSTEMİ (PARAŞÜT MANTIĞI) ---
        async function yukleFatura() {
            // Seçenekleri Doldur
            const [pRes, cRes, iRes] = await Promise.all([fetch('/api/products'), fetch('/api/customers'), fetch('/api/invoices')]);
            const pData = await pRes.json(); const cData = await cRes.json(); const iData = await iRes.json();
            
            document.getElementById('inv-product').innerHTML = pData.map(i => `<option value="${i._id}">${i.name} (${i.stock} Adet)</option>`).join('');
            document.getElementById('inv-customer').innerHTML = cData.map(i => `<option value="${i.ad}">${i.ad}</option>`).join('');
            
            document.getElementById('fatura-list').innerHTML = iData.reverse().map(i => `
                <tr class="hover:bg-slate-50">
                    <td class="px-8 py-6 italic font-bold text-slate-400">#${i._id.slice(-6).toUpperCase()}</td>
                    <td class="px-8 py-6 font-black text-slate-800 uppercase">${i.customer}</td>
                    <td class="px-8 py-6"><span class="fatura-badge">${i.product_name} x ${i.qty}</span></td>
                    <td class="px-8 py-6 text-xs font-bold text-slate-400 uppercase">${i.date}</td>
                    <td class="px-8 py-6 text-right"><button onclick="sil('${i._id}','invoices')" class="text-red-400"><i class="fas fa-trash-alt"></i></button></td>
                </tr>
            `).join('');
        }

        async function faturaKes() {
            const pid = document.getElementById('inv-product').value;
            const qty = parseInt(document.getElementById('inv-qty').value);
            const customer = document.getElementById('inv-customer').value;
            
            if(!pid || qty <= 0) return alert("Hatalı miktar veya parça!");

            // 1. Stoktan Düş
            const updateRes = await fetch(`/api/products/${pid}/stock`, { 
                method: 'PUT', 
                headers: {'Content-Type':'application/json'}, 
                body: JSON.stringify({change: -qty}) 
            });
            const updateJson = await updateRes.json();
            
            if(!updateJson.ok) return alert("Yetersiz Stok!");

            // 2. Fatura Kaydı Oluştur
            const pObj = products.find(x => x._id === pid);
            await fetch('/api/invoices', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({
                    customer,
                    product_id: pid,
                    product_name: pObj.name,
                    qty: qty,
                    date: new Date().toLocaleString('tr-TR')
                })
            });

            alert("Fatura Kesildi ve Stok Düştü!");
            yukleFatura();
        }

        // --- DASHBOARD VE GENEL ---
        async function yukleDashboard() {
            const [p, c, i] = await Promise.all([fetch('/api/products'), fetch('/api/customers'), fetch('/api/invoices')]);
            const pD = await p.json(); const cD = await c.json(); const iD = await i.json();
            document.getElementById('dash-count').innerText = pD.length;
            document.getElementById('dash-inv').innerText = iD.length;
            let val = 0; pD.forEach(x => val += (x.stock * x.price));
            document.getElementById('dash-total').innerText = '₺' + val.toLocaleString('tr-TR');
        }

        async function hizliEkle() {
            const obj = {
                code: document.getElementById('in-code').value || 'KODSUZ',
                name: document.getElementById('in-name').value,
                category: document.getElementById('in-cat').value || 'GENEL',
                price: parseFloat(document.getElementById('in-price').value || 0),
                stock: parseInt(document.getElementById('in-stock').value || 1)
            };
            if(!obj.name) return alert("İsim şart!");
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(obj) });
            yukleStok();
        }

        async function cariEkle() {
            const ad = document.getElementById('cari-ad').value;
            if(!ad) return alert("Ad yaz!");
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ad, tel: document.getElementById('cari-tel').value}) });
            document.getElementById('cari-ad').value = ''; yukleCari();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers'); const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="custom-card p-10 flex justify-between items-center group">
                    <div><b class="text-xl uppercase block text-slate-800">${i.ad}</b><span class="text-slate-400 font-bold">${i.tel || '-'}</span></div>
                    <button onclick="sil('${i._id}','customers')" class="text-red-400 opacity-0 group-hover:opacity-100"><i class="fas fa-trash-alt"></i></button>
                </div>`).join('');
        }

        async function sil(id, col) {
            if(confirm('Silinsin mi?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                showPage(col === 'products' ? 'stok' : col === 'invoices' ? 'fatura' : 'cari');
            }
        }

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

@app.route('/api/products/<id>/stock', methods=['PUT'])
def update_stock(id):
    change = request.json['change']
    product = db.products.find_one({"_id": ObjectId(id)})
    if not product: return jsonify({"ok": False})
    if change < 0 and (product['stock'] + change) < 0:
        return jsonify({"ok": False, "msg": "Yetersiz Stok"})
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
