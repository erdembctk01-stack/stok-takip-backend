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

# --- PANEL TASARIMI (TURUNCU TEMA - FIX) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO PRO | Eren Usta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .sidebar-link { transition: all 0.2s; color: #94a3b8; }
        .sidebar-link:hover { background-color: #2d2d2d; color: white; }
        .sidebar-active { background-color: #f97316 !important; color: white !important; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4); }
        .page-content { display: none; animation: fadeIn 0.4s ease-out; }
        .active-section { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #f97316; border-radius: 10px; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#1a1a1a]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-b-[12px] border-orange-500">
            <div class="text-center mb-10">
                <div class="w-20 h-20 bg-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-6 rotate-3 shadow-xl">
                    <i class="fas fa-car-side text-3xl text-white"></i>
                </div>
                <h1 class="text-4xl font-black text-slate-800 tracking-tighter italic">ÖZCAN OTO <span class="text-orange-500 font-light">PRO</span></h1>
                <p class="text-slate-400 font-bold uppercase text-[10px] tracking-[0.3em] mt-3">Eren Usta Yönetim Paneli</p>
            </div>
            <div class="space-y-5">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-5 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none font-bold focus:border-orange-500 transition-all">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none font-bold focus:border-orange-500 transition-all">
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-5 rounded-2xl shadow-xl shadow-orange-200 transition-all active:scale-95 text-lg">GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen overflow-hidden">
        <aside class="w-72 bg-[#1a1a1a] text-white flex-shrink-0 flex flex-col shadow-2xl z-50">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-2xl font-black italic text-white uppercase tracking-tighter">ÖZCAN OTO</h2>
            </div>
            <nav class="flex-1 px-4 py-6 space-y-3 overflow-y-auto">
                <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-chart-pie"></i> Dashboard
                </button>
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-box-open"></i> Stok ve Hizmetler
                </button>
                <button onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-users"></i> Müşteriler (Cari)
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-file-invoice"></i> Giderler
                </button>
            </nav>
            <div class="p-6">
                <button onclick="handleLogout()" class="w-full p-4 bg-red-500/10 text-red-500 rounded-2xl font-bold hover:bg-red-500 hover:text-white transition-all">SİSTEMİ KAPAT</button>
            </div>
        </aside>

        <main class="flex-1 overflow-y-auto p-8 md:p-12">
            <div id="page-dashboard" class="page-content active-section">
                <div class="mb-8">
                    <h2 class="text-4xl font-black text-slate-800">Hoş geldin, Eren Usta</h2>
                    <p class="text-slate-500 font-bold mt-2">Dükkanın bugünlük özeti burada.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                    <div class="bg-orange-500 p-8 rounded-[2.5rem] text-white shadow-xl shadow-orange-200">
                        <p class="text-xs font-black uppercase opacity-80">Net Varlık (Kasa)</p>
                        <h4 id="dash-total-money" class="text-4xl font-black mt-2">₺0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border">
                        <p class="text-xs font-black text-slate-400 uppercase">Toplam Stok Değeri</p>
                        <h4 id="dash-stok-val" class="text-3xl font-black text-slate-800 mt-2">₺0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border">
                        <p class="text-xs font-black text-slate-400 uppercase">Toplam Gider</p>
                        <h4 id="dash-gider-val" class="text-3xl font-black text-red-500 mt-2">₺0</h4>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-center mb-8">
                    <h3 class="text-3xl font-black text-slate-800 uppercase">Stok Listesi</h3>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Parça ara..." class="p-4 bg-white rounded-2xl border-2 border-slate-100 outline-none focus:border-orange-500 w-64 font-bold">
                </div>

                <div class="bg-white p-6 rounded-[2rem] shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-5 gap-4">
                    <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-xl font-bold outline-none">
                    <input id="in-name" type="text" placeholder="Parça Adı" class="p-4 bg-slate-50 rounded-xl font-bold outline-none">
                    <input id="in-price" type="number" placeholder="Birim Fiyat" class="p-4 bg-slate-50 rounded-xl font-bold outline-none">
                    <input id="in-stock" type="number" placeholder="Başlangıç Stok" class="p-4 bg-slate-50 rounded-xl font-bold outline-none">
                    <button onclick="hizliEkle()" class="bg-orange-500 text-white font-black rounded-xl hover:bg-orange-600 transition-all">LİSTEYE EKLE</button>
                </div>

                <div class="bg-white rounded-[2rem] shadow-xl border overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b">
                            <tr>
                                <th class="px-8 py-5 text-xs font-black text-slate-400 uppercase">Parça / Kod</th>
                                <th class="px-8 py-5 text-xs font-black text-slate-400 uppercase text-center">Mevcut Stok</th>
                                <th class="px-8 py-5 text-xs font-black text-slate-400 uppercase text-right">Birim Fiyat</th>
                                <th class="px-8 py-5 text-xs font-black text-slate-400 uppercase text-right">İşlem</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase">Gider Kayıtları</h3>
                <div class="bg-white p-6 rounded-[2rem] border mb-8 grid grid-cols-3 gap-4">
                    <input id="gid-ad" type="text" placeholder="Gider Açıklaması" class="p-4 bg-slate-50 rounded-xl font-bold">
                    <input id="gid-tutar" type="number" placeholder="Tutar" class="p-4 bg-slate-50 rounded-xl font-bold">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black rounded-xl">KAYDET</button>
                </div>
                <div id="gider-list" class="space-y-4"></div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase">Müşteri Kayıtları</h3>
                <div class="bg-white p-6 rounded-[2rem] border mb-8 grid grid-cols-3 gap-4">
                    <input id="cari-ad" type="text" placeholder="Müşteri Ad Soyad" class="p-4 bg-slate-50 rounded-xl font-bold">
                    <input id="cari-tel" type="text" placeholder="Telefon Numarası" class="p-4 bg-slate-50 rounded-xl font-bold">
                    <button onclick="cariEkle()" class="bg-slate-800 text-white font-black rounded-xl">MÜŞTERİ EKLE</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 gap-6"></div>
            </div>
        </main>
    </div>

    <script>
        // --- TEMEL FONKSİYONLAR ---
        async function yukleStok() {
            const res = await fetch('/api/products');
            const data = await res.json();
            const query = document.getElementById('search').value.toLowerCase();
            
            const list = document.getElementById('stok-list');
            list.innerHTML = data
                .filter(i => (i.name + (i.code || '')).toLowerCase().includes(query))
                .map(i => `
                    <tr class="hover:bg-slate-50 transition-all">
                        <td class="px-8 py-6">
                            <div class="font-black text-slate-800 uppercase">${i.name}</div>
                            <div class="text-[10px] text-slate-400 font-bold tracking-widest">${i.code || 'KODSUZ'}</div>
                        </td>
                        <td class="px-8 py-6 text-center">
                            <div class="flex items-center justify-center gap-4">
                                <button onclick="stokGuncelle('${i._id}', -1)" class="w-8 h-8 bg-slate-100 rounded-lg font-bold hover:bg-orange-500 hover:text-white">-</button>
                                <span class="font-black text-lg w-8">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}', 1)" class="w-8 h-8 bg-slate-100 rounded-lg font-bold hover:bg-orange-500 hover:text-white">+</button>
                            </div>
                        </td>
                        <td class="px-8 py-6 text-right font-black text-slate-700">₺${i.price.toLocaleString()}</td>
                        <td class="px-8 py-6 text-right">
                            <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>`).join('');
        }

        async function hizliEkle() {
            const code = document.getElementById('in-code').value;
            const name = document.getElementById('in-name').value;
            const price = parseFloat(document.getElementById('in-price').value || 0);
            const stock = parseInt(document.getElementById('in-stock').value || 0);

            if(!name) return alert("Parça adını boş bırakma Eren Usta!");

            const parca = { code, name, price, stock, category: "Genel" };
            
            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(parca)
            });

            // Formu temizle
            document.getElementById('in-code').value = '';
            document.getElementById('in-name').value = '';
            document.getElementById('in-price').value = '';
            document.getElementById('in-stock').value = '';

            // Listeyi anında tazele
            yukleStok();
            alert("Parça başarıyla eklendi!");
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change})
            });
            yukleStok();
        }

        async function yukleDashboard() {
            const pRes = await fetch('/api/products');
            const gRes = await fetch('/api/expenses');
            const pData = await pRes.json();
            const gData = await gRes.json();
            
            let totalStokDeğeri = 0;
            pData.forEach(p => totalStokDeğeri += (p.stock * p.price));
            
            let totalGider = 0;
            gData.forEach(g => totalGider += g.tutar);

            document.getElementById('dash-stok-val').innerText = '₺' + totalStokDeğeri.toLocaleString();
            document.getElementById('dash-gider-val').innerText = '₺' + totalGider.toLocaleString();
            document.getElementById('dash-total-money').innerText = '₺' + (totalStokDeğeri - totalGider).toLocaleString();
        }

        async function giderEkle() {
            const ad = document.getElementById('gid-ad').value;
            const tutar = parseFloat(document.getElementById('gid-tutar').value || 0);
            if(!ad) return;
            await fetch('/api/expenses', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ad, tutar, tarih: new Date().toLocaleDateString('tr-TR')})
            });
            document.getElementById('gid-ad').value = '';
            document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            const data = await res.json();
            document.getElementById('gider-list').innerHTML = data.map(i => `
                <div class="bg-white p-5 rounded-2xl border-l-4 border-red-500 shadow-sm flex justify-between items-center">
                    <div><b class="uppercase text-slate-700">${i.ad}</b><p class="text-[10px] text-slate-400 font-bold">${i.tarih}</p></div>
                    <div class="font-black text-red-500">₺${i.tutar.toLocaleString()}</div>
                </div>`).join('');
        }

        async function cariEkle() {
            const ad = document.getElementById('cari-ad').value;
            const tel = document.getElementById('cari-tel').value;
            await fetch('/api/customers', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ad, tel})
            });
            document.getElementById('cari-ad').value = '';
            document.getElementById('cari-tel').value = '';
            yukleCari();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-6 rounded-2xl shadow-sm border flex justify-between items-center">
                    <div><b class="text-lg uppercase text-slate-800">${i.ad}</b><p class="text-slate-400 font-bold italic">${i.tel}</p></div>
                    <button onclick="sil('${i._id}','customers')" class="text-slate-300 hover:text-red-500 transition-all"><i class="fas fa-user-minus"></i></button>
                </div>`).join('');
        }

        async function sil(id, col) {
            if(confirm('Silmek istediğine emin misin usta?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); 
                else if(col==='expenses') yukleGider(); 
                else yukleCari();
            }
        }

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
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
                localStorage.setItem('eren_auth', 'true');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
            } else { alert("Şifre yanlış usta!"); }
        }

        function handleLogout() {
            localStorage.removeItem('eren_auth');
            location.reload();
        }

        if(localStorage.getItem('eren_auth')) {
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
