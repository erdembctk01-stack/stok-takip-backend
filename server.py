from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>ÖZCAN OTO PRO</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .sidebar { background: #0f172a; width: 260px; height: 100vh; position: fixed; color: white; }
        .sidebar-link { padding: 1rem 2rem; display: block; cursor: pointer; color: #94a3b8; font-weight: bold; font-size: 13px; }
        .sidebar-link:hover { background: #1e293b; color: white; }
        .active-link { background: #f97316 !important; color: white !important; }
        .main-content { margin-left: 260px; padding: 3rem; }
        .page { display: none; }
        .active-page { display: block; }
        .card { background: white; border: 1px solid #e2e8f0; border-radius: 1rem; padding: 1.5rem; }
    </style>
</head>
<body>

    <div id="login-screen" class="fixed inset-0 z-[1000] bg-[#0f172a] flex items-center justify-center">
        <div class="bg-white p-10 rounded-3xl w-96">
            <h2 class="text-2xl font-black text-center mb-6">ÖZCAN OTO GİRİŞ</h2>
            <input id="user" type="text" placeholder="Kullanıcı" class="w-full p-3 mb-3 border rounded-xl">
            <input id="pass" type="password" placeholder="Şifre" class="w-full p-3 mb-6 border rounded-xl">
            <button onclick="login()" class="w-full bg-slate-900 text-white p-3 rounded-xl font-bold">GİRİŞ</button>
        </div>
    </div>

    <div id="app-screen" class="hidden">
        <div class="sidebar">
            <div class="p-8 border-b border-slate-800 mb-4"><h1 class="text-xl font-black italic">ÖZCAN OTO</h1></div>
            <div onclick="showPage('dash')" id="l-dash" class="sidebar-link active-link">DASHBOARD</div>
            <div onclick="showPage('stok')" id="l-stok" class="sidebar-link">ENVANTER</div>
            <div onclick="showPage('satis')" id="l-satis" class="sidebar-link">SATIŞ YAP</div>
            <div onclick="showPage('cari')" id="l-cari" class="sidebar-link">CARİLER</div>
            <div onclick="showPage('gider')" id="l-gider" class="sidebar-link">GİDERLER</div>
            <div onclick="logout()" class="sidebar-link mt-10 text-red-500">ÇIKIŞ</div>
        </div>

        <div class="main-content">
            <div id="p-dash" class="page active-page">
                <h2 class="text-2xl font-black mb-8 italic">GENEL DURUM</h2>
                <div class="grid grid-cols-3 gap-6 mb-8">
                    <div class="card border-l-4 border-emerald-500">
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Günlük Kazanç</p>
                        <h3 id="d-kazanc" class="text-2xl font-black text-emerald-600 mt-1">₺0</h3>
                    </div>
                    <div class="card border-l-4 border-red-500">
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Günlük Gider</p>
                        <h3 id="d-gider" class="text-2xl font-black text-red-600 mt-1">₺0</h3>
                    </div>
                    <div class="card border-l-4 border-blue-600">
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Depo Değeri</p>
                        <div class="flex items-center justify-between mt-1">
                            <h3 id="d-depo" class="text-2xl font-black text-blue-700">****</h3>
                            <button onclick="hesaplaDepo()" class="text-[10px] bg-blue-50 text-blue-600 px-2 py-1 rounded font-bold border border-blue-100">HESAPLA</button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="p-stok" class="page">
                <div class="flex justify-between mb-4"><h3 class="font-black">STOK LİSTESİ</h3><input id="s-ara" oninput="yukleStok()" placeholder="Ara..." class="p-2 border rounded-lg text-sm"></div>
                <div class="card mb-6 grid grid-cols-5 gap-2">
                    <input id="i-c" placeholder="Kod" class="p-2 border rounded">
                    <input id="i-n" placeholder="Parça" class="p-2 border rounded">
                    <input id="i-k" placeholder="Kat" class="p-2 border rounded">
                    <input id="i-f" type="number" placeholder="Fiyat" class="p-2 border rounded">
                    <input id="i-s" type="number" placeholder="Adet" class="p-2 border rounded">
                    <button onclick="stokEkle()" class="col-span-5 bg-slate-900 text-white p-2 rounded font-bold">EKLE</button>
                </div>
                <div class="bg-white rounded-xl border overflow-hidden">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-slate-50 text-slate-400 font-bold uppercase text-[10px]">
                            <tr><th class="p-4">Parça</th><th class="p-4 text-center">Stok</th><th class="p-4 text-right">Fiyat</th><th class="p-4"></th></tr>
                        </thead>
                        <tbody id="stok-table" class="divide-y"></tbody>
                    </table>
                </div>
            </div>

            <div id="p-satis" class="page">
                <h3 class="font-black mb-4">SATIŞ YAP</h3>
                <div class="card space-y-3">
                    <input id="f-m" placeholder="Müşteri Ad Soyad" class="w-full p-3 border rounded">
                    <input id="f-t" placeholder="Telefon" class="w-full p-3 border rounded">
                    <select id="f-p" class="w-full p-3 border rounded"></select>
                    <input id="f-a" type="number" placeholder="Adet" class="w-full p-3 border rounded">
                    <button onclick="satisYap()" class="w-full bg-orange-600 text-white p-4 rounded-xl font-bold">SATIŞI TAMAMLA</button>
                </div>
            </div>

            <div id="p-cari" class="page">
                <h3 class="font-black mb-4">CARİLER</h3>
                <div id="cari-list" class="grid grid-cols-2 gap-4"></div>
            </div>

            <div id="p-gider" class="page">
                <h3 class="font-black mb-4 text-red-600">Harcama Ekle</h3>
                <div class="card flex gap-2 mb-4">
                    <input id="g-n" placeholder="Açıklama" class="flex-1 p-3 border rounded">
                    <input id="g-t" type="number" placeholder="Tutar" class="w-32 p-3 border rounded">
                    <button onclick="giderEkle()" class="bg-red-600 text-white px-6 rounded font-bold">EKLE</button>
                </div>
                <div id="gider-list" class="space-y-2"></div>
            </div>
        </div>
    </div>

    <script>
        function login() {
            if(document.getElementById('user').value === "ozcanoto" && document.getElementById('pass').value === "eren9013") {
                document.getElementById('login-screen').classList.add('hidden');
                document.getElementById('app-screen').classList.remove('hidden');
                showPage('dash');
            }
        }
        function logout() { location.reload(); }

        function showPage(p) {
            document.querySelectorAll('.page').forEach(x => x.classList.remove('active-page'));
            document.querySelectorAll('.sidebar-link').forEach(x => x.classList.remove('active-link'));
            document.getElementById('p-'+p).classList.add('active-page');
            document.getElementById('l-'+p).classList.add('active-link');
            if(p === 'dash') yukleDash();
            if(p === 'stok') yukleStok();
            if(p === 'satis') yukleSatislar();
            if(p === 'cari') yukleCari();
            if(p === 'gider') yukleGider();
        }

        async function yukleDash() {
            const [pRes, gRes, fRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/invoices')]);
            const prods = await pRes.json(); const exps = await gRes.json(); const invs = await fRes.json();
            const bugun = new Date().toLocaleDateString('tr-TR');

            let gK = 0; invs.forEach(i => {
                if(i.tarih.includes(bugun)) {
                    const p = prods.find(x => x._id === i.parca_id || x.name === i.parca_ad);
                    if(p) gK += (Number(i.adet) * Number(p.price));
                }
            });
            let gG = 0; exps.forEach(e => { if(e.tarih === bugun) gG += Number(e.tutar); });

            document.getElementById('d-kazanc').innerText = `₺${gK.toLocaleString('tr-TR')}`;
            document.getElementById('d-gider').innerText = `₺${gG.toLocaleString('tr-TR')}`;
            document.getElementById('d-depo').innerText = "****";
        }

        async function hesaplaDepo() {
            const res = await fetch('/api/products'); const prods = await res.json();
            let total = 0; prods.forEach(p => total += (Number(p.stock) * Number(p.price)));
            document.getElementById('d-depo').innerText = `₺${total.toLocaleString('tr-TR')}`;
        }

        async function yukleStok() {
            const res = await fetch('/api/products'); const data = await res.json();
            const q = document.getElementById('s-ara').value.toLowerCase();
            document.getElementById('stok-table').innerHTML = data.filter(i => (i.name+i.code).toLowerCase().includes(q)).reverse().map(i => `
                <tr class="${i.stock <= 2 ? 'bg-red-50' : ''}">
                    <td class="p-4 font-bold text-xs uppercase">${i.name} <br><span class="text-[9px] text-slate-400">${i.code}</span></td>
                    <td class="p-4 text-center font-bold">${i.stock}</td>
                    <td class="p-4 text-right font-bold">₺${i.price}</td>
                    <td class="p-4 text-right"><button onclick="sil('${i._id}','products')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash"></i></button></td>
                </tr>`).join('');
        }

        async function stokEkle() {
            const obj = { code: document.getElementById('i-c').value, name: document.getElementById('i-n').value, price: document.getElementById('i-f').value, stock: document.getElementById('i-s').value, tarih: new Date().toLocaleDateString('tr-TR') };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(obj) });
            yukleStok();
        }

        async function yukleSatislar() {
            const res = await fetch('/api/products'); const data = await res.json();
            document.getElementById('f-p').innerHTML = data.map(i => `<option value="${i._id}">${i.name} (Stok: ${i.stock})</option>`).join('');
        }

        async function satisYap() {
            const obj = { ad: document.getElementById('f-m').value, tel: document.getElementById('f-t').value, parcaId: document.getElementById('f-p').value, adet: parseInt(document.getElementById('f-a').value), tarih: new Date().toLocaleString('tr-TR') };
            await fetch('/api/fatura-kes', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(obj) });
            alert("SATIŞ TAMAM"); showPage('dash');
        }

        async function yukleCari() {
            const res = await fetch('/api/customers'); const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `<div class="card flex justify-between"><div><b class="text-xs uppercase">${i.ad}</b><p class="text-[10px]">${i.tel}</p></div><button onclick="sil('${i._id}','customers')" class="text-slate-300 hover:text-red-500"><i class="fas fa-trash"></i></button></div>`).join('');
        }

        async function giderEkle() {
            const obj = { ad: document.getElementById('g-n').value, tutar: document.getElementById('g-t').value, tarih: new Date().toLocaleDateString('tr-TR') };
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(obj) });
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses'); const data = await res.json();
            document.getElementById('gider-list').innerHTML = data.map(i => `<div class="card flex justify-between font-bold text-xs"><span>${i.ad} (${i.tarih})</span><span class="text-red-600">₺${i.tutar}</span></div>`).join('');
        }

        async function sil(id, col) { if(confirm('SİLİNSİN Mİ?')) { await fetch(`/api/${col}/${id}`, {method: 'DELETE'}); showPage(col === 'products' ? 'stok' : 'cari'); } }
    </script>
</body>
</html>
"""

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
    data = request.json
    parca = db.products.find_one({"_id": ObjectId(data['parcaId'])})
    db.products.update_one({"_id": ObjectId(data['parcaId'])}, {"$inc": {"stock": -data['adet']}})
    db.invoices.insert_one({"ad": data['ad'], "tel": data['tel'], "parca_id": data['parcaId'], "parca_ad": parca['name'], "adet": data['adet'], "tarih": data['tarih']})
    if not db.customers.find_one({"ad": data['ad']}):
        db.customers.insert_one({"ad": data['ad'], "tel": data['tel'], "tarih": data['tarih'].split(' ')[0]})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
