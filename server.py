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

# --- PANEL TASARIMI (EREN USTA PRO - KESİN ÇÖZÜM) ---
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
        .page-content { display: none; animation: fadeIn 0.3s ease-in-out; }
        .active-section { display: block; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body class="min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#1a1a1a]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-b-[12px] border-orange-500 text-center">
            <h1 class="text-3xl font-black mb-8 italic">ÖZCAN OTO <span class="text-orange-500">PRO</span></h1>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-100 rounded-xl outline-none font-bold">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-100 rounded-xl outline-none font-bold">
                <button onclick="handleLogin()" class="w-full bg-orange-500 text-white font-black py-4 rounded-xl shadow-lg">GİRİŞ</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        <aside class="w-64 bg-[#1a1a1a] text-white flex-shrink-0 flex flex-col p-6 gap-4">
            <h2 class="text-xl font-black italic mb-6">ÖZCAN OTO</h2>
            <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-active flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-chart-pie"></i> Özet</button>
            <button onclick="showPage('stok')" id="btn-stok" class="flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-box"></i> Stoklar</button>
            <button onclick="showPage('cari')" id="btn-cari" class="flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-address-book"></i> Rehber</button>
            <button onclick="showPage('gider')" id="btn-gider" class="flex items-center gap-3 p-4 rounded-xl font-bold transition-all"><i class="fas fa-wallet"></i> Giderler</button>
            <button onclick="handleLogout()" class="mt-auto p-4 text-red-400 font-bold">Çıkış Yap</button>
        </aside>

        <main class="flex-1 p-10 overflow-y-auto">
            
            <div id="page-dashboard" class="page-content active-section">
                <h2 class="text-3xl font-black text-slate-800 mb-6">Hoş geldin, Eren Usta</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 text-white">
                    <div class="bg-orange-500 p-8 rounded-3xl shadow-lg">
                        <p class="text-sm font-bold opacity-80 uppercase">Toplam Mal Değeri</p>
                        <h3 id="dash-stok-val" class="text-3xl font-black mt-2">₺0</h3>
                    </div>
                    <div class="bg-slate-800 p-8 rounded-3xl shadow-lg">
                        <p class="text-sm font-bold opacity-80 uppercase">Kritik Stoklar</p>
                        <h3 id="dash-critical-count" class="text-3xl font-black mt-2">0 Parça</h3>
                    </div>
                    <div class="bg-emerald-600 p-8 rounded-3xl shadow-lg">
                        <p class="text-sm font-bold opacity-80 uppercase">Rehber Kaydı</p>
                        <h3 id="dash-customer-count" class="text-3xl font-black mt-2">0 Kişi</h3>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-center mb-8">
                    <h3 class="text-2xl font-black italic uppercase">Parça Yönetimi</h3>
                    <div class="flex gap-4">
                        <button onclick="exportToExcel()" class="bg-emerald-500 text-white px-4 py-2 rounded-lg font-bold text-sm"><i class="fas fa-file-excel"></i> Excel Al</button>
                        <input id="search" oninput="yukleStok()" type="text" placeholder="Ara..." class="p-2 border rounded-lg font-bold outline-none">
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border mb-8 grid grid-cols-5 gap-3">
                    <input id="in-code" type="text" placeholder="Kod" class="p-3 bg-slate-50 border rounded-xl font-bold outline-none">
                    <input id="in-name" type="text" placeholder="Parça Adı" class="p-3 bg-slate-50 border rounded-xl font-bold outline-none">
                    <input id="in-price" type="number" placeholder="Fiyat" class="p-3 bg-slate-50 border rounded-xl font-bold outline-none">
                    <input id="in-stock" type="number" placeholder="Stok" class="p-3 bg-slate-50 border rounded-xl font-bold outline-none">
                    <button onclick="hizliEkle()" class="bg-orange-500 text-white font-black rounded-xl hover:bg-orange-600">LİSTEYE EKLE</button>
                </div>

                <div class="bg-white rounded-2xl shadow-xl overflow-hidden border">
                    <table class="w-full text-left" id="stok-table-data">
                        <thead class="bg-slate-50 border-b">
                            <tr>
                                <th class="p-5 text-xs font-black uppercase">Parça / Kod</th>
                                <th class="p-5 text-xs font-black uppercase text-center">Stok</th>
                                <th class="p-5 text-xs font-black uppercase text-right">Fiyat</th>
                                <th class="p-5 text-xs font-black uppercase text-right">Sil</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-2xl font-black mb-6">MÜŞTERİ REHBERİ</h3>
                <div class="bg-white p-6 rounded-2xl border mb-6 grid grid-cols-3 gap-4">
                    <input id="cari-ad" type="text" placeholder="Ad Soyad" class="p-3 border rounded-xl font-bold">
                    <input id="cari-tel" type="text" placeholder="Telefon" class="p-3 border rounded-xl font-bold">
                    <button onclick="cariEkle()" class="bg-slate-800 text-white font-black rounded-xl">REHBERE EKLE</button>
                </div>
                <div id="cari-list" class="grid grid-cols-2 gap-4"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-2xl font-black mb-6">GİDERLER</h3>
                <div class="bg-white p-6 rounded-2xl border mb-6 grid grid-cols-3 gap-4">
                    <input id="gid-ad" type="text" placeholder="Açıklama" class="p-3 border rounded-xl font-bold">
                    <input id="gid-tutar" type="number" placeholder="Tutar" class="p-3 border rounded-xl font-bold">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black rounded-xl">KAYDET</button>
                </div>
                <div id="gider-list" class="space-y-3"></div>
            </div>

        </main>
    </div>

    <script>
        // --- TEMEL MANTIK ---
        async function yukleStok() {
            try {
                const res = await fetch('/api/products');
                const data = await res.json();
                const query = document.getElementById('search').value.toLowerCase();
                const list = document.getElementById('stok-list');
                
                list.innerHTML = data
                    .filter(i => (i.name + (i.code || '')).toLowerCase().includes(query))
                    .reverse() // En yeni eklenen en üstte
                    .map(i => `
                        <tr class="border-b hover:bg-slate-50 transition-all">
                            <td class="p-5 font-bold uppercase">${i.name} <br><span class="text-[10px] text-slate-400 font-normal">${i.code || '-'}</span></td>
                            <td class="p-5 text-center">
                                <div class="flex items-center justify-center gap-3">
                                    <button onclick="stokGuncelle('${i._id}', -1)" class="w-6 h-6 border rounded">-</button>
                                    <span class="font-black ${i.stock < 5 ? 'text-red-500' : ''}">${i.stock}</span>
                                    <button onclick="stokGuncelle('${i._id}', 1)" class="w-6 h-6 border rounded">+</button>
                                </div>
                            </td>
                            <td class="p-5 text-right font-black">₺${i.price.toLocaleString()}</td>
                            <td class="p-5 text-right">
                                <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>`).join('');
            } catch(e) { console.log("Hata:", e); }
        }

        async function hizliEkle() {
            const name = document.getElementById('in-name').value;
            const code = document.getElementById('in-code').value;
            const price = parseFloat(document.getElementById('in-price').value || 0);
            const stock = parseInt(document.getElementById('in-stock').value || 0);

            if(!name) return alert("İsimsiz parça olmaz Eren Usta!");

            const veri = { name, code, price, stock, category: "Genel" };

            // Veriyi gönder
            const response = await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(veri)
            });

            if(response.ok) {
                // Formu temizle
                document.getElementById('in-name').value = '';
                document.getElementById('in-code').value = '';
                document.getElementById('in-price').value = '';
                document.getElementById('in-stock').value = '';
                
                // Listeyi HEMEN yenile
                await yukleStok();
                alert("Başarıyla listeye eklendi!");
            }
        }

        async function yukleDashboard() {
            const [pRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/customers')]);
            const pData = await pRes.json();
            const cData = await cRes.json();
            
            let totalVal = 0;
            let critical = 0;
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
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-4 rounded-xl border flex justify-between items-center shadow-sm">
                    <div><b class="uppercase font-black text-slate-800">${i.ad}</b><p class="text-orange-600 font-bold">${i.tel}</p></div>
                    <button onclick="sil('${i._id}','customers')" class="text-red-300"><i class="fas fa-trash"></i></button>
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
                <div class="bg-white p-4 rounded-xl border-l-4 border-red-500 shadow-sm flex justify-between items-center">
                    <div><b class="uppercase">${i.ad}</b><p class="text-[10px] text-slate-400">${i.tarih}</p></div>
                    <b class="text-red-500 font-black">₺${i.tutar.toLocaleString()}</b>
                </div>`).join('');
        }

        async function sil(id, col) {
            if(confirm('Silinsin mi usta?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); else if(col==='expenses') yukleGider(); else yukleCari();
            }
        }

        function exportToExcel() {
            const wb = XLSX.utils.table_to_book(document.getElementById("stok-table-data"));
            XLSX.writeFile(wb, "OzcanOto_Stok.xlsx");
        }

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('aside button').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'stok') yukleStok();
            if(pageId === 'dashboard') yukleDashboard();
            if(pageId === 'gider') yukleGider();
            if(pageId === 'cari') yukleCari();
        }

        function handleLogin() {
            const u = document.getElementById('log-user').value;
            const p = document.getElementById('log-pass').value;
            if(u === "ozcanoto" && p === "eren9013") {
                localStorage.setItem('auth', '1');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
            } else { alert("Yanlış şifre!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }
        if(localStorage.getItem('auth')) {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
            showPage('dashboard');
        }
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
