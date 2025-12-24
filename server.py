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

# --- PANEL TASARIMI ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO PRO | Kurumsal Kaynak Planlama</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
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
        .critical-row { background-color: #fee2e2 !important; border-left: 6px solid #ef4444; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[200] flex items-center justify-center bg-[#1e1b1e]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-b-[15px] border-orange-500">
            <div class="text-center mb-10">
                <div class="w-20 h-20 bg-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-orange-500/30">
                    <i class="fas fa-wrench text-4xl text-white"></i>
                </div>
                <h1 class="text-3xl font-black text-slate-800 tracking-tighter italic">ÖZCAN OTO PRO</h1>
                <p class="text-slate-400 font-bold uppercase text-[10px] tracking-[0.3em] mt-3">Kurumsal Yönetim</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500">
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-5 rounded-2xl shadow-xl transition-all active:scale-95">SİSTEME GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        <aside class="w-72 bg-slate-900 text-white flex-shrink-0 flex flex-col shadow-2xl z-50">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-2xl font-black italic text-orange-500 uppercase tracking-tighter">ÖZCAN OTO</h2>
            </div>
            <nav class="flex-1 px-4 py-8 space-y-2 overflow-y-auto">
                <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-th-large"></i> Dashboard
                </button>
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-boxes"></i> Parça Listesi
                </button>
                <button onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-users-cog"></i> Cari Rehber
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-file-invoice-dollar"></i> Gider Takibi
                </button>
                <button onclick="openFinanceModal()" class="w-full flex items-center gap-4 p-4 rounded-xl font-bold text-orange-500 bg-orange-500/10 hover:bg-orange-500 hover:text-white transition-all text-left">
                    <i class="fas fa-wallet"></i> TOPLAM DEPO DEĞERİ
                </button>
            </nav>
            <div class="p-6 bg-slate-950">
                <button onclick="handleLogout()" class="w-full flex items-center justify-center gap-3 p-3 text-red-400 font-bold border border-red-900/30 rounded-xl hover:bg-red-500 hover:text-white transition-all">
                    <i class="fas fa-power-off"></i> ÇIKIŞ
                </button>
            </div>
        </aside>

        <main class="flex-1 p-8 md:p-12 overflow-y-auto">
            <div id="page-dashboard" class="page-content active-section">
                <div class="mb-10">
                    <h3 class="text-3xl font-black text-slate-800 uppercase italic">İşletme Özeti</h3>
                    <p id="current-date" class="text-slate-400 font-bold"></p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-orange-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Toplam Parça</p>
                        <h4 id="dash-count" class="text-4xl font-black text-slate-800">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-red-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Kritik Stok (<=2)</p>
                        <h4 id="dash-crit" class="text-4xl font-black text-red-600">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-emerald-500">
                        <p class="text-xs font-black text-slate-400 uppercase">Kayıtlı Cari</p>
                        <h4 id="dash-cari" class="text-4xl font-black text-slate-800">0</h4>
                    </div>
                </div>

                <div class="bg-slate-900 p-10 rounded-[3rem] shadow-xl text-white">
                    <h4 class="text-lg font-black mb-6 uppercase tracking-tighter text-orange-500">Gün Sonu Raporlama</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button onclick="exportStokExcel()" class="p-6 bg-white/5 border border-white/10 rounded-3xl font-black hover:bg-emerald-600 transition-all flex items-center justify-center gap-4">
                            <i class="fas fa-file-excel text-2xl"></i> LİSTE OLARAK EXCEL AL
                        </button>
                        <button onclick="sendGmailReport()" class="p-6 bg-white/5 border border-white/10 rounded-3xl font-black hover:bg-orange-600 transition-all flex items-center justify-center gap-4">
                            <i class="fas fa-envelope text-2xl"></i> GMAIL RAPORU GÖNDER
                        </button>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex flex-col md:flex-row justify-between items-end mb-10 gap-4">
                    <h3 class="text-3xl font-black text-slate-800">Envanter</h3>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Ara..." class="p-4 bg-white rounded-2xl border-2 border-slate-100 outline-none w-full md:w-80 font-bold">
                </div>
                <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-10">
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <input id="in-code" type="text" placeholder="Kod" class="p-4 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-name" type="text" placeholder="Parça Adı" class="p-4 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-stock" type="number" placeholder="Stok (Boşsa 1)" class="p-4 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100 focus:ring-orange-500">
                        <button onclick="hizliEkle()" class="md:col-span-5 bg-orange-500 text-white font-black rounded-2xl py-4 hover:bg-orange-600 uppercase">Kaydet</button>
                    </div>
                </div>
                <div class="bg-white rounded-[3rem] shadow-xl overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase tracking-widest">
                            <tr>
                                <th class="px-8 py-7">Parça</th>
                                <th class="px-8 py-7">Kategori</th>
                                <th class="px-8 py-7 text-center">Stok</th>
                                <th class="px-8 py-7 text-right">Fiyat</th>
                                <th class="px-8 py-7 text-right">Sil</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic">Cari Rehber</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border mb-10 flex flex-col md:flex-row gap-6">
                    <input id="cari-ad" type="text" placeholder="İsim / Firma" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100">
                    <input id="cari-tel" type="text" placeholder="Telefon" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100">
                    <button onclick="cariEkle()" class="px-10 bg-slate-800 text-white font-black rounded-2xl hover:bg-black">KAYDET</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic">Giderler</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border mb-10 flex flex-col md:flex-row gap-6">
                    <input id="gid-ad" type="text" placeholder="Açıklama" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100">
                    <input id="gid-tutar" type="number" placeholder="Tutar" class="w-full md:w-64 p-5 bg-slate-50 rounded-2xl font-bold ring-2 ring-slate-100">
                    <button onclick="giderEkle()" class="px-10 bg-red-500 text-white font-black rounded-2xl hover:bg-red-600">GİDERİ İŞLE</button>
                </div>
                <div id="gider-list" class="space-y-4"></div>
            </div>
        </main>
    </div>

    <div id="finance-modal" class="hidden fixed inset-0 z-[200] bg-slate-900/90 flex items-center justify-center p-6 backdrop-blur-md">
        <div class="bg-white w-full max-w-lg rounded-[4rem] shadow-2xl p-12 space-y-6">
            <h2 class="text-3xl font-black uppercase text-center text-orange-500">FİNANSAL DURUM</h2>
            <div class="p-8 bg-slate-50 rounded-[2.5rem] flex justify-between"><span class="font-bold">DEPO DEĞERİ</span><span id="fin-stok" class="font-black text-emerald-600">₺0</span></div>
            <div class="p-8 bg-slate-50 rounded-[2.5rem] flex justify-between"><span class="font-bold">HARCAMALAR</span><span id="fin-gider" class="font-black text-red-500">₺0</span></div>
            <div class="p-8 bg-orange-500 text-white rounded-[2.5rem] flex justify-between font-black"><span class="uppercase">NET DURUM</span><span id="fin-net">₺0</span></div>
            <button onclick="closeFinanceModal()" class="w-full py-6 bg-slate-900 text-white font-black rounded-3xl">KAPAT</button>
        </div>
    </div>

    <script>
        let products = []; let expenses = []; let customers = [];
        let totalVal = 0; let totalGid = 0;

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

        async function yukleStok() {
            const res = await fetch('/api/products');
            products = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            let tV = 0;
            document.getElementById('stok-list').innerHTML = products
                .filter(i => (i.name + i.code + (i.category || '')).toLowerCase().includes(q)).reverse()
                .map(i => {
                    tV += (i.stock * i.price);
                    const isCrit = i.stock <= 2;
                    return `<tr class="${isCrit ? 'critical-row' : ''} group">
                        <td class="px-8 py-7"><div class="font-black ${isCrit?'text-red-700':'text-slate-800'} text-lg uppercase">${i.name}</div><div class="text-[10px] font-black text-orange-500">${i.code}</div></td>
                        <td class="px-8 py-7"><span class="bg-slate-100 px-3 py-1 rounded-full text-[10px] font-black">${i.category || 'GENEL'}</span></td>
                        <td class="px-8 py-7 text-center"><div class="flex items-center justify-center gap-3 bg-white border p-2 rounded-2xl">
                            <button onclick="stokGuncelle('${i._id}',-1)" class="w-8 h-8 text-red-500 font-black">-</button>
                            <span class="font-black">${i.stock}</span>
                            <button onclick="stokGuncelle('${i._id}',1)" class="w-8 h-8 text-emerald-500 font-black">+</button>
                        </div></td>
                        <td class="px-8 py-7 text-right font-black">₺${i.price.toLocaleString()}</td>
                        <td class="px-8 py-7 text-right"><button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash-alt"></i></button></td>
                    </tr>`;
                }).join('');
            totalVal = tV;
        }

        async function yukleDashboard() {
            const [pRes, gRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/customers')]);
            products = await pRes.json(); expenses = await gRes.json(); customers = await cRes.json();
            document.getElementById('dash-count').innerText = products.length;
            document.getElementById('dash-crit').innerText = products.filter(x => x.stock <= 2).length;
            document.getElementById('dash-cari').innerText = customers.length;
            totalVal = 0; products.forEach(i => totalVal += (i.stock * i.price));
            totalGid = 0; expenses.forEach(i => totalGid += i.tutar);
            document.getElementById('current-date').innerText = new Date().toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        }

        function exportStokExcel() {
            if(products.length === 0) return alert("Parça yok!");
            
            // LİSTE FORMATINDA EXCEL HAZIRLAMA (Gmail gibi alt alta)
            let excelData = [["ÖZCAN OTO GÜNLÜK STOK RAPORU (" + new Date().toLocaleDateString('tr-TR') + ")"], [" "]];
            
            products.forEach(p => {
                excelData.push(["PARÇA: " + p.name.toUpperCase()]);
                excelData.push(["KOD: " + p.code]);
                excelData.push(["KATEGORİ: " + (p.category || "GENEL").toUpperCase()]);
                excelData.push(["STOK: " + p.stock + " ADET"]);
                excelData.push(["BİRİM FİYAT: ₺" + p.price.toLocaleString()]);
                excelData.push(["--------------------------------------------------"]);
            });
            
            excelData.push([" "]);
            excelData.push(["TOPLAM DEPO DEĞERİ: ₺" + totalVal.toLocaleString()]);

            const ws = XLSX.utils.aoa_to_sheet(excelData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Stok Listesi");
            XLSX.writeFile(wb, "OzcanOto_Liste_Raporu_" + new Date().toLocaleDateString('tr-TR') + ".xlsx");
        }

        function sendGmailReport() {
            if(products.length === 0) return alert("Parça yok!");
            let body = "ÖZCAN OTO GÜNLÜK STOK RAPORU (" + new Date().toLocaleDateString('tr-TR') + ")\n\n";
            products.forEach(p => {
                body += `PARÇA: ${p.name.toUpperCase()}\nKOD: ${p.code}\nKATEGORİ: ${p.category || 'GENEL'}\nSTOK: ${p.stock}\nFİYAT: ₺${p.price.toLocaleString()}\n--------------------------\n`;
            });
            body += `\nTOPLAM DEPO DEĞERİ: ₺${totalVal.toLocaleString()}`;
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Gunluk Rapor&body=${encodeURIComponent(body)}`;
        }

        async function hizliEkle() {
            const name = document.getElementById('in-name').value;
            if(!name) return alert("İsim şart!");
            const p = { 
                code: document.getElementById('in-code').value || 'KODSUZ', 
                name: name, 
                category: document.getElementById('in-cat').value || 'GENEL',
                price: parseFloat(document.getElementById('in-price').value || 0), 
                stock: document.getElementById('in-stock').value === "" ? 1 : parseInt(document.getElementById('in-stock').value)
            };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            ['in-name', 'in-code', 'in-price', 'in-cat', 'in-stock'].forEach(id => document.getElementById(id).value = '');
            yukleStok();
        }

        async function cariEkle() {
            const ad = document.getElementById('cari-ad').value;
            if(!ad) return alert("İsim şart!");
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ad, tel: document.getElementById('cari-tel').value, tarih: new Date().toLocaleDateString('tr-TR')}) });
            document.getElementById('cari-ad').value = ''; document.getElementById('cari-tel').value = '';
            yukleCari();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers'); const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-8 rounded-[2.5rem] border shadow-sm flex items-center justify-between group">
                    <div><b class="text-slate-800 uppercase block">${i.ad}</b><span class="text-sm text-slate-400">${i.tel || 'NO YOK'}</span></div>
                    <button onclick="sil('${i._id}','customers')" class="text-red-500 opacity-0 group-hover:opacity-100"><i class="fas fa-trash-alt"></i></button>
                </div>`).join('');
        }

        async function giderEkle() {
            const ad = document.getElementById('gid-ad').value; const tutar = parseFloat(document.getElementById('gid-tutar').value);
            if(!ad || !tutar) return alert("Eksik bilgi!");
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ad, tutar, tarih: new Date().toLocaleDateString('tr-TR')}) });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses'); expenses = await res.json();
            document.getElementById('gider-list').innerHTML = expenses.map(i => `
                <div class="bg-white p-8 rounded-[2.5rem] border-l-[12px] border-red-500 shadow-sm flex justify-between items-center">
                    <div><b class="uppercase text-slate-800">${i.ad}</b><p class="text-[10px] text-slate-400 font-black">${i.tarih}</p></div>
                    <div class="flex items-center gap-8"><div class="font-black text-red-500 text-3xl italic">₺${i.tutar.toLocaleString()}</div>
                    <button onclick="sil('${i._id}','expenses')" class="text-slate-200 hover:text-red-500"><i class="fas fa-trash-alt"></i></button></div>
                </div>`).join('');
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Emin misin usta?')) { await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); if(col==='products') yukleStok(); else if(col==='customers') yukleCari(); else yukleGider(); }
        }

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('pro_session', 'active'); document.getElementById('login-section').classList.add('hidden'); document.getElementById('main-section').classList.remove('hidden'); showPage('dashboard');
            } else alert("Hata!");
        }

        function handleLogout() { localStorage.clear(); location.reload(); }
        function openFinanceModal() { document.getElementById('finance-modal').classList.remove('hidden'); document.getElementById('fin-stok').innerText = '₺' + totalVal.toLocaleString(); document.getElementById('fin-gider').innerText = '₺' + totalGid.toLocaleString(); document.getElementById('fin-net').innerText = '₺' + (totalVal - totalGid).toLocaleString(); }
        function closeFinanceModal() { document.getElementById('finance-modal').classList.add('hidden'); }

        window.onload = () => { if(localStorage.getItem('pro_session')) { document.getElementById('login-section').classList.add('hidden'); document.getElementById('main-section').classList.remove('hidden'); showPage('dashboard'); } };
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
