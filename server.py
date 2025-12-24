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

# --- PANEL TASARIMI (TURUNCU & DETAYLI) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO | Pro Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        body { font-family: 'Poppins', sans-serif; }
        .sidebar-link { transition: all 0.3s; color: #fdf2f2; }
        .sidebar-link:hover { background-color: #fb923c; color: white; }
        .sidebar-active { background-color: #f97316 !important; color: white !important; box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4); }
        .page-content { display: none; }
        .active-section { display: block; animation: slideIn 0.3s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
    </style>
</head>
<body class="bg-orange-50/30 min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-[#1a1a1a]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-t-[10px] border-orange-500">
            <div class="text-center mb-8">
                <i class="fas fa-tools text-5xl text-orange-500 mb-4"></i>
                <h1 class="text-3xl font-black text-slate-800 uppercase italic">ÖZCAN OTO PRO</h1>
                <p class="text-slate-400 font-bold text-xs mt-2 uppercase tracking-widest">Yönetici Girişi</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı" class="w-full p-4 bg-slate-50 border-2 rounded-2xl outline-none focus:border-orange-500 transition-all font-bold">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 border-2 rounded-2xl outline-none focus:border-orange-500 transition-all font-bold">
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-4 rounded-2xl shadow-lg transition-all active:scale-95">SİSTEMİ BAŞLAT</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <aside class="w-72 bg-slate-900 text-white flex-shrink-0 flex flex-col shadow-2xl">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-2xl font-black italic text-orange-500 uppercase tracking-tighter">ÖZCAN OTO</h2>
                <span class="text-[10px] text-slate-500 font-bold tracking-[0.3em]">VERSION 4.0 PRO</span>
            </div>
            
            <nav class="flex-1 px-4 py-8 space-y-3">
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-boxes"></i> Stok Takibi
                </button>
                <button onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-address-book"></i> Cari Rehber
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-wallet"></i> Gider Takibi
                </button>
                
                <div class="my-6 border-t border-slate-800"></div>
                
                <button onclick="openFinance()" class="w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-orange-400 bg-orange-500/10 hover:bg-orange-500 hover:text-white transition-all text-left">
                    <i class="fas fa-chart-line"></i> TOPLAM DEPO DEĞERİ
                </button>
                <button onclick="sendDailyReport()" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-left">
                    <i class="fas fa-share-square"></i> Gün Sonu Gönder
                </button>
            </nav>

            <div class="p-6 border-t border-slate-800">
                <button onclick="handleLogout()" class="w-full p-4 bg-red-500/10 text-red-500 rounded-xl font-bold hover:bg-red-500 hover:text-white transition-all">
                    <i class="fas fa-power-off mr-2"></i> ÇIKIŞ
                </button>
            </div>
        </aside>

        <main class="flex-1 p-10 overflow-y-auto">
            
            <div id="page-stok" class="page-content active-section">
                <div class="flex justify-between items-center mb-8">
                    <h3 class="text-3xl font-black text-slate-800">Parça Envanteri</h3>
                    <div class="relative">
                        <i class="fas fa-search absolute left-4 top-4 text-slate-400"></i>
                        <input id="search" oninput="yukleStok()" type="text" placeholder="Hızlı parça ara..." class="pl-12 pr-6 py-3 bg-white rounded-xl border-2 border-slate-100 outline-none focus:border-orange-500 w-80 font-bold shadow-sm">
                    </div>
                </div>

                <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8 grid grid-cols-1 md:grid-cols-5 gap-4">
                    <input id="in-code" type="text" placeholder="Kod" class="p-4 bg-slate-50 rounded-xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                    <input id="in-name" type="text" placeholder="Parça Adı" class="p-4 bg-slate-50 rounded-xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                    <select id="in-cat" class="p-4 bg-slate-50 rounded-xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                        <option>Motor</option><option>Fren</option><option>Şanzıman</option><option>Kaporta</option><option>Elektrik</option><option>Yağlar</option>
                    </select>
                    <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                    <button onclick="hizliEkle()" class="bg-orange-500 text-white font-black rounded-xl hover:bg-orange-600 shadow-lg shadow-orange-100 uppercase transition-all">Ekle</button>
                </div>

                <div class="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase tracking-widest">
                            <tr>
                                <th class="px-8 py-6">Parça / Kategori</th>
                                <th class="px-8 py-6 text-center">Stok Durumu</th>
                                <th class="px-8 py-6 text-right">Fiyat</th>
                                <th class="px-8 py-6 text-right">Yönet</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8">Cari Rehber & Numaralar</h3>
                <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input id="cari-ad" type="text" placeholder="İsim / Firma" class="p-4 bg-slate-50 rounded-xl font-bold outline-none border-2 border-slate-100 focus:border-orange-500">
                    <input id="cari-tel" type="text" placeholder="Telefon (05xx)" class="p-4 bg-slate-50 rounded-xl font-bold outline-none border-2 border-slate-100 focus:border-orange-500">
                    <button onclick="cariEkle()" class="bg-slate-800 text-white font-black rounded-xl hover:bg-black transition-all">NUMARAYI KAYDET</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8">Masraf Takibi</h3>
                <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input id="gid-ad" type="text" placeholder="Gider Kalemi" class="p-4 bg-slate-50 rounded-xl font-bold outline-none border-2 border-slate-100 focus:border-orange-500">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="p-4 bg-slate-50 rounded-xl font-bold outline-none border-2 border-slate-100 focus:border-orange-500">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black rounded-xl hover:bg-red-600 transition-all">GİDERİ İŞLE</button>
                </div>
                <div id="gider-list" class="space-y-4"></div>
            </div>

        </main>
    </div>

    <div id="finance-modal" class="hidden fixed inset-0 z-[110] bg-slate-900/90 flex items-center justify-center p-6 backdrop-blur-sm">
        <div class="bg-white w-full max-w-lg rounded-[3.5rem] shadow-2xl overflow-hidden border-b-[15px] border-orange-500">
            <div class="bg-orange-500 p-10 text-white text-center">
                <i class="fas fa-piggy-bank text-5xl mb-4"></i>
                <h2 class="text-3xl font-black uppercase italic tracking-tighter">Finansal Durum Paneli</h2>
            </div>
            <div class="p-10 space-y-6">
                <div class="flex justify-between items-center p-6 bg-slate-50 rounded-3xl border-2 border-slate-100">
                    <span class="font-bold text-slate-400 uppercase text-xs">Toplam Stok Değeri</span>
                    <span id="fin-stok" class="text-3xl font-black text-emerald-600">₺0</span>
                </div>
                <div class="flex justify-between items-center p-6 bg-slate-50 rounded-3xl border-2 border-slate-100">
                    <span class="font-bold text-slate-400 uppercase text-xs">Toplam Giderler</span>
                    <span id="fin-gider" class="text-3xl font-black text-red-500">₺0</span>
                </div>
                <button onclick="closeFinance()" class="w-full py-5 bg-slate-900 text-white font-black rounded-2xl uppercase tracking-widest hover:bg-slate-800 transition-all">TAMAMDIR</button>
            </div>
        </div>
    </div>

    <script>
        let currentProducts = [];
        let totalVal = 0; let totalGid = 0;

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'stok') yukleStok();
            if(pageId === 'cari') yukleCari();
            if(pageId === 'gider') yukleGider();
        }

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('session_pro', 'ok');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                yukleStok(); yukleGider();
            } else { alert("Hatalı Giriş!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        async function yukleStok() {
            const res = await fetch('/api/products');
            currentProducts = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            let tV = 0;

            document.getElementById('stok-list').innerHTML = currentProducts
                .filter(i => (i.name+i.code).toLowerCase().includes(q))
                .map(i => {
                    tV += (i.stock * i.price);
                    const zero = i.stock <= 0;
                    return `
                    <tr class="${zero ? 'bg-slate-50' : 'hover:bg-orange-50/50'} transition-all group">
                        <td class="px-8 py-6">
                            <div class="font-black ${zero ? 'text-slate-400' : 'text-slate-800'} text-lg uppercase">${i.name}</div>
                            <div class="text-[10px] font-bold text-orange-500 tracking-widest">${i.code} | ${i.category || 'GENEL'}</div>
                        </td>
                        <td class="px-8 py-6 text-center">
                            <div class="flex items-center justify-center gap-3 bg-white border border-slate-200 p-2 rounded-2xl w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('${i._id}',-1)" class="w-10 h-10 text-red-500 font-black hover:bg-red-50 rounded-xl">-</button>
                                <span class="w-12 text-center font-black text-xl ${zero ? 'text-red-500' : 'text-slate-800'}">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}',1)" class="w-10 h-10 text-emerald-500 font-black hover:bg-emerald-50 rounded-xl">+</button>
                            </div>
                        </td>
                        <td class="px-8 py-6 text-right font-black text-slate-700">₺${i.price.toLocaleString()}</td>
                        <td class="px-8 py-6 text-right">
                            <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500 transition-colors"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    </tr>`;
                }).join('');
            totalVal = tV;
        }

        async function hizliEkle() {
            const p = { 
                code: document.getElementById('in-code').value || 'KODSUZ', 
                name: document.getElementById('in-name').value, 
                category: document.getElementById('in-cat').value,
                price: parseFloat(document.getElementById('in-price').value || 0), 
                stock: 0 
            };
            if(!p.name) return alert("İsim şart!");
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            yukleStok();
        }

        async function cariEkle() {
            const c = { ad: document.getElementById('cari-ad').value, tel: document.getElementById('cari-tel').value };
            if(!c.ad || !c.tel) return alert("Bilgileri gir usta!");
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(c) });
            yukleCari();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center justify-between transition-all hover:border-orange-200">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-orange-100 text-orange-600 rounded-2xl flex items-center justify-center font-black">${i.ad.substring(0,2).toUpperCase()}</div>
                        <div>
                            <b class="text-slate-800 uppercase block">${i.ad}</b>
                            <span class="text-sm font-bold text-slate-400">${i.tel}</span>
                        </div>
                    </div>
                    <button onclick="sil('${i._id}','customers')" class="text-slate-200 hover:text-red-500"><i class="fas fa-user-minus"></i></button>
                </div>`).join('');
        }

        async function giderEkle() {
            const g = { ad: document.getElementById('gid-ad').value, tutar: parseFloat(document.getElementById('gid-tutar').value) };
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(g) });
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            const data = await res.json();
            totalGid = 0;
            document.getElementById('gider-list').innerHTML = data.map(i => {
                totalGid += i.tutar;
                return `
                <div class="bg-white p-6 rounded-[2rem] border-l-[10px] border-red-500 shadow-sm flex justify-between items-center">
                    <b class="uppercase text-slate-800">${i.ad}</b>
                    <div class="text-right">
                        <div class="font-black text-red-500 text-xl">₺${i.tutar.toLocaleString()}</div>
                        <button onclick="sil('${i._id}','expenses')" class="text-[10px] text-slate-300 font-bold hover:text-red-500">KAYDI SİL</button>
                    </div>
                </div>`;
            }).join('');
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Kayıt tamamen silinecek, onaylıyor musun usta?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); else if(col==='customers') yukleCari(); else yukleGider();
            }
        }

        function openFinance() {
            document.getElementById('finance-modal').classList.remove('hidden');
            document.getElementById('fin-stok').innerText = '₺' + totalVal.toLocaleString();
            document.getElementById('fin-gider').innerText = '₺' + totalGid.toLocaleString();
        }
        function closeFinance() { document.getElementById('finance-modal').classList.add('hidden'); }

        function sendDailyReport() {
            let body = "ÖZCAN OTO GÜN SONU\n\n";
            currentProducts.forEach(p => { body += `${p.name} | Stok: ${p.stock}\n`; });
            body += `\nToplam Mal Değeri: ₺${totalVal.toLocaleString()}`;
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Rapor&body=${encodeURIComponent(body)}`;
        }

        if(localStorage.getItem('session_pro')) {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
            yukleStok();
        }
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
    # SIFIRIN ALTINA DÜŞMESİNİ ENGELLER AMA ÜRÜNÜ SİLMEZ
    product = db.products.find_one({"_id": ObjectId(id)})
    if change == -1 and product['stock'] <= 0:
        return jsonify({"ok": False, "msg": "Stok zaten sıfır!"})
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
