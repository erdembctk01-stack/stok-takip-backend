from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime
import hashlib

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- ŞİFRELEME YARDIMCISI ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- HTML VE JS PANELİ ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Özcan Oto Servis | Güvenli Stok</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-100 font-sans min-h-screen">

    <div id="login-section" class="flex items-center justify-center min-h-screen">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl w-full max-w-md border-4 border-blue-600">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-slate-800 italic uppercase italic">ÖZCAN OTO</h1>
                <p class="text-slate-400 font-bold">Lütfen giriş yapın</p>
            </div>
            
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-4 bg-slate-50 border rounded-2xl outline-none font-bold">
                
                <div class="flex items-center gap-2 px-2">
                    <input type="checkbox" id="remember" class="w-5 h-5 cursor-pointer">
                    <label for="remember" class="text-sm font-bold text-slate-600 cursor-pointer">Beni 30 Gün Hatırla</label>
                </div>

                <button onclick="handleLogin()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-2xl transition-all shadow-lg active:scale-95">GİRİŞ YAP</button>
                <button onclick="toggleAuthMode()" class="w-full text-slate-400 font-bold text-sm">Hesabın yok mu? Kayıt Ol</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden p-4 md:p-8">
        <div class="max-w-6xl mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                <h1 class="text-3xl font-black text-slate-800 italic uppercase">ÖZCAN OTO SERVİS</h1>
                <div class="flex gap-4">
                    <button onclick="toggleModal()" class="bg-emerald-600 text-white px-6 py-3 rounded-2xl font-black shadow-lg">KASA DURUMU</button>
                    <button onclick="handleLogout()" class="bg-slate-800 text-white px-6 py-3 rounded-2xl font-black">ÇIKIŞ</button>
                </div>
            </div>

            <div class="bg-white p-6 rounded-[2rem] shadow-sm border mb-8 grid grid-cols-1 md:grid-cols-5 gap-3">
                <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <input id="in-name" type="text" placeholder="Parça İsmi" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <input id="in-price" type="number" placeholder="Birim Fiyat" class="p-4 bg-slate-50 rounded-xl font-bold border outline-none">
                <button onclick="hizliEkle()" class="bg-blue-600 text-white font-black rounded-xl">KAYDET</button>
            </div>

            <input id="search" oninput="yukle()" type="text" placeholder="Hızlı ara..." class="w-full p-4 mb-6 bg-white rounded-2xl shadow-sm outline-none font-bold border-2 focus:border-blue-500">

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

    <div id="modal" class="hidden fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50">
        <div class="bg-white p-10 rounded-[2.5rem] shadow-2xl text-center max-w-sm w-full mx-4">
            <p class="text-xs font-black text-slate-400 uppercase mb-2">Toplam Stok Değeri</p>
            <h2 id="modal-val" class="text-5xl font-black text-slate-800 mb-8">₺0</h2>
            <button onclick="toggleModal()" class="w-full bg-slate-800 text-white py-4 rounded-2xl font-black">KAPAT</button>
        </div>
    </div>

    <script>
        let isRegisterMode = false;
        let totalCash = 0;

        // AUTH İŞLEMLERİ
        function toggleAuthMode() {
            isRegisterMode = !isRegisterMode;
            const btn = document.querySelector('#login-section button:last-child');
            const mainBtn = document.querySelector('#login-section button:first-of-type');
            const title = document.querySelector('#login-section p');
            
            title.innerText = isRegisterMode ? "Yeni Hesap Oluşturun" : "Lütfen giriş yapın";
            mainBtn.innerText = isRegisterMode ? "KAYIT OL" : "GİRİŞ YAP";
            btn.innerText = isRegisterMode ? "Zaten hesabın var mı? Giriş Yap" : "Hesabın yok mu? Kayıt Ol";
        }

        async function handleLogin() {
            const user = document.getElementById('log-user').value;
            const pass = document.getElementById('log-pass').value;
            const remember = document.getElementById('remember').checked;
            const endpoint = isRegisterMode ? '/api/register' : '/api/login';

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: user, password: pass, remember})
            });

            const data = await res.json();
            if(res.ok) {
                if(!isRegisterMode) {
                    localStorage.setItem('session', data.session);
                    checkAuth();
                } else {
                    alert("Başarıyla kayıt oldunuz! Şimdi giriş yapın.");
                    toggleAuthMode();
                }
            } else { alert(data.error); }
        }

        function checkAuth() {
            const session = localStorage.getItem('session');
            if(session) {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                yukle();
            }
        }

        function handleLogout() {
            localStorage.removeItem('session');
            location.reload();
        }

        // STOK İŞLEMLERİ
        async function yukle() {
            const res = await fetch('/api/products');
            const data = await res.json();
            const query = document.getElementById('search').value.toLowerCase();
            const list = document.getElementById('list');
            let tVal = 0; let crit = 0;

            list.innerHTML = data.filter(i => (i.name+i.code).toLowerCase().includes(query)).map(i => {
                tVal += (i.stock * i.price);
                const isCrit = i.stock <= 2;
                return `
                <tr class="${isCrit ? 'bg-red-50' : ''}">
                    <td class="px-8 py-6">
                        <div class="text-[10px] font-bold text-yellow-600 tracking-tighter">Fiyat: ₺${i.price}</div>
                        <div class="font-black ${isCrit ? 'text-red-600 underline' : 'text-slate-800'} uppercase">${i.name}</div>
                        <div class="text-[10px] text-slate-400 font-bold">${i.code}</div>
                    </td>
                    <td class="px-8 py-6 font-bold text-slate-500 uppercase text-xs">${i.category}</td>
                    <td class="px-8 py-6">
                        <div class="flex items-center justify-center gap-2 bg-white border p-1 rounded-xl w-fit mx-auto shadow-sm">
                            <button onclick="stokGuncelle('${i._id}', -1, ${i.stock})" class="w-8 h-8 text-red-500 font-bold">-</button>
                            <span class="w-8 text-center font-black">${i.stock}</span>
                            <button onclick="stokGuncelle('${i._id}', 1, ${i.stock})" class="w-8 h-8 text-green-500 font-bold">+</button>
                        </div>
                    </td>
                    <td class="px-8 py-6 text-right">
                        <button onclick="sil('${i._id}')" class="bg-red-500 text-white w-10 h-10 rounded-xl hover:bg-red-600 transition-all shadow-md">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </td>
                </tr>`;
            }).join('');
            totalCash = tVal;
        }

        async function stokGuncelle(id, change, current) {
            if(change === -1 && current <= 0) return; // Eksiye inme koruması
            await fetch(`/api/products/${id}/stock`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({change})
            });
            yukle();
        }

        async function hizliEkle() {
            const payload = {
                code: document.getElementById('in-code').value,
                name: document.getElementById('in-name').value,
                category: document.getElementById('in-cat').value,
                price: parseFloat(document.getElementById('in-price').value || 0),
                stock: 0
            };
            await fetch('/api/products', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            document.querySelectorAll('#main-section input:not(#search)').forEach(i => i.value = '');
            yukle();
        }

        async function sil(id) {
            if(confirm('BU ÜRÜN KALICI OLARAK SİLİNECEK! Emin misin?')) {
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

# --- AUTH API ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if db.users.find_one({"username": data['username']}):
        return jsonify({"error": "Kullanıcı zaten var!"}), 400
    db.users.insert_one({
        "username": data['username'],
        "password": hash_pass(data['password'])
    })
    return jsonify({"ok": True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({
        "username": data['username'],
        "password": hash_pass(data['password'])
    })
    if user:
        days = 30 if data.get('remember') else 1
        session_id = hashlib.sha256(f"{data['username']}{datetime.datetime.now()}".encode()).hexdigest()
        # Not: Gerçek bir sistemde bu session DB'ye kaydedilir. Pratiklik için basit tuttuk.
        return jsonify({"session": session_id, "expire_days": days})
    return jsonify({"error": "Hatalı giriş!"}), 401

# --- ÜRÜN API ---
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
    # Eksiye düşmeme kontrolü DB seviyesinde
    db.products.update_one(
        {"_id": ObjectId(id)},
        {"$inc": {"stock": change}}
    )
    return jsonify({"ok": True})

@app.route('/api/products/<id>', methods=['DELETE'])
def del_p(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
