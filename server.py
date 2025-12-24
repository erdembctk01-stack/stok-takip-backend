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

# --- PANEL TASARIMI ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO | Kurumsal Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .sidebar-link:hover { background-color: #334155; }
        .sidebar-active { background-color: #2563eb !important; color: white !important; }
        .page-content { display: none; }
        .active-section { display: block; }
        .glass { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="bg-slate-100 font-sans min-h-screen">

    <div id="login-section" class="flex items-center justify-center min-h-screen">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl w-full max-w-md border-4 border-blue-600">
            <div class="text-center mb-8">
                <i class="fas fa-user-shield text-5xl text-blue-600 mb-4"></i>
                <h1 class="text-3xl font-black text-slate-800 italic uppercase tracking-tighter">ÖZCAN OTO</h1>
                <p class="text-slate-400 font-bold uppercase text-xs tracking-widest mt-2">Yönetim Girişi</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold focus:border-blue-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold focus:border-blue-500">
                <button onclick="handleLogin()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-2xl transition-all shadow-lg active:scale-95 text-lg">SİSTEME GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <div class="w-72 bg-slate-800 text-white flex-shrink-0 flex flex-col border-r border-slate-700 shadow-2xl">
            <div class="p-8">
                <h2 class="text-2xl font-black italic text-blue-400 uppercase tracking-tighter">ÖZCAN OTO</h2>
                <div class="flex items-center gap-2 mt-2">
                    <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                    <p class="text-[10px] text-slate-400 font-bold tracking-widest uppercase">Sistem Aktif</p>
                </div>
            </div>
            
            <nav class="flex-1 px-4 space-y-2">
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-2xl font-bold transition-all text-left">
                    <i class="fas fa-layer-group text-lg"></i> Stok Yönetimi
                </button>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-slate-400 transition-all text-left">
                    <i class="fas fa-file-invoice-dollar text-lg"></i> Gider & Masraf
                </button>
                <div class="my-6 border-t border-slate-700/50"></div>
                <button onclick="openFinanceModal()" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-emerald-400 transition-all text-left bg-emerald-500/5">
                    <i class="fas fa-chart-line text-lg"></i> Finansal Durum
                </button>
                <button onclick="sendDailyReport()" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-2xl font-bold text-blue-400 transition-all text-left">
                    <i class="fas fa-envelope-open-text text-lg"></i> Gün Sonu Yedek
                </button>
            </nav>

            <div class="p-6 bg-slate-900/50">
                <button onclick="handleLogout()" class="w-full flex items-center justify-center gap-3 p-3 bg-red-500/10 text-red-500 rounded-xl font-bold hover:bg-red-500 hover:text-white transition-all">
                    <i class="fas fa-sign-out-alt"></i> ÇIKIŞ
                </button>
            </div>
        </div>

        <main class="flex-1 p-10 overflow-y-auto">
            
            <div id="page-stok" class="page-content active-section">
                <div class="flex justify-between items-end mb-8">
                    <div>
                        <h3 class="text-3xl font-black text-slate-800">Stok Listesi</h3>
                        <p class="text-slate-400 font-medium">Toplam <span id="item-count" class="text-blue-600 font-bold">0</span> farklı ürün kayıtlı.</p>
                    </div>
                    <div class="flex gap-4">
                         <input id="search" oninput="yukleStok()" type="text" placeholder="Hızlı ara..." class="p-3 bg-white rounded-xl border-2 border-slate-200 outline-none focus:border-blue-500 font-bold w-64 shadow-sm">
                    </div>
                </div>

                <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-200 mb-8">
                    <h4 class="text-xs font-black text-slate-400 uppercase mb-4 tracking-widest">Yeni Parça Ekle</h4>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <input id="in-code" type="text" placeholder="Kod" class="p-4 bg-slate-50 rounded-xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        <input id="in-name" type="text" placeholder="Parça İsmi" class="p-4 bg-slate-50 rounded-xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        <input id="in-price" type="number" placeholder="Birim Fiyat" class="p-4 bg-slate-50 rounded-xl font-bold border-none outline-none ring-2 ring-slate-100 focus:ring-blue-500">
                        <button onclick="hizliEkle()" class="bg-blue-600 text-white font-black rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all uppercase">Sisteme Kaydet</button>
                    </div>
                </div>

                <div class="bg-white rounded-[2rem] shadow-xl border border-slate-200 overflow-hidden">
                    <table class="w-full text-left border-collapse">
                        <thead class="bg-slate-50 text-slate-400 text-[11px] font-black uppercase tracking-widest border-b">
                            <tr>
                                <th class="px-10 py-6">Parça Detayları</th>
                                <th class="px-10 py-6 text-center">Stok Adedi</th>
                                <th class="px-10 py-6 text-right">İşlem</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8">Gider & Masraf Yönetimi</h3>
                <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-200 mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input id="gid-ad" type="text" placeholder="Gider Kalemi (Kira, Fatura vb.)" class="p-4 bg-slate-50 rounded-xl font-bold outline-none ring-2 ring-slate-100 focus:ring-red-500">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="p-4 bg-slate-50 rounded-xl font-bold outline-none ring-2 ring-slate-100 focus:ring-red-500">
                    <button onclick="giderEkle()" class="bg-red-500 text-white font-black rounded-xl hover:bg-red-600 transition-all uppercase">Gider Kaydet</button>
                </div>
                <div id="gider-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
            </div>

        </main>
    </div>

    <div id="finance-modal" class="hidden fixed inset-0 z-[100] bg-slate-900/80 flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-xl rounded-[3rem] shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
            <div class="bg-slate-800 p-10 text-white text-center">
                <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-university text-2xl"></i>
                </div>
                <h2 class="text-2xl font-black uppercase italic tracking-tighter">Finansal Özet Raporu</h2>
                <p class="text-slate-400 text-xs font-bold mt-1 uppercase tracking-widest">Özcan Oto Servis | Güncel Durum</p>
            </div>
            <div class="p-10 space-y-6">
                <div class="flex justify-between items-center p-6 bg-slate-50 rounded-2xl border-2 border-slate-100">
                    <span class="font-bold text-slate-500 uppercase text-xs">Toplam Stok Değeri</span>
                    <span id="fin-stok-val" class="text-2xl font-black text-emerald-600">₺0</span>
                </div>
                <div class="flex justify-between items-center p-6 bg-slate-50 rounded-2xl border-2 border-slate-100">
                    <span class="font-bold text-slate-500 uppercase text-xs">Toplam Giderler</span>
                    <span id="fin-gider-val" class="text-2xl font-black text-red-500">₺0</span>
                </div>
                <div class="flex justify-between items-center p-6 bg-blue-600 rounded-2xl shadow-xl shadow-blue-200">
                    <span class="font-bold text-white uppercase text-xs">Net Özsermaye</span>
                    <span id="fin-net-val" class="text-2xl font-black text-white">₺0</span>
                </div>
                <button onclick="closeFinanceModal()" class="w-full py-5 bg-slate-800 text-white font-black rounded-2xl uppercase text-sm tracking-widest mt-4">Pencereyi Kapat</button>
            </div>
        </div>
    </div>

    <script>
        let currentProducts = [];
        let totalStokVal = 0;
        let totalGiderVal = 0;

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            if(pageId === 'stok') yukleStok();
            if(pageId === 'gider') yukleGider();
        }

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                yukleStok();
            } else { alert("Hatalı Giriş!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        async function yukleStok() {
            const res = await fetch('/api/products');
            currentProducts = await res.json();
            const query = document.getElementById('search').value.toLowerCase();
            let tVal = 0;

            document.getElementById('stok-list').innerHTML = currentProducts
                .filter(i => (i.name+i.code).toLowerCase().includes(query))
                .map(i => {
                    const isCrit = i.stock <= 2;
                    tVal += (i.stock * i.price);
                    return `
                    <tr class="${isCrit ? 'bg-red-50/50' : 'hover:bg-slate-50/50'} transition-all">
                        <td class="px-10 py-6">
                            <div class="text-[10px] font-black text-white bg-emerald-500 w-fit px-2 rounded mb-1 uppercase">₺${i.price.toLocaleString()}</div>
                            <div class="font-black ${isCrit ? 'text-red-600' : 'text-slate-800'} uppercase text-lg leading-tight">${i.name}</div>
                            <div class="text-[10px] text-slate-400 font-bold tracking-widest mt-1">${i.code}</div>
                        </td>
                        <td class="px-10 py-6 text-center">
                            <div class="flex items-center justify-center gap-4 bg-white border border-slate-200 p-2 rounded-2xl w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('${i._id}', -1, ${i.stock})" class="w-10 h-10 text-red-500 font-black hover:bg-red-50 rounded-xl transition-all">-</button>
                                <span class="w-10 text-center font-black text-xl">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}', 1, ${i.stock})" class="w-10 h-10 text-emerald-500 font-black hover:bg-emerald-50 rounded-xl transition-all">+</button>
                            </div>
                        </td>
                        <td class="px-10 py-6 text-right">
                            <button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500 p-3 transition-all"><i class="fas fa-trash-alt text-xl"></i></button>
                        </td>
                    </tr>`;
                }).join('');
            
            totalStokVal = tVal;
            document.getElementById('item-count').innerText = currentProducts.length;
        }

        async function hizliEkle() {
            const p = { code: document.getElementById('in-code').value || 'KODSUZ', name: document.getElementById('in-name').value, price: parseFloat(document.getElementById('in-price').value || 0), stock: 0 };
            if(!p.name) return alert("İsim Boş Olamaz!");
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            document.getElementById('in-name').value = ''; document.getElementById('in-price').value = '';
            yukleStok();
        }

        async function giderEkle() {
            const g = { ad: document.getElementById('gid-ad').value, tutar: parseFloat(document.getElementById('gid-tutar').value) };
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(g) });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            const data = await res.json();
            let gVal = 0;
            document.getElementById('gider-list').innerHTML = data.map(i => {
                gVal += i.tutar;
                return `
                <div class="bg-white p-6 rounded-3xl border-l-8 border-red-500 shadow-sm flex justify-between items-center">
                    <div><b class="uppercase block text-slate-800">${i.ad}</b><small class="text-slate-400 font-bold">Masraf Kaydı</small></div>
                    <div class="text-right">
                        <div class="font-black text-red-500 text-xl">₺${i.tutar.toLocaleString()}</div>
                        <button onclick="sil('${i._id}','expenses')" class="text-[10px] text-slate-300 font-bold hover:text-red-500">SİL</button>
                    </div>
                </div>`;
            }).join('');
            totalGiderVal = gVal;
        }

        async function stokGuncelle(id, change, current) {
            if(change === -1 && current <= 0) return;
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Kayıt silinecek, onaylıyor musun usta?')) { 
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); 
                if(col==='products') yukleStok(); else yukleGider(); 
            }
        }

        function openFinanceModal() {
            document.getElementById('finance-modal').classList.remove('hidden');
            document.getElementById('fin-stok-val').innerText = '₺' + totalStokVal.toLocaleString();
            document.getElementById('fin-gider-val').innerText = '₺' + totalGiderVal.toLocaleString();
            document.getElementById('fin-net-val').innerText = '₺' + (totalStokVal - totalGiderVal).toLocaleString();
        }

        function closeFinanceModal() { document.getElementById('finance-modal').classList.add('hidden'); }

        function sendDailyReport() {
            let body = "ÖZCAN OTO GÜN SONU YEDEK\n\n";
            currentProducts.forEach(p => { body += `${p.name} [${p.code}] - Stok: ${p.stock}\n`; });
            body += `\nTOPLAM STOK DEĞERİ: ₺${totalStokVal.toLocaleString()}`;
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Rapor&body=${encodeURIComponent(body)}`;
        }

        if(localStorage.getItem('session')) {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
            yukleStok(); yukleGider();
        }
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
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": request.json['change']}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
