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

# --- PANEL TASARIMI (EREN USTA PRO - OTOMATİK LİSTELEME FİKS) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO PRO | Eren Usta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .sidebar-active { background-color: #f97316 !important; color: white !important; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4); }
        .page-content { display: none; }
        .active-section { display: block; }
    </style>
</head>
<body class="min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#1a1a1a]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-b-[12px] border-orange-500 text-center">
            <h1 class="text-3xl font-black mb-8 italic text-slate-800 uppercase">ÖZCAN OTO <span class="text-orange-500">PRO</span></h1>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-100 rounded-xl outline-none font-bold focus:ring-2 ring-orange-400 transition-all">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-100 rounded-xl outline-none font-bold focus:ring-2 ring-orange-400 transition-all">
                <button onclick="handleLogin()" class="w-full bg-orange-500 text-white font-black py-4 rounded-xl shadow-lg hover:bg-orange-600 transition-all">SİSTEME GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        <aside class="w-64 bg-[#1a1a1a] text-white flex-shrink-0 flex flex-col p-6 gap-4 shadow-2xl">
            <h2 class="text-xl font-black italic mb-6 border-b border-slate-700 pb-4">ÖZCAN OTO</h2>
            <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-active flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-chart-pie"></i> Özet</button>
            <button onclick="showPage('stok')" id="btn-stok" class="flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-box"></i> Stoklar</button>
            <button onclick="showPage('cari')" id="btn-cari" class="flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-address-book"></i> Rehber</button>
            <button onclick="showPage('gider')" id="btn-gider" class="flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-wallet"></i> Giderler</button>
            <button onclick="handleLogout()" class="mt-auto p-4 text-red-400 font-bold hover:bg-red-500/10 rounded-xl transition-all">Çıkış Yap</button>
        </aside>

        <main class="flex-1 p-10 overflow-y-auto">
            
            <div id="page-dashboard" class="page-content active-section">
                <h2 class="text-3xl font-black text-slate-800 mb-6 uppercase italic">Hoş geldin, Eren Usta</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-white">
                    <div class="bg-orange-500 p-8 rounded-3xl shadow-lg shadow-orange-100">
                        <p class="text-xs font-bold opacity-80 uppercase">Toplam Mal Değeri</p>
                        <h3 id="dash-stok-val" class="text-3xl font-black mt-2">₺0</h3>
                    </div>
                    <div class="bg-slate-800 p-8 rounded-3xl shadow-lg shadow-slate-200">
                        <p class="text-xs font-bold opacity-80 uppercase">Kritik Stoklar ( < 5 )</p>
                        <h3 id="dash-critical-count" class="text-3xl font-black mt-2">0 Parça</h3>
                    </div>
                    <div class="bg-emerald-600 p-8 rounded-3xl shadow-lg shadow-emerald-100">
                        <p class="text-xs font-bold opacity-80 uppercase">Kayıtlı Müşteri</p>
                        <h3 id="dash-customer-count" class="text-3xl font-black mt-2">0 Kişi</h3>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-2xl font-black italic uppercase text-slate-800">Parça Yönetimi</h3>
                    <div class="flex gap-4">
                        <button onclick="exportToExcel()" class="bg-emerald-500 text-white px-6 py-2 rounded-xl font-black text-xs shadow-md hover:bg-emerald-600 transition-all"><i class="fas fa-file-excel mr-2"></i>EXCEL AL</button>
                        <input id="search" oninput="yukleStok()" type="text" placeholder="Parça veya kod ara..." class="p-3 border rounded-xl font-bold outline-none shadow-sm w-72 focus:border-orange-500 transition-all">
                    </div>
                </div>

                <div class="bg-white p-6 rounded-3xl shadow-md border border-slate-100 mb-8 flex flex-wrap gap-4">
                    <input id="in-code" type="text" placeholder="Parça Kodu" class="flex-1 min-w-[120px] p-4 bg-slate-50 border border-transparent rounded-2xl font-bold outline-none focus:bg-white focus:border-orange-200 transition-all">
                    <input id="in-name" type="text" placeholder="Parça Adı" class="flex-1 min-w-[200px] p-4 bg-slate-50 border border-transparent rounded-2xl font-bold outline-none focus:bg-white focus:border-orange-200 transition-all">
                    <input id="in-cat" type="text" placeholder="Kategori" class="flex-1 min-w-[150px] p-4 bg-slate-50 border border-transparent rounded-2xl font-bold outline-none focus:bg-white focus:border-orange-200 transition-all">
                    <input id="in-price" type="number" placeholder="Fiyat" class="w-32 p-4 bg-slate-50 border border-transparent rounded-2xl font-bold outline-none focus:bg-white focus:border-orange-200 transition-all">
                    <input id="in-stock" type="number" placeholder="Stok" class="w-24 p-4 bg-slate-50 border border-transparent rounded-2xl font-bold outline-none focus:bg-white focus:border-orange-200 transition-all">
                    <button onclick="hizliEkle()" class="bg-orange-500 text-white font-black px-10 py-4 rounded-2xl hover:bg-orange-600 shadow-xl shadow-orange-100 transition-all">KAYDET</button>
                </div>

                <div class="bg-white rounded-[2rem] shadow-xl overflow-hidden border border-slate-100">
                    <table class="w-full text-left" id="stok-table-data">
                        <thead class="bg-slate-50 border-b border-slate-100">
                            <tr>
                                <th class="p-6 text-xs font-black uppercase text-slate-400">Parça Bilgisi</th>
                                <th class="p-6 text-xs font-black uppercase text-slate-400">Kategori</th>
                                <th class="p-6 text-xs font-black uppercase text-slate-400 text-center">Mevcut Stok</th>
                                <th class="p-6 text-xs font-black uppercase text-slate-400 text-right">Birim Fiyat</th>
                                <th class="p-6 text-xs font-black uppercase text-slate-400 text-right">Sil</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-50">
                            </tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-2xl font-black mb-6 italic uppercase">Müşteri Rehberi</h3>
                <div class="bg-white p-6 rounded-2xl border mb-6 flex gap-4 shadow-sm">
                    <input id="cari-ad" type="text" placeholder="Müşteri Ad Soyad" class="flex-1 p-4 border rounded-xl font-bold outline-none">
                    <input id="cari-tel" type="text" placeholder="Telefon" class="flex-1 p-4 border rounded-xl font-bold outline-none">
                    <button onclick="cariEkle()" class="bg-slate-800 text-white font-black px-10 rounded-xl hover:bg-black transition-all">EKLE</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-3 gap-4"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-2xl font-black mb-6 italic uppercase text-red-600">Gider Kayıtları</h3>
                <div class="bg-white p-6 rounded-2xl border mb-6 flex gap-4 shadow-sm">
                    <input id="gid-ad" type="text" placeholder="Gider Açıklaması" class="flex-1 p-4 border rounded-xl font-bold outline-none">
                    <input id="gid-tutar" type="number" placeholder="Tutar" class="w-48 p-4 border rounded-xl font-bold outline-none">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black px-10 rounded-xl hover:bg-red-600 transition-all">KAYDET</button>
                </div>
                <div id="gider-list" class="space-y-3"></div>
            </div>

        </main>
    </div>

    <script>
        // --- STOK LİSTELEME (DÜZELTİLDİ) ---
        async function yukleStok() {
            try {
                const res = await fetch('/api/products');
                const data = await res.json();
                const query = (document.getElementById('search').value || "").toLowerCase();
                const list = document.getElementById('stok-list');
                
                const filtered = data.filter(i => 
                    (i.name || "").toLowerCase().includes(query) || 
                    (i.code || "").toLowerCase().includes(query) ||
                    (i.category || "").toLowerCase().includes(query)
                ).reverse();

                list.innerHTML = filtered.map(i => `
                    <tr class="hover:bg-orange-50/50 transition-all">
                        <td class="p-6">
                            <div class="font-black text-slate-800 uppercase text-sm">${i.name}</div>
                            <div class="text-[10px] text-slate-400 font-bold tracking-widest">${i.code || '-'}</div>
                        </td>
                        <td class="p-6">
                            <span class="bg-slate-100 text-slate-600 text-[10px] px-3 py-1 rounded-full font-black uppercase">${i.category || 'Genel'}</span>
                        </td>
                        <td class="p-6 text-center">
                            <div class="flex items-center justify-center gap-4">
                                <button onclick="stokGuncelle('${i._id}', -1)" class="w-8 h-8 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-red-500 hover:text-white transition-all font-black">-</button>
                                <span class="font-black text-lg w-10 ${i.stock < 5 ? 'text-red-500 animate-pulse' : 'text-slate-700'}">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}', 1)" class="w-8 h-8 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-emerald-500 hover:text-white transition-all font-black">+</button>
                            </div>
                        </td>
                        <td class="p-6 text-right font-black text-slate-800">₺${i.price.toLocaleString()}</td>
                        <td class="p-6 text-right">
                            <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500 transition-all px-4 py-2"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    </tr>`).join('');
            } catch(e) { console.error("Stok hatası:", e); }
        }

        async function hizliEkle() {
            const name = document.getElementById('in-name').value;
            const code = document.getElementById('in-code').value;
            const category = document.getElementById('in-cat').value;
            const price = parseFloat(document.getElementById('in-price').value || 0);
            const stock = parseInt(document.getElementById('in-stock').value || 0);

            if(!name) return alert("Usta parça adını yazmadın!");

            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, code, category, price, stock })
            });

            // Temizle
            document.getElementById('in-name').value = '';
            document.getElementById('in-code').value = '';
            document.getElementById('in-cat').value = '';
            document.getElementById('in-price').value = '';
            document.getElementById('in-stock').value = '';
            
            await yukleStok(); 
            yukleDashboard();
        }

        async function yukleDashboard() {
            const [pRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/customers')]);
            const pData = await pRes.json();
            const cData = await cRes.json();
            
            let totalVal = 0; let critical = 0;
            pData.forEach(p => {
                totalVal += (p.stock * p.price);
                if(p.stock < 5) critical++;
            });

            document.getElementById('dash-stok-val').innerText = '₺' + totalVal.toLocaleString();
            document.getElementById('dash-critical-count').innerText = critical + ' Parça';
            document.getElementById('dash-customer-count').innerText = cData.length + ' Kişi';
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change})
            });
            yukleStok();
            yukleDashboard();
        }

        async function cariEkle() {
            const ad = document.getElementById('cari-ad').value;
            const tel = document.getElementById('cari-tel').value;
            if(!ad) return;
            await fetch('/api/customers', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ad, tel})
            });
            document.getElementById('cari-ad').value = ''; document.getElementById('cari-tel').value = '';
            yukleCari();
            yukleDashboard();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-5 rounded-2xl border border-slate-100 flex justify-between items-center shadow-sm">
                    <div><b class="uppercase font-black text-slate-800 text-sm">${i.ad}</b><p class="text-orange-600 font-bold text-xs">${i.tel}</p></div>
                    <button onclick="sil('${i._id}','customers')" class="text-slate-300 hover:text-red-500 transition-all"><i class="fas fa-trash"></i></button>
                </div>`).join('');
        }

        async function giderEkle() {
            const ad = document.getElementById('gid-ad').value;
            const tutar = parseFloat(document.getElementById('gid-tutar').value || 0);
            await fetch('/api/expenses', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ad, tutar, tarih: new Date().toLocaleDateString('tr-TR')})
            });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            const data = await res.json();
            document.getElementById('gider-list').innerHTML = data.map(i => `
                <div class="bg-white p-5 rounded-2xl border-l-4 border-red-500 shadow-sm flex justify-between items-center">
                    <div><b class="uppercase text-sm">${i.ad}</b><p class="text-[10px] text-slate-400 font-bold">${i.tarih}</p></div>
                    <b class="text-red-500 font-black">₺${i.tutar.toLocaleString()}</b>
                </div>`).join('');
        }

        async function sil(id, col) {
            if(confirm('Sileyim mi usta?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); else if(col==='expenses') yukleGider(); else yukleCari();
            }
        }

        function exportToExcel() {
            const wb = XLSX.utils.table_to_book(document.getElementById("stok-table-data"));
            XLSX.writeFile(wb, "OzcanOto_Stok_Listesi.xlsx");
        }

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('aside button').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            
            // Sayfa geçişlerinde her zaman veriyi tazele
            if(pageId === 'stok') yukleStok();
            if(pageId === 'dashboard') yukleDashboard();
            if(pageId === 'gider') yukleGider();
            if(pageId === 'cari') yukleCari();
        }

        function handleLogin() {
            const u = document.getElementById('log-user').value;
            const p = document.getElementById('log-pass').value;
            if(u === "ozcanoto" && p === "eren9013") {
                localStorage.setItem('auth_token', '9013_active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
                // Giriş yapınca stokları arka planda çek
                yukleStok();
            } else { alert("Şifre yanlış usta!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        // --- SAYFA AÇILIŞ KONTROLÜ ---
        window.onload = () => {
            if(localStorage.getItem('auth_token')) {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
                yukleStok(); // SAYFA YÜKLENDİĞİNDE STOKLARI ÇEK
            }
        };
    </script>
</body>
</html>
"""

# --- BACKEND API ---
@app.route('/')
def index():
    return render_template_string(HTML_PANEL)

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
