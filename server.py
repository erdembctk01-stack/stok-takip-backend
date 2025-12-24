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

# --- PANEL TASARIMI (Paraşüt Tarzı Modern Arayüz) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Özcan Oto | Yönetim Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .sidebar-link:hover { background-color: #334155; }
        .active-link { background-color: #2563eb; color: white; }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-900">

    <div id="login-section" class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900">
        <div class="bg-white p-10 rounded-3xl shadow-2xl w-full max-w-md border-t-8 border-blue-600">
            <div class="text-center mb-8">
                <div class="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-tools text-3xl text-blue-600"></i>
                </div>
                <h1 class="text-2xl font-bold text-slate-800 uppercase tracking-tighter">Özcan Oto Servis</h1>
                <p class="text-slate-400 text-sm mt-1 font-medium">Lütfen kimliğinizi doğrulayın</p>
            </div>
            <div class="space-y-4">
                <div class="relative">
                    <i class="fas fa-user absolute left-4 top-4 text-slate-400"></i>
                    <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full pl-12 pr-4 py-4 bg-slate-50 border rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold transition-all">
                </div>
                <div class="relative">
                    <i class="fas fa-lock absolute left-4 top-4 text-slate-400"></i>
                    <input id="log-pass" type="password" placeholder="Şifre" class="w-full pl-12 pr-4 py-4 bg-slate-50 border rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 font-bold transition-all">
                </div>
                <div class="flex items-center gap-2 px-1">
                    <input type="checkbox" id="remember" class="w-5 h-5 accent-blue-600 cursor-pointer">
                    <label for="remember" class="text-sm font-semibold text-slate-600 cursor-pointer">Beni 30 Gün Hatırla</label>
                </div>
                <button onclick="handleLogin()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-2xl shadow-lg transition-all active:scale-95">PANEL'E GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <div class="w-64 bg-slate-800 text-white flex-shrink-0 hidden md:flex flex-col border-r border-slate-700">
            <div class="p-6">
                <h2 class="text-xl font-black italic tracking-tighter text-blue-400">ÖZCAN OTO</h2>
                <p class="text-[10px] text-slate-400 font-bold tracking-widest mt-1">GÜNCEL STOK SİSTEMİ</p>
            </div>
            
            <nav class="flex-1 px-4 space-y-2">
                <a href="#" class="active-link flex items-center gap-3 p-3 rounded-xl font-bold transition-all">
                    <i class="fas fa-boxes w-6"></i> Stok Listesi
                </a>
                <a href="javascript:void(0)" onclick="toggleModal()" class="sidebar-link flex items-center gap-3 p-3 rounded-xl font-bold text-slate-300 transition-all">
                    <i class="fas fa-wallet w-6"></i> Kasa Durumu
                </a>
                <a href="javascript:void(0)" onclick="sendDailyReport()" class="sidebar-link flex items-center gap-3 p-3 rounded-xl font-bold text-slate-300 transition-all">
                    <i class="fas fa-share-square w-6"></i> Gün Sonu Yedek
                </a>
                <div class="pt-6 border-t border-slate-700 mt-6">
                    <p class="text-[10px] text-slate-500 font-bold uppercase mb-4 px-3">Yönetim</p>
                    <a href="javascript:void(0)" onclick="handleLogout()" class="sidebar-link flex items-center gap-3 p-3 rounded-xl font-bold text-red-400 transition-all">
                        <i class="fas fa-power-off w-6"></i> Güvenli Çıkış
                    </a>
                </div>
            </nav>
            
            <div class="p-4 bg-slate-900/50">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center text-xs font-bold uppercase">OO</div>
                    <div class="text-xs">
                        <p class="font-bold">Özcan Usta</p>
                        <p class="text-slate-500">Yönetici</p>
                    </div>
                </div>
            </div>
        </div>

        <main class="flex-1 p-6 md:p-10 overflow-y-auto">
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                    <p class="text-xs font-bold text-slate-400 uppercase">Toplam Stok Değeri</p>
                    <h3 id="stat-total-cash" class="text-2xl font-black text-slate-800 mt-1">₺0</h3>
                </div>
                <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                    <p class="text-xs font-bold text-slate-400 uppercase">Kritik Stok Uyarısı</p>
                    <h3 id="stat-crit-count" class="text-2xl font-black text-red-500 mt-1">0</h3>
                </div>
                <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                    <p class="text-xs font-bold text-slate-400 uppercase">Toplam Parça Çeşidi</p>
                    <h3 id="stat-item-count" class="text-2xl font-black text-blue-600 mt-1">0</h3>
                </div>
            </div>

            <div class="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mb-10">
                <h4 class="text-sm font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <i class="fas fa-plus-circle text-blue-500"></i> Yeni Parça Kaydı
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-2xl border-none outline-none focus:ring-2 focus:ring-blue-500 font-bold">
                    <input id="in-name" type="text" placeholder="Parça İsmi" class="p-4 bg-slate-50 rounded-2xl border-none outline-none focus:ring-2 focus:ring-blue-500 font-bold">
                    <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-2xl border-none outline-none focus:ring-2 focus:ring-blue-500 font-bold">
                    <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-2xl border-none outline-none focus:ring-2 focus:ring-blue-500 font-bold">
                    <button onclick="hizliEkle()" class="md:col-span-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-2xl shadow-md transition-all">SİSTEME KAYDET</button>
                </div>
            </div>

            <div class="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="p-6 border-b border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
                    <h4 class="font-bold text-slate-800">Parça Envanteri</h4>
                    <div class="relative w-full md:w-80">
                        <i class="fas fa-search absolute left-4 top-4 text-slate-400"></i>
                        <input id="search" oninput="yukle()" type="text" placeholder="Ara..." class="w-full pl-12 pr-4 py-3 bg-slate-50 rounded-xl outline-none border-none focus:ring-2 focus:ring-blue-500 font-bold text-sm">
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50/50 text-slate-400 text-[10px] font-black uppercase">
                            <tr>
                                <th class="px-8 py-5">Ürün Bilgisi</th>
                                <th class="px-8 py-5">Kategori</th>
                                <th class="px-8 py-5 text-center">Stok Durumu</th>
                                <th class="px-8 py-5 text-right">Eylemler</th>
                            </tr>
                        </thead>
                        <tbody id="list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <div id="modal" class="hidden fixed inset-0 z-[110] bg-slate-900/80 flex items-center justify-center p-4">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl text-center max-w-sm w-full border-b-8 border-blue-600">
            <div class="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-coins text-3xl text-emerald-600"></i>
            </div>
            <p class="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Depodaki Toplam Sermaye</p>
            <h2 id="modal-val" class="text-4xl font-black text-slate-800 mb-8">₺0</h2>
            <button onclick="toggleModal()" class="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold uppercase text-sm tracking-widest transition-all hover:bg-slate-800">Pencereyi Kapat</button>
        </div>
    </div>

    <script>
        let currentProducts = [];
        let totalCash = 0;

        function handleLogin() {
            const user = document.getElementById('log-user').value;
            const pass = document.getElementById('log-pass').value;
            const remember = document.getElementById('remember').checked;

            if(user === "ozcanoto" && pass === "eren9013") {
                const expiry = remember ? 30 : 1;
                const now = new Date();
                now.setTime(now.getTime() + (expiry * 24 * 60 * 60 * 1000));
                localStorage.setItem('session', 'active_session');
                localStorage.setItem('expiry', now.getTime());
                checkAuth();
            } else {
                alert("Hatalı Giriş!");
            }
        }

        function checkAuth() {
            const session = localStorage.getItem('session');
            const expiry = localStorage.getItem('expiry');
            const now = new Date().getTime();
            if(session && expiry && now < expiry) {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                yukle();
            } else {
                handleLogout();
            }
        }

        function handleLogout() {
            localStorage.clear();
            document.getElementById('login-section').classList.remove('hidden');
            document.getElementById('main-section').classList.add('hidden');
        }

        async function yukle() {
            const res = await fetch('/api/products');
            currentProducts = await res.json();
            const query = document.getElementById('search').value.toLowerCase();
            const list = document.getElementById('list');
            let tVal = 0; let critCount = 0;

            list.innerHTML = currentProducts.filter(i => (i.name+i.code).toLowerCase().includes(query)).map(i => {
                const isCrit = i.stock <= 2;
                if(i.stock <= 10) critCount++;
                tVal += (i.stock * i.price);
                return `
                <tr class="${isCrit ? 'bg-red-50/50' : 'hover:bg-slate-50/80'} transition-all">
                    <td class="px-8 py-5">
                        <div class="text-[10px] font-black text-white bg-emerald-500 w-fit px-2 rounded mb-1 shadow-sm">₺${i.price.toLocaleString()}</div>
                        <div class="font-bold ${isCrit ? 'text-red-600' : 'text-slate-800'} uppercase text-sm">${i.name}</div>
                        <div class="text-[10px] text-slate-400 font-bold tracking-widest mt-0.5">${i.code}</div>
                    </td>
                    <td class="px-8 py-5 font-semibold text-slate-500 uppercase text-xs">${i.category}</td>
                    <td class="px-8 py-5 text-center">
                        <div class="flex items-center justify-center gap-3 bg-white border border-slate-200 p-1.5 rounded-xl w-fit mx-auto shadow-sm">
                            <button onclick="stokGuncelle('${i._id}', -1, ${i.stock})" class="w-8 h-8 flex items-center justify-center text-red-500 font-black hover:bg-red-50 rounded-lg transition-colors">-</button>
                            <span class="w-10 text-center font-black text-slate-800">${i.stock}</span>
                            <button onclick="stokGuncelle('${i._id}', 1, ${i.stock})" class="w-8 h-8 flex items-center justify-center text-emerald-500 font-black hover:bg-emerald-50 rounded-lg transition-colors">+</button>
                        </div>
                    </td>
                    <td class="px-8 py-5 text-right">
                        <button onclick="sil('${i._id}')" class="text-slate-300 hover:text-red-600 transition-colors px-3 py-2">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </td>
                </tr>`;
            }).join('');
            
            totalCash = tVal;
            document.getElementById('stat-total-cash').innerText = '₺' + totalCash.toLocaleString();
            document.getElementById('stat-crit-count').innerText = critCount;
            document.getElementById('stat-item-count').innerText = currentProducts.length;
        }

        function sendDailyReport() {
            let body = "ÖZCAN OTO SERVİS - GÜN SONU YEDEK\n\n";
            currentProducts.forEach(p => {
                body += `PARÇA: ${p.name.toUpperCase()} | KOD: ${p.code} | STOK: ${p.stock} | FİYAT: ₺${p.price.toLocaleString()}\n`;
            });
            body += `\nTOPLAM SERMAYE: ₺${totalCash.toLocaleString()}`;
            const mailto = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Gun Sonu Raporu&body=${encodeURIComponent(body)}`;
            window.location.href = mailto;
        }

        async function stokGuncelle(id, change, current) {
            if(change === -1 && current <= 0) return;
            await fetch(`/api/products/${id}/stock`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change})
            });
            yukle();
        }

        async function hizliEkle() {
            const p = {
                code: document.getElementById('in-code').value || 'KODSUZ',
                name: document.getElementById('in-name').value,
                category: document.getElementById('in-cat').value || 'DİĞER',
                price: parseFloat(document.getElementById('in-price').value || 0),
                stock: 0
            };
            if(!p.name) return alert("Parça İsmi Şart!");
            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(p)
            });
            document.querySelectorAll('#main-section input:not(#search)').forEach(i => i.value = '');
            yukle();
        }

        async function sil(id) {
            if(confirm('BU PARÇA TAMAMEN SİLİNSİN Mİ?')) {
                await fetch(`/api/products/${id}`, {method: 'DELETE'});
                yukle();
            }
        }

        function toggleModal() {
            document.getElementById('modal').classList.toggle('hidden');
            document.getElementById('modal-val').innerText = '₺' + totalCash.toLocaleString();
        }

        checkAuth();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PANEL)

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        items = list(db.products.find())
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    db.products.insert_one(request.json)
    return jsonify({"ok": True}), 201

@app.route('/api/products/<id>/stock', methods=['PUT'])
def update_stock(id):
    change = request.json.get('change', 0)
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

@app.route('/api/products/<id>', methods=['DELETE'])
def del_p(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
