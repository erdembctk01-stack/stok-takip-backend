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
    <title>Özcan Oto Servis | Stok Takip</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-100 font-sans min-h-screen">

    <div id="login-section" class="flex items-center justify-center min-h-screen">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl w-full max-w-md border-4 border-blue-600">
            <div class="text-center mb-8">
                <i class="fas fa-user-shield text-5xl text-blue-600 mb-4"></i>
                <h1 class="text-3xl font-black text-slate-800 italic uppercase">ÖZCAN OTO</h1>
                <p class="text-slate-400 font-bold uppercase text-xs tracking-widest mt-2">Yönetim Girişi</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold focus:border-blue-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold focus:border-blue-500">
                <div class="flex items-center gap-2 px-2">
                    <input type="checkbox" id="remember" class="w-5 h-5 cursor-pointer">
                    <label for="remember" class="text-sm font-bold text-slate-600 cursor-pointer">30 Gün Hatırla</label>
                </div>
                <button onclick="handleLogin()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-2xl transition-all shadow-lg active:scale-95 text-lg">SİSTEME GİR</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden p-4 md:p-8">
        <div class="max-w-6xl mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                <div>
                    <h1 class="text-3xl font-black text-slate-800 italic uppercase">ÖZCAN OTO SERVİS</h1>
                    <div class="bg-red-500 text-white text-[10px] font-black px-3 py-1 rounded-full w-fit uppercase mt-1">
                        Kritik Parça Sayısı: <span id="stat-crit-count">0</span>
                    </div>
                </div>
                <div class="flex gap-3">
                    <button onclick="toggleModal()" class="bg-blue-600 text-white px-6 py-3 rounded-2xl font-black shadow-md hover:bg-blue-700 transition-all">KASA DURUMU</button>
                    <button onclick="sendDailyReport()" class="bg-emerald-600 text-white px-6 py-3 rounded-2xl font-black shadow-md hover:bg-emerald-700 transition-all">
                        <i class="fas fa-envelope mr-2"></i>GÜN SONU YEDEK
                    </button>
                    <button onclick="handleLogout()" class="bg-slate-800 text-white px-4 py-3 rounded-2xl font-black">
                        <i class="fas fa-sign-out-alt"></i>
                    </button>
                </div>
            </div>

            <div class="bg-white p-6 rounded-[2rem] shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-5 gap-3">
                <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <input id="in-name" type="text" placeholder="Parça İsmi" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <button onclick="hizliEkle()" class="bg-blue-600 text-white font-black rounded-xl hover:bg-blue-700 transition-all uppercase text-sm">Parçayı Ekle</button>
            </div>

            <div class="relative mb-6">
                <i class="fas fa-search absolute left-5 top-5 text-slate-400"></i>
                <input id="search" oninput="yukle()" type="text" placeholder="Parça adı veya koduyla arama..." class="w-full pl-14 pr-6 py-4 bg-white rounded-2xl shadow-sm outline-none font-bold border-2 focus:border-blue-500">
            </div>

            <div class="bg-white rounded-[2rem] shadow-sm border overflow-hidden">
                <table class="w-full text-left">
                    <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase">
                        <tr><th class="px-8 py-6">Parça Detayı</th><th class="px-8 py-6">Kategori</th><th class="px-8 py-6 text-center">Stok</th><th class="px-8 py-6 text-right">Sil</th></tr>
                    </thead>
                    <tbody id="list" class="divide-y"></tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="modal" class="hidden fixed inset-0 bg-slate-900/60 flex items-center justify-center z-50 p-4">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl text-center max-w-sm w-full border-b-8 border-emerald-500">
            <i class="fas fa-money-bill-wave text-5xl text-emerald-500 mb-4"></i>
            <p class="text-xs font-black text-slate-400 uppercase mb-2 tracking-widest">Depodaki Toplam Sermaye</p>
            <h2 id="modal-val" class="text-4xl font-black text-slate-800 mb-8 tracking-tighter">₺0</h2>
            <button onclick="toggleModal()" class="w-full bg-slate-800 text-white py-4 rounded-2xl font-black uppercase tracking-widest text-sm">Kapat</button>
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
                <tr class="${isCrit ? 'bg-red-50' : 'hover:bg-slate-50'} transition-all">
                    <td class="px-8 py-6">
                        <div class="text-[10px] font-black text-white bg-emerald-500 w-fit px-2 rounded mb-1 shadow-sm uppercase tracking-tighter">₺${i.price.toLocaleString()}</div>
                        <div class="font-black ${isCrit ? 'text-red-600 underline decoration-2' : 'text-slate-800'} uppercase text-lg leading-tight">${i.name}</div>
                        <div class="text-[10px] text-slate-400 font-bold tracking-widest mt-1">${i.code}</div>
                    </td>
                    <td class="px-8 py-6 font-bold text-slate-500 uppercase text-xs">${i.category}</td>
                    <td class="px-8 py-6 text-center">
                        <div class="flex items-center justify-center gap-2 bg-white border p-1 rounded-xl w-fit mx-auto shadow-sm">
                            <button onclick="stokGuncelle('${i._id}', -1, ${i.stock})" class="w-8 h-8 text-red-500 font-bold hover:bg-red-50 rounded-lg">-</button>
                            <span class="w-8 text-center font-black">${i.stock}</span>
                            <button onclick="stokGuncelle('${i._id}', 1, ${i.stock})" class="w-8 h-8 text-green-500 font-bold hover:bg-green-50 rounded-lg">+</button>
                        </div>
                    </td>
                    <td class="px-8 py-6 text-right">
                        <button onclick="sil('${i._id}')" class="bg-red-600 text-white w-10 h-10 rounded-xl shadow-lg hover:scale-110 transition-all">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </td>
                </tr>`;
            }).join('');
            totalCash = tVal;
            document.getElementById('stat-crit-count').innerText = critCount;
        }

        function sendDailyReport() {
            let body = "ÖZCAN OTO SERVİS - GÜN SONU STOK YEDEK\n";
            body += "===========================================\n\n";
            
            currentProducts.forEach(p => {
                body += `PARÇA ADI : ${p.name.toUpperCase()}\n`;
                body += `PARÇA KODU: ${p.code}\n`;
                body += `STOK ADEDİ: ${p.stock}\n`;
                body += `BİRİM FİYAT: ₺${p.price.toLocaleString()}\n`;
                body += "-------------------------------------------\n";
            });
            
            body += `\nTOPLAM DEPO SERMAYESİ: ₺${totalCash.toLocaleString()}`;
            
            const subject = "Ozcan Oto Gun Sonu Raporu";
            const mailto = `mailto:adanaozcanotoyedekparca@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
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
            if(!p.name) return alert("Parça İsmi Girmelisiniz!");
            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(p)
            });
            document.querySelectorAll('#main-section input:not(#search)').forEach(i => i.value = '');
            yukle();
        }

        async function sil(id) {
            if(confirm('BU PARÇA SİSTEMDEN KALICI OLARAK SİLİNECEK! Emin misiniz?')) {
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
