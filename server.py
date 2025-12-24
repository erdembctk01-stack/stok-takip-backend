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

# --- PANEL TASARIMI (PRO PARAŞÜT CLONE) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO PRO | Kurumsal Yönetim</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .sidebar-link { transition: all 0.2s; color: #94a3b8; }
        .sidebar-link:hover { background-color: #1e293b; color: white; }
        .sidebar-active { background-color: #2563eb !important; color: white !important; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4); }
        .page-content { display: none; animation: fadeIn 0.4s ease-out; }
        .active-section { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .custom-scroll::-webkit-scrollbar { width: 6px; }
        .custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#0f172a]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-b-[12px] border-blue-600">
            <div class="text-center mb-10">
                <div class="w-20 h-20 bg-blue-600 rounded-3xl flex items-center justify-center mx-auto mb-6 rotate-3 shadow-xl">
                    <i class="fas fa-car-side text-3xl text-white"></i>
                </div>
                <h1 class="text-4xl font-black text-slate-800 tracking-tighter italic">ÖZCAN OTO <span class="text-blue-600 font-light">PRO</span></h1>
                <p class="text-slate-400 font-bold uppercase text-[10px] tracking-[0.3em] mt-3">Kurumsal Yönetim Paneli</p>
            </div>
            <div class="space-y-5">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-5 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none font-bold focus:border-blue-500 transition-all">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none font-bold focus:border-blue-500 transition-all">
                <button onclick="handleLogin()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-5 rounded-2xl shadow-xl shadow-blue-200 transition-all active:scale-95 text-lg">GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen overflow-hidden">
        
        <aside class="w-72 bg-[#0f172a] text-white flex-shrink-0 flex flex-col shadow-2xl z-50">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-2xl font-black italic text-white uppercase tracking-tighter">ÖZCAN OTO</h2>
                <div class="flex items-center gap-2 mt-3">
                    <div class="w-2 h-2 bg-emerald-500 rounded-full animate-ping"></div>
                    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Çevrimiçi Panel</span>
                </div>
            </div>
            
            <nav class="flex-1 px-4 py-6 space-y-3 custom-scroll overflow-y-auto">
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mb-2">Genel Bakış</p>
                <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-chart-pie text-lg"></i> Dashboard
                </button>
                
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mt-6 mb-2">Ticari İşlemler</p>
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-box-open text-lg"></i> Stok ve Hizmetler
                </button>
                <button onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-users text-lg"></i> Müşteriler (Cari)
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-file-invoice text-lg"></i> Gider ve Masraflar
                </button>

                <div class="my-6 border-t border-slate-800/50"></div>
                <button onclick="sendDailyReport()" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-blue-400 text-left">
                    <i class="fas fa-cloud-download-alt"></i> Veri Yedekle
                </button>
            </nav>

            <div class="p-6 border-t border-slate-800">
                <button onclick="handleLogout()" class="w-full flex items-center justify-center gap-3 p-4 bg-red-500/10 text-red-500 rounded-2xl font-bold hover:bg-red-500 hover:text-white transition-all">
                    <i class="fas fa-power-off"></i> SİSTEMİ KAPAT
                </button>
            </div>
        </aside>

        <main class="flex-1 overflow-y-auto custom-scroll p-8 md:p-12">
            
            <div id="page-dashboard" class="page-content active-section">
                <div class="mb-10">
                    <h3 class="text-4xl font-extrabold text-slate-800 tracking-tight">Hoş geldin, Özcan Usta</h3>
                    <p class="text-slate-400 font-medium mt-1">İşletmenizin bugünkü özeti aşağıdadır.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-200">
                        <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-4 text-xl"><i class="fas fa-coins"></i></div>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Stok Değeri</p>
                        <h4 id="dash-stok-val" class="text-3xl font-black text-slate-800 mt-2">₺0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-200">
                        <div class="w-12 h-12 bg-red-100 text-red-600 rounded-2xl flex items-center justify-center mb-4 text-xl"><i class="fas fa-arrow-down"></i></div>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Toplam Gider</p>
                        <h4 id="dash-gider-val" class="text-3xl font-black text-slate-800 mt-2">₺0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-200">
                        <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-4 text-xl"><i class="fas fa-boxes"></i></div>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Ürün Çeşidi</p>
                        <h4 id="dash-item-count" class="text-3xl font-black text-slate-800 mt-2">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-200">
                        <div class="w-12 h-12 bg-amber-100 text-amber-600 rounded-2xl flex items-center justify-center mb-4 text-xl"><i class="fas fa-exclamation-triangle"></i></div>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Kritik Stok</p>
                        <h4 id="dash-crit-count" class="text-3xl font-black text-red-600 mt-2">0</h4>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex justify-between items-center mb-10">
                    <h3 class="text-3xl font-black text-slate-800 tracking-tight italic">STOK VE HİZMETLER</h3>
                    <div class="relative">
                        <i class="fas fa-search absolute left-5 top-4 text-slate-300"></i>
                        <input id="search" oninput="yukleStok()" type="text" placeholder="Parça veya kod ara..." class="pl-14 pr-6 py-4 bg-white rounded-2xl border-2 border-slate-100 outline-none focus:border-blue-500 w-80 font-bold shadow-sm">
                    </div>
                </div>

                <div class="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 mb-10">
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase ml-2">Parça Kodu</label>
                            <input id="in-code" type="text" placeholder="Örn: BKS-102" class="w-full p-4 bg-slate-50 rounded-2xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        </div>
                        <div class="space-y-2 md:col-span-1">
                            <label class="text-[10px] font-black text-slate-400 uppercase ml-2">Parça İsmi</label>
                            <input id="in-name" type="text" placeholder="Örn: Ön Balata" class="w-full p-4 bg-slate-50 rounded-2xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        </div>
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase ml-2">Kategori</label>
                            <select id="in-cat" class="w-full p-4 bg-slate-50 rounded-2xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                                <option>Motor Parçası</option><option>Fren Sistemi</option><option>Şanzıman</option><option>Yağ Grubu</option><option>Kaporta</option><option>Aksesuar</option><option>Diğer</option>
                            </select>
                        </div>
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-slate-400 uppercase ml-2">Birim Fiyat (₺)</label>
                            <input id="in-price" type="number" placeholder="0.00" class="w-full p-4 bg-slate-50 rounded-2xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        </div>
                        <div class="flex items-end">
                            <button onclick="hizliEkle()" class="w-full bg-blue-600 text-white font-black py-4 rounded-2xl hover:bg-blue-700 shadow-xl shadow-blue-100 uppercase text-xs tracking-widest">Listeye Ekle</button>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-[3rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50/50 text-slate-400 text-[10px] font-black uppercase tracking-widest border-b border-slate-100">
                            <tr>
                                <th class="px-10 py-7">Ürün / Hizmet Bilgisi</th>
                                <th class="px-10 py-7">Kategori</th>
                                <th class="px-10 py-7 text-center">Mevcut Stok</th>
                                <th class="px-10 py-7 text-right">Yönet</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8">Müşteri ve Tedarikçi Yönetimi</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 mb-8">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <input id="cari-ad" type="text" placeholder="Müşteri/Firma Adı" class="p-4 bg-slate-50 rounded-2xl font-bold outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        <input id="cari-tel" type="text" placeholder="Telefon No" class="p-4 bg-slate-50 rounded-2xl font-bold outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        <button onclick="cariEkle()" class="bg-slate-800 text-white font-black rounded-2xl hover:bg-black transition-all">YENİ CARİ KAYDET</button>
                    </div>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 gap-6"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8">Harcama ve Gider Takibi</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <input id="gid-ad" type="text" placeholder="Gider Başlığı (Kira, Fatura, Maaş)" class="p-4 bg-slate-50 rounded-2xl font-bold outline-none ring-2 ring-slate-100 focus:ring-red-500">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="p-4 bg-slate-50 rounded-2xl font-bold outline-none ring-2 ring-slate-100 focus:ring-red-500">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black rounded-2xl hover:bg-red-600 shadow-xl shadow-red-100">MASRAFI İŞLE</button>
                </div>
                <div id="gider-list" class="space-y-4"></div>
            </div>

        </main>
    </div>

    <script>
        let products = [];
        let expenses = [];
        
        // BAŞLANGIÇ AYARLARI
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
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('pro_session', 'auth_true');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
            } else { alert("Hatalı Giriş!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        // STOK FONKSİYONLARI
        async function yukleStok() {
            const res = await fetch('/api/products');
            products = await res.json();
            const query = document.getElementById('search').value.toLowerCase();
            
            document.getElementById('stok-list').innerHTML = products
                .filter(i => (i.name+i.code).toLowerCase().includes(query))
                .map(i => {
                    const isCrit = i.stock <= 2;
                    return `
                    <tr class="${isCrit ? 'bg-red-50/50' : 'hover:bg-slate-50/50'} transition-all group">
                        <td class="px-10 py-7">
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 bg-white border-2 border-slate-100 rounded-2xl flex items-center justify-center text-emerald-500 font-black text-sm shadow-sm">₺${i.price.toLocaleString()}</div>
                                <div>
                                    <div class="font-black ${isCrit ? 'text-red-600' : 'text-slate-800'} uppercase text-base">${i.name}</div>
                                    <div class="text-[10px] text-slate-400 font-bold tracking-[0.2em] mt-1">${i.code}</div>
                                </div>
                            </div>
                        </td>
                        <td class="px-10 py-7">
                            <span class="px-4 py-2 bg-slate-100 text-slate-500 rounded-full text-[10px] font-black uppercase tracking-widest border border-slate-200">${i.category || 'DİĞER'}</span>
                        </td>
                        <td class="px-10 py-7 text-center">
                            <div class="flex items-center justify-center gap-4 bg-white border border-slate-200 p-2 rounded-2xl w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('${i._id}', -1, ${i.stock})" class="w-10 h-10 text-red-500 font-black hover:bg-red-50 rounded-xl">-</button>
                                <span class="w-12 text-center font-black text-xl text-slate-700">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}', 1, ${i.stock})" class="w-10 h-10 text-emerald-500 font-black hover:bg-emerald-50 rounded-xl">+</button>
                            </div>
                        </td>
                        <td class="px-10 py-7 text-right">
                            <button onclick="sil('${i._id}','products')" class="opacity-0 group-hover:opacity-100 transition-all bg-red-50 text-red-500 w-12 h-12 rounded-2xl hover:bg-red-500 hover:text-white"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    </tr>`;
                }).join('');
        }

        async function hizliEkle() {
            const p = { 
                code: document.getElementById('in-code').value || 'KODSUZ', 
                name: document.getElementById('in-name').value, 
                category: document.getElementById('in-cat').value,
                price: parseFloat(document.getElementById('in-price').value || 0), 
                stock: 0 
            };
            if(!p.name) return alert("İsim Boş Olamaz!");
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            document.querySelectorAll('#page-stok input').forEach(el => el.value = '');
            yukleStok();
        }

        // GİDER FONKSİYONLARI
        async function giderEkle() {
            const g = { 
                ad: document.getElementById('gid-ad').value, 
                tutar: parseFloat(document.getElementById('gid-tutar').value),
                tarih: new Date().toLocaleDateString('tr-TR')
            };
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(g) });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            expenses = await res.json();
            document.getElementById('gider-list').innerHTML = expenses.map(i => `
                <div class="bg-white p-7 rounded-[2rem] border-l-[12px] border-red-500 shadow-sm flex justify-between items-center transition-all hover:scale-[1.01]">
                    <div>
                        <b class="uppercase block text-slate-800 text-lg">${i.ad}</b>
                        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">${i.tarih} | İşletme Masrafı</p>
                    </div>
                    <div class="text-right flex items-center gap-6">
                        <div class="font-black text-red-500 text-2xl">₺${i.tutar.toLocaleString()}</div>
                        <button onclick="sil('${i._id}','expenses')" class="text-slate-200 hover:text-red-500"><i class="fas fa-trash-alt text-xl"></i></button>
                    </div>
                </div>`).join('');
        }

        // CARİ FONKSİYONLARI
        async function cariEkle() {
            const c = { ad: document.getElementById('cari-ad').value, tel: document.getElementById('cari-tel').value };
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(c) });
            document.getElementById('cari-ad').value = ''; document.getElementById('cari-tel').value = '';
            yukleCari();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 flex items-center gap-6">
                    <div class="w-16 h-16 bg-slate-800 text-white rounded-2xl flex items-center justify-center text-xl font-bold uppercase">${i.ad.substring(0,2)}</div>
                    <div class="flex-1">
                        <b class="text-xl text-slate-800 block">${i.ad.toUpperCase()}</b>
                        <span class="text-sm text-slate-400 font-bold">${i.tel}</span>
                    </div>
                    <button onclick="sil('${i._id}','customers')" class="text-slate-200 hover:text-red-500"><i class="fas fa-user-minus"></i></button>
                </div>`).join('');
        }

        // DASHBOARD HESAPLAMALARI
        async function yukleDashboard() {
            const [pRes, gRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses')]);
            const pData = await pRes.json();
            const gData = await gRes.json();
            
            let sVal = 0; let crit = 0;
            pData.forEach(p => { sVal += (p.stock * p.price); if(p.stock <= 2) crit++; });
            let gVal = 0;
            gData.forEach(g => { gVal += g.tutar; });

            document.getElementById('dash-stok-val').innerText = '₺' + sVal.toLocaleString();
            document.getElementById('dash-gider-val').innerText = '₺' + gVal.toLocaleString();
            document.getElementById('dash-item-count').innerText = pData.length;
            document.getElementById('dash-crit-count').innerText = crit;
        }

        async function stokGuncelle(id, change, current) {
            if(change === -1 && current <= 0) return;
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Usta, bu kayıt tamamen silinecek. Emin misin?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); 
                else if(col==='expenses') yukleGider();
                else yukleCari();
            }
        }

        function sendDailyReport() {
            alert("Rapor Hazırlanıyor... Lütfen bekleyin.");
            let body = "ÖZCAN OTO PRO - DETAYLI ENVANTER RAPORU\n";
            body += "----------------------------------------\n\n";
            products.forEach(p => { body += `[${p.category}] ${p.name} | Stok: ${p.stock} | Değer: ₺${(p.stock * p.price).toLocaleString()}\n`; });
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Pro Rapor&body=${encodeURIComponent(body)}`;
        }

        // OTURUM KONTROL
        if(localStorage.getItem('pro_session')) {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
            showPage('dashboard');
        }
    </script>
</body>
</html>
"""

# --- BACKEND API (GELİŞMİŞ) ---
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
