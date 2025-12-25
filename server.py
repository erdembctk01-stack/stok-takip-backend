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
    <title>ÖZCAN OTO | Kurumsal Yönetim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; overflow: hidden; background-color: #f8fafc; }
        .sidebar { background: #0f172a; border-right: 1px solid #1e293b; }
        .sidebar-link { transition: all 0.2s ease; color: #94a3b8; border-radius: 0.75rem; margin-bottom: 0.25rem; cursor: pointer; }
        .sidebar-link:hover { background: #1e293b; color: #f8fafc; }
        .sidebar-active { background: #f97316 !important; color: white !important; font-weight: 700; }
        .page-content { display: none; height: 100vh; overflow-y: auto; padding: 3rem; }
        .active-section { display: block; animation: fadeIn 0.3s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .custom-card { border-radius: 1.5rem; background: white; border: 1px solid #e2e8f0; }
        .critical-row { background-color: #fef2f2 !important; color: #991b1b; }
    </style>
</head>
<body>

    <div id="login-section" class="fixed inset-0 z-[300] flex items-center justify-center bg-[#0f172a]">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl w-full max-w-md border-t-8 border-orange-500 text-center">
            <h1 class="text-2xl font-extrabold text-slate-800 tracking-tight uppercase">ÖZCAN OTO PRO</h1>
            <div class="space-y-4 mt-8">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-50 rounded-xl font-medium text-sm outline-none border border-transparent focus:border-orange-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 rounded-xl font-medium text-sm outline-none border border-transparent focus:border-orange-500">
                <button onclick="handleLogin()" class="w-full bg-slate-900 hover:bg-black text-white font-bold py-4 rounded-xl shadow-lg transition-all uppercase text-sm tracking-wider">Sisteme Giriş Yap</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex h-screen">
        <aside class="w-72 sidebar text-white flex-shrink-0 flex flex-col">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-xl font-black tracking-tighter text-white uppercase">ÖZCAN OTO</h2>
                <p class="text-[10px] text-orange-500 font-bold uppercase tracking-[0.2em]">Yedek Parça & Servis</p>
            </div>
            <nav class="flex-1 px-4 py-6 space-y-1">
                <div onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active flex items-center gap-3 p-4 text-sm font-semibold"><i class="fas fa-chart-line w-5"></i> Dashboard</div>
                <div onclick="showPage('stok')" id="btn-stok" class="sidebar-link flex items-center gap-3 p-4 text-sm font-semibold"><i class="fas fa-boxes w-5"></i> Parça Yönetimi</div>
                <div onclick="showPage('fatura')" id="btn-fatura" class="sidebar-link flex items-center gap-3 p-4 text-sm font-semibold"><i class="fas fa-file-invoice w-5"></i> Fatura Kes</div>
                <div onclick="showPage('log')" id="btn-log" class="sidebar-link flex items-center gap-3 p-4 text-sm font-semibold"><i class="fas fa-history w-5"></i> Satış Geçmişi</div>
                <div onclick="showPage('cari')" id="btn-cari" class="sidebar-link flex items-center gap-3 p-4 text-sm font-semibold"><i class="fas fa-users w-5"></i> Cari Kayıtlar</div>
                <div onclick="showPage('gider')" id="btn-gider" class="sidebar-link flex items-center gap-3 p-4 text-sm font-semibold"><i class="fas fa-wallet w-5"></i> Harcamalar</div>
            </nav>
            <div class="p-6 border-t border-slate-800">
                <button onclick="handleLogout()" class="w-full p-3 text-slate-400 hover:text-red-400 text-xs font-bold uppercase transition-all"><i class="fas fa-sign-out-alt mr-2"></i> Güvenli Çıkış</button>
            </div>
        </aside>

        <main class="flex-1 relative overflow-hidden">
            <div id="page-dashboard" class="page-content active-section">
                <h3 class="text-3xl font-extrabold text-slate-800 uppercase italic mb-8">Sistem Paneli</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div class="custom-card p-8 border-l-4 border-emerald-500">
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Günlük Satış Kazancı</p>
                        <h4 id="dash-kazanc" class="text-3xl font-black text-emerald-600">₺0</h4>
                    </div>
                    <div class="custom-card p-8 border-l-4 border-red-500">
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Günlük Toplam Gider</p>
                        <h4 id="dash-gider" class="text-3xl font-black text-red-600">₺0</h4>
                    </div>
                    <div class="custom-card p-8 border-l-4 border-blue-600">
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Toplam Depo Değeri</p>
                        <h4 id="dash-depo" class="text-3xl font-black text-slate-800">****</h4>
                        <button onclick="hesaplaDepo()" class="mt-4 text-[9px] font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full uppercase">Hesapla</button>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                    <div class="custom-card p-8 border-l-4 border-green-600 flex justify-between items-center cursor-pointer hover:bg-green-50 transition-all" onclick="exportToExcel('products')">
                        <div>
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Envanter Raporu</p>
                            <h4 class="text-xl font-bold text-slate-800">Stok Excel Olarak İndir</h4>
                        </div>
                        <i class="fas fa-file-excel text-3xl text-green-600"></i>
                    </div>
                    <div class="custom-card p-8 border-l-4 border-orange-400 flex justify-between items-center cursor-pointer hover:bg-orange-50 transition-all" onclick="sendGmailReport('products')">
                        <div>
                            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Hızlı Paylaşım</p>
                            <h4 class="text-xl font-bold text-slate-800">Stoğu Gmail İle Gönder</h4>
                        </div>
                        <i class="fas fa-envelope text-3xl text-orange-500"></i>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-center mb-8">
                    <h3 class="text-2xl font-bold text-slate-800 uppercase">Envanter Listesi</h3>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Parça veya kod ara..." class="p-3 bg-white border border-slate-200 rounded-xl w-80 text-sm font-medium shadow-sm outline-none">
                </div>
                <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden text-sm">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                            <tr><th class="px-8 py-5">Parça Tanımı</th><th class="px-8 py-5 text-center">Stok Durumu</th><th class="px-8 py-5 text-right">Birim Fiyat</th><th class="px-8 py-5 text-right">İşlem</th></tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-fatura" class="page-content">
                <h3 class="text-2xl font-bold text-slate-800 mb-8 uppercase">Satış ve Fatura İşlemi</h3>
                <div class="custom-card p-10 mb-8">
                    <div class="grid grid-cols-2 gap-6">
                        <input id="fat-ad" type="text" placeholder="Müşteri Ad Soyad" class="p-4 bg-slate-50 rounded-xl font-semibold border-none">
                        <input id="fat-tel" type="text" placeholder="İletişim No" class="p-4 bg-slate-50 rounded-xl font-semibold border-none">
                        <select id="fat-parca" class="p-4 bg-slate-50 rounded-xl font-semibold border-none"></select>
                        <input id="fat-adet" type="number" placeholder="Satış Miktarı" class="p-4 bg-slate-50 rounded-xl font-semibold border-none">
                        <button onclick="faturaKes()" class="col-span-2 bg-orange-600 text-white font-bold py-5 rounded-xl hover:bg-orange-700 shadow-lg uppercase text-sm">Faturayı Onayla ve Stoktan Düş</button>
                    </div>
                </div>
            </div>

            <div id="page-log" class="page-content">
                <div class="flex justify-between items-center mb-8">
                    <h3 class="text-2xl font-bold text-slate-800 uppercase">Satış Geçmişi & Kayıtlar</h3>
                    <div class="flex gap-2">
                         <button onclick="exportToExcel('invoices')" class="bg-green-600 text-white px-4 py-2 rounded-lg text-xs font-bold uppercase"><i class="fas fa-file-excel mr-2"></i>Excel İndir</button>
                         <button onclick="sendGmailReport('invoices')" class="bg-orange-500 text-white px-4 py-2 rounded-lg text-xs font-bold uppercase"><i class="fas fa-envelope mr-2"></i>Gmail Paylaş</button>
                    </div>
                </div>
                <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden text-sm">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 text-slate-500 font-bold uppercase text-[10px]">
                            <tr><th class="px-6 py-4">Müşteri</th><th class="px-6 py-4">Satılan Parça</th><th class="px-6 py-4 text-center">Adet</th><th class="px-6 py-4 text-right">Tarih</th><th class="px-6 py-4 text-right">İşlem</th></tr>
                        </thead>
                        <tbody id="fatura-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-2xl font-bold text-slate-800 mb-8 uppercase">Cari Rehber</h3>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-2xl font-bold text-slate-800 mb-8 uppercase text-red-700">Gider Yönetimi</h3>
                <div id="gider-list" class="space-y-4"></div>
            </div>
        </main>
    </div>

    <script>
        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('pro_session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
            } else alert("Hatalı Giriş!");
        }

        async function exportToExcel(type) {
            try {
                const res = await fetch(`/api/${type}`);
                const data = await res.json();
                const bugun = new Date().toLocaleDateString('tr-TR');
                
                let reportRows = [];
                
                if(type === 'products') {
                    reportRows.push(["ÖZCAN OTO GÜNLÜK RAPOR - " + bugun]);
                    reportRows.push([]); 
                    data.forEach(i => {
                        reportRows.push(["PARÇA: " + i.name]);
                        reportRows.push(["KOD: " + (i.code || "-")]);
                        reportRows.push(["STOK: " + i.stock + " ADET"]);
                        reportRows.push(["FİYAT: ₺" + i.price]);
                        reportRows.push(["------------------"]);
                    });
                    let total = 0; data.forEach(p => total += (Number(p.stock) * Number(p.price)));
                    reportRows.push([]);
                    reportRows.push(["TOPLAM DEPO DEĞERİ: ₺" + total.toLocaleString('tr-TR')]);
                } else {
                    reportRows.push(["ÖZCAN OTO GÜNLÜK SATIŞ RAPORU - " + bugun]);
                    reportRows.push([]);
                    data.forEach(i => {
                        reportRows.push(["MÜŞTERİ: " + i.ad]);
                        reportRows.push(["PARÇA: " + i.parca_ad]);
                        reportRows.push(["ADET: " + i.adet]);
                        reportRows.push(["TARİH: " + i.tarih]);
                        reportRows.push(["------------------"]);
                    });
                }

                // XLSX formatında (Binary string yerine array of arrays) kayıt karakter sorununu çözer
                const ws = XLSX.utils.aoa_to_sheet(reportRows);
                const wb = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(wb, ws, "OzcanOtoRapor");
                XLSX.writeFile(wb, `OzcanOto_${type}_${bugun}.xlsx`);
            } catch (err) {
                alert("Hata: " + err.message);
            }
        }

        async function sendGmailReport(type) {
            const res = await fetch(`/api/${type}`);
            const data = await res.json();
            const bugun = new Date().toLocaleDateString('tr-TR');
            let body = `ÖZCAN OTO GÜNLÜK RAPOR - ${bugun}\n\n`;
            if(type === 'products') {
                data.forEach(i => body += `PARÇA: ${i.name}\nKOD: ${i.code || "-"}\nSTOK: ${i.stock} ADET\nFİYAT: ₺${i.price}\n------------------\n`);
                let total = 0; data.forEach(p => total += (Number(p.stock) * Number(p.price)));
                body += `\nTOPLAM DEPO DEĞERİ: ₺${total.toLocaleString('tr-TR')}`;
            } else {
                data.forEach(i => body += `MÜŞTERİ: ${i.ad}\nPARÇA: ${i.parca_ad}\nADET: ${i.adet}\nTARİH: ${i.tarih}\n------------------\n`);
            }
            window.location.href = `mailto:?subject=Ozcan Oto Rapor&body=${encodeURIComponent(body)}`;
        }

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            if(pageId === 'dashboard') yukleDashboard();
            if(pageId === 'stok') yukleStok();
            if(pageId === 'fatura' || pageId === 'log') yukleFatura();
            if(pageId === 'cari') yukleCari();
            if(pageId === 'gider') yukleGider();
        }

        async function yukleDashboard() {
            const [pRes, gRes, fRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/invoices')]);
            const prods = await pRes.json(); const exps = await gRes.json(); const invs = await fRes.json();
            const bugun = new Date().toLocaleDateString('tr-TR');
            let gG = 0; exps.forEach(e => { if(e.tarih === bugun) gG += Number(e.tutar); });
            let gK = 0; invs.forEach(i => {
                if(i.tarih.includes(bugun)) {
                    const p = prods.find(pr => pr._id === i.parca_id || pr.name === i.parca_ad);
                    if(p) gK += (Number(i.adet) * Number(p.price));
                }
            });
            document.getElementById('dash-kazanc').innerText = `₺${gK.toLocaleString('tr-TR')}`;
            document.getElementById('dash-gider').innerText = `₺${gG.toLocaleString('tr-TR')}`;
        }

        async function yukleStok() {
            const res = await fetch('/api/products'); const p = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            document.getElementById('stok-list').innerHTML = p.filter(i => (i.name + i.code).toLowerCase().includes(q)).reverse().map(i => `
                <tr class="${i.stock <= 2 ? 'critical-row' : ''}">
                    <td class="px-8 py-5"><b class="uppercase font-bold block">${i.name}</b><span class="text-[10px] text-slate-400 font-bold">${i.code || "-"}</span></td>
                    <td class="px-8 py-5 text-center font-extrabold">${i.stock}</td>
                    <td class="px-8 py-5 text-right font-bold">₺${Number(i.price).toLocaleString('tr-TR')}</td>
                    <td class="px-8 py-5 text-right"><button onclick="sil('${i._id}','products')" class="text-red-400"><i class="fas fa-trash-alt"></i></button></td>
                </tr>`).join('');
        }

        async function faturaKes() {
            const ad = document.getElementById('fat-ad').value;
            const parcaId = document.getElementById('fat-parca').value;
            const adet = document.getElementById('fat-adet').value;
            if(!ad || !parcaId || !adet) return alert("Eksik alan!");
            const res = await fetch('/api/fatura-kes', { 
                method: 'POST', 
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify({ ad, tel: document.getElementById('fat-tel').value, parcaId, adet: parseInt(adet), tarih: new Date().toLocaleString('tr-TR') }) 
            });
            const data = await res.json();
            if(data.ok) { alert("SATIŞ BAŞARILI"); yukleFatura(); } else { alert("Hata: " + data.error); }
        }

        async function yukleFatura() {
            const [pRes, fRes] = await Promise.all([fetch('/api/products'), fetch('/api/invoices')]);
            const pData = await pRes.json(); const fData = await fRes.json();
            document.getElementById('fat-parca').innerHTML = pData.map(i => `<option value="${i._id}">${i.name} (Stok: ${i.stock})</option>`).join('');
            document.getElementById('fatura-list').innerHTML = fData.reverse().map(i => `
                <tr>
                    <td class="px-6 py-4 font-bold uppercase">${i.ad}</td>
                    <td class="px-6 py-4">${i.parca_ad}</td>
                    <td class="px-6 py-4 text-center font-bold text-orange-600">${i.adet}</td>
                    <td class="px-6 py-4 text-right text-[10px] font-bold uppercase">${i.tarih}</td>
                    <td class="px-6 py-4 text-right"><button onclick="sil('${i._id}','invoices')" class="text-red-400"><i class="fas fa-trash"></i></button></td>
                </tr>`).join('');
        }

        async function sil(id, col) { 
            if(confirm('SİLİNSİN Mİ?')) { 
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); 
                // DASHBOARD'A ATMA SORUNU BURADA ÇÖZÜLDÜ:
                if(col === 'products') yukleStok(); 
                else if(col === 'invoices') yukleFatura();
                else showPage(col === 'expenses' ? 'gider' : 'cari');
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

@app.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    try:
        data = request.json
        parca_id = data.get('parcaId')
        adet = int(data.get('adet', 0))
        parca = db.products.find_one({"_id": ObjectId(parca_id)})
        current_stock = int(parca.get('stock', 0))
        db.products.update_one({"_id": ObjectId(parca_id)}, {"$set": {"stock": current_stock - adet}})
        db.invoices.insert_one({"ad": data['ad'], "tel": data['tel'], "parca_id": parca_id, "parca_ad": parca['name'], "adet": adet, "tarih": data['tarih']})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
