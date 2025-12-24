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

# --- PANEL TASARIMI (TURUNCU & ULTRA DETAYLI) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO PRO | Kurumsal Kaynak Planlama</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .sidebar-link { transition: all 0.2s; color: #cbd5e1; }
        .sidebar-link:hover { background-color: #f97316; color: white; }
        .sidebar-active { background-color: #f97316 !important; color: white !important; border-radius: 1rem; }
        .page-content { display: none; }
        .active-section { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .orange-card { border-left: 8px solid #f97316; }
        .critical-row { background-color: #fee2e2 !important; border-left: 6px solid #ef4444; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen">

    <div id="login-section" class="fixed inset-0 z-[200] flex items-center justify-center bg-[#1e1b1e]">
        <div class="bg-white p-12 rounded-[3rem] shadow-2xl w-full max-w-md border-b-[15px] border-orange-500">
            <div class="text-center mb-10">
                <div class="w-20 h-20 bg-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-orange-500/30">
                    <i class="fas fa-wrench text-4xl text-white"></i>
                </div>
                <h1 class="text-3xl font-black text-slate-800 tracking-tighter italic">ÖZCAN OTO PRO</h1>
                <p class="text-slate-400 font-bold uppercase text-[10px] tracking-[0.3em] mt-3">Kurumsal Yönetim</p>
            </div>
            <div class="space-y-4">
                <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500">
                <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 bg-slate-50 border-2 rounded-2xl outline-none font-bold focus:border-orange-500">
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-5 rounded-2xl shadow-xl transition-all active:scale-95">SİSTEME GİRİŞ YAP</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <aside class="w-72 bg-slate-900 text-white flex-shrink-0 flex flex-col shadow-2xl z-50">
            <div class="p-8 border-b border-slate-800">
                <h2 class="text-2xl font-black italic text-orange-500 uppercase tracking-tighter">ÖZCAN OTO</h2>
                <div class="flex items-center gap-2 mt-2">
                    <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                    <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Sistem Hazır</p>
                </div>
            </div>
            
            <nav class="flex-1 px-4 py-8 space-y-2 overflow-y-auto">
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mb-2">Genel Özet</p>
                <button onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-th-large"></i> Dashboard
                </button>
                
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mt-6 mb-2">Satış & Stok</p>
                <button onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-boxes"></i> Parça Listesi
                </button>
                <button onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-users-cog"></i> Cari Rehber
                </button>

                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mt-6 mb-2">Finans</p>
                <button onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-4 rounded-xl font-bold text-left">
                    <i class="fas fa-file-invoice-dollar"></i> Gider Takibi
                </button>
                <button onclick="openFinanceModal()" class="w-full flex items-center gap-4 p-4 rounded-xl font-bold text-orange-500 bg-orange-500/10 hover:bg-orange-500 hover:text-white transition-all text-left">
                    <i class="fas fa-wallet"></i> TOPLAM DEPO DEĞERİ
                </button>
            </nav>

            <div class="p-6 bg-slate-950">
                <button onclick="handleLogout()" class="w-full flex items-center justify-center gap-3 p-3 text-red-400 font-bold border border-red-900/30 rounded-xl hover:bg-red-500 hover:text-white transition-all">
                    <i class="fas fa-power-off"></i> ÇIKIŞ
                </button>
            </div>
        </aside>

        <main class="flex-1 p-8 md:p-12 overflow-y-auto">
            
            <div id="page-dashboard" class="page-content active-section">
                <div class="mb-10">
                    <h3 class="text-3xl font-black text-slate-800 uppercase italic">İşletme Özeti</h3>
                    <p id="current-date" class="text-slate-400 font-bold"></p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-orange-500">
                        <i class="fas fa-box-open text-orange-500 text-2xl mb-4"></i>
                        <p class="text-xs font-black text-slate-400 uppercase">Toplam Kayıtlı Parça</p>
                        <h4 id="dash-count" class="text-4xl font-black text-slate-800">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-red-500">
                        <i class="fas fa-exclamation-circle text-red-500 text-2xl mb-4"></i>
                        <p class="text-xs font-black text-slate-400 uppercase">Kritik Stok (2 ve Altı)</p>
                        <h4 id="dash-crit" class="text-4xl font-black text-red-600">0</h4>
                    </div>
                    <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border-b-8 border-emerald-500">
                        <i class="fas fa-address-book text-emerald-500 text-2xl mb-4"></i>
                        <p class="text-xs font-black text-slate-400 uppercase">Kayıtlı Cari</p>
                        <h4 id="dash-cari" class="text-4xl font-black text-slate-800">0</h4>
                    </div>
                </div>

                <div class="bg-white p-10 rounded-[3rem] shadow-sm border">
                    <h4 class="text-lg font-black mb-6 uppercase tracking-tighter">Hızlı İşlem Menüsü</h4>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <button onclick="showPage('stok')" class="p-6 bg-orange-50 text-orange-600 rounded-3xl font-black hover:bg-orange-500 hover:text-white transition-all"><i class="fas fa-plus block mb-2 text-xl"></i> Stok Ekle</button>
                        <button onclick="showPage('gider')" class="p-6 bg-red-50 text-red-600 rounded-3xl font-black hover:bg-red-500 hover:text-white transition-all"><i class="fas fa-minus block mb-2 text-xl"></i> Gider Gir</button>
                        <button onclick="showPage('cari')" class="p-6 bg-blue-50 text-blue-600 rounded-3xl font-black hover:bg-blue-500 hover:text-white transition-all"><i class="fas fa-user-plus block mb-2 text-xl"></i> Yeni Cari</button>
                        <button onclick="openFinanceModal()" class="p-6 bg-emerald-50 text-emerald-600 rounded-3xl font-black hover:bg-emerald-500 hover:text-white transition-all"><i class="fas fa-calculator block mb-2 text-xl"></i> Hesaplama</button>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex flex-col md:flex-row justify-between items-end mb-10 gap-4">
                    <div>
                        <h3 class="text-3xl font-black text-slate-800">Envanter Detayı</h3>
                        <p class="text-slate-400 font-bold uppercase text-[10px] tracking-widest mt-2">Stoklarınız Sıfır Olsa Bile Burada Kalır</p>
                    </div>
                    <input id="search" oninput="yukleStok()" type="text" placeholder="Kod veya isimle ara..." class="p-4 bg-white rounded-2xl border-2 border-slate-100 outline-none focus:border-orange-500 w-full md:w-80 font-bold shadow-sm">
                </div>

                <div class="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-10">
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <input id="in-code" type="text" placeholder="Parça Kodu" class="p-4 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-name" type="text" placeholder="Parça Adı" class="p-4 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-cat" type="text" placeholder="Kategori" class="p-4 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-price" type="number" placeholder="Fiyat (₺)" class="p-4 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                        <input id="in-stock" type="number" placeholder="Stok (Boşsa 1)" class="p-4 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-orange-500">
                        <button onclick="hizliEkle()" class="md:col-span-5 bg-orange-500 text-white font-black rounded-2xl py-4 hover:bg-orange-600 shadow-xl shadow-orange-100 transition-all uppercase">Kaydet</button>
                    </div>
                </div>

                <div class="bg-white rounded-[3rem] shadow-xl border border-slate-100 overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b text-slate-400 text-[10px] font-black uppercase tracking-widest">
                            <tr>
                                <th class="px-8 py-7">Parça Detayı</th>
                                <th class="px-8 py-7">Kategori</th>
                                <th class="px-8 py-7 text-center">Stok</th>
                                <th class="px-8 py-7 text-right">Birim Fiyat</th>
                                <th class="px-8 py-7 text-right">Sil</th>
                            </tr>
                        </thead>
                        <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                    </table>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic">Müşteri & Cari Takibi</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 mb-10 flex flex-col md:flex-row gap-6">
                    <input id="cari-ad" type="text" placeholder="İsim / Firma" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-blue-500">
                    <input id="cari-tel" type="text" placeholder="Telefon No" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-blue-500">
                    <button onclick="cariEkle()" class="px-10 bg-slate-800 text-white font-black rounded-2xl hover:bg-black transition-all uppercase">Cariyi Kaydet</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-3xl font-black text-slate-800 mb-8 uppercase italic tracking-tighter">İşletme Harcamaları</h3>
                <div class="bg-white p-10 rounded-[3rem] shadow-sm border border-slate-100 mb-10 flex flex-col md:flex-row gap-6">
                    <input id="gid-ad" type="text" placeholder="Harcama Açıklaması" class="flex-1 p-5 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-red-500">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="w-full md:w-64 p-5 bg-slate-50 rounded-2xl font-bold border-none ring-2 ring-slate-100 focus:ring-red-500">
                    <button onclick="giderEkle()" class="px-10 bg-red-500 text-white font-black rounded-2xl hover:bg-red-600 shadow-xl shadow-red-100 transition-all uppercase">Gideri İşle</button>
                </div>
                <div id="gider-list" class="space-y-4"></div>
            </div>

        </main>
    </div>

    <div id="finance-modal" class="hidden fixed inset-0 z-[200] bg-slate-900/90 flex items-center justify-center p-6 backdrop-blur-md">
        <div class="bg-white w-full max-w-lg rounded-[4rem] shadow-2xl overflow-hidden border-b-[20px] border-orange-500">
            <div class="bg-orange-500 p-12 text-white text-center">
                <div class="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <i class="fas fa-hand-holding-usd text-4xl"></i>
                </div>
                <h2 class="text-3xl font-black uppercase italic tracking-tighter">Finansal Rapor</h2>
                <p class="text-white/70 font-bold uppercase text-[10px] tracking-widest mt-2">Anlık Özkaynak Durumu</p>
            </div>
            <div class="p-12 space-y-6">
                <div class="flex justify-between items-center p-8 bg-slate-50 rounded-[2.5rem] border-2 border-slate-100">
                    <span class="font-bold text-slate-400 uppercase text-xs">Depo Stok Değeri</span>
                    <span id="fin-stok" class="text-3xl font-black text-emerald-600">₺0</span>
                </div>
                <div class="flex justify-between items-center p-8 bg-slate-50 rounded-[2.5rem] border-2 border-slate-100">
                    <span class="font-bold text-slate-400 uppercase text-xs">Toplam Harcamalar</span>
                    <span id="fin-gider" class="text-3xl font-black text-red-500">₺0</span>
                </div>
                <div class="flex justify-between items-center p-8 bg-orange-500 rounded-[2.5rem] text-white shadow-xl shadow-orange-200">
                    <span class="font-bold uppercase text-xs">Net Durum</span>
                    <span id="fin-net" class="text-3xl font-black">₺0</span>
                </div>
                <button onclick="closeFinanceModal()" class="w-full py-6 bg-slate-900 text-white font-black rounded-3xl uppercase tracking-widest hover:bg-slate-800 transition-all mt-4">Kapat</button>
            </div>
        </div>
    </div>

    <script>
        let products = [];
        let expenses = [];
        let customers = [];
        let totalVal = 0; let totalGid = 0;

        document.getElementById('current-date').innerText = new Date().toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

        function showPage(pageId) {
            document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active-section'));
            document.querySelectorAll('.sidebar-link').forEach(b => b.classList.remove('sidebar-active'));
            document.getElementById('page-' + pageId).classList.add('active-section');
            document.getElementById('btn-' + pageId).classList.add('sidebar-active');
            
            if(pageId === 'dashboard') yukleDashboard();
            if(pageId === 'stok') yukleStok();
            if(pageId === 'cari') yukleCari();
            if(pageId === 'gider') yukleGider();
        }

        function handleLogin() {
            if(document.getElementById('log-user').value === "ozcanoto" && document.getElementById('log-pass').value === "eren9013") {
                localStorage.setItem('pro_session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
                yukleStok();
            } else { alert("Hatalı Giriş!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        async function yukleStok() {
            const res = await fetch('/api/products');
            products = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            let tV = 0;

            document.getElementById('stok-list').innerHTML = products
                .filter(i => (i.name + i.code + (i.category || '')).toLowerCase().includes(q))
                .reverse()
                .map(i => {
                    tV += (i.stock * i.price);
                    const isCritical = i.stock <= 2;
                    return `
                    <tr class="${isCritical ? 'critical-row' : 'hover:bg-orange-50/30'} group transition-all">
                        <td class="px-8 py-7">
                            <div class="font-black ${isCritical ? 'text-red-700' : 'text-slate-800'} text-lg uppercase tracking-tight">${i.name}</div>
                            <div class="text-[10px] font-black text-orange-500 uppercase tracking-widest mt-1">${i.code}</div>
                        </td>
                        <td class="px-8 py-7">
                            <span class="bg-slate-100 px-3 py-1 rounded-full text-[10px] font-black text-slate-500 uppercase">${i.category || 'GENEL'}</span>
                        </td>
                        <td class="px-8 py-7 text-center">
                            <div class="flex items-center justify-center gap-3 bg-white border border-slate-200 p-2 rounded-2xl w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('${i._id}',-1)" class="w-10 h-10 text-red-500 font-black hover:bg-red-50 rounded-xl transition-all">-</button>
                                <span class="w-12 text-center font-black text-xl ${isCritical ? 'text-red-600' : 'text-slate-800'}">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}',1)" class="w-10 h-10 text-emerald-500 font-black hover:bg-emerald-50 rounded-xl transition-all">+</button>
                            </div>
                        </td>
                        <td class="px-8 py-7 text-right font-black text-slate-700">₺${i.price.toLocaleString()}</td>
                        <td class="px-8 py-7 text-right">
                            <button onclick="sil('${i._id}','products')" class="opacity-0 group-hover:opacity-100 transition-all text-slate-300 hover:text-red-500 p-4"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    </tr>`;
                }).join('');
            totalVal = tV;
        }

        async function yukleDashboard() {
            const [pRes, gRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/customers')]);
            const p = await pRes.json();
            const g = await gRes.json();
            const c = await cRes.json();
            
            let crit = p.filter(x => x.stock <= 2).length;
            document.getElementById('dash-count').innerText = p.length;
            document.getElementById('dash-crit').innerText = crit;
            document.getElementById('dash-cari').innerText = c.length;
        }

        async function hizliEkle() {
            const codeInput = document.getElementById('in-code').value;
            const nameInput = document.getElementById('in-name').value;
            const catInput = document.getElementById('in-cat').value;
            const priceInput = document.getElementById('in-price').value;
            const stockInput = document.getElementById('in-stock').value;

            if(!nameInput) return alert("Parça adı boş olamaz!");

            const p = { 
                code: codeInput || 'KODSUZ', 
                name: nameInput, 
                category: catInput || 'GENEL',
                price: parseFloat(priceInput || 0), 
                stock: stockInput === "" ? 1 : parseInt(stockInput)
            };

            await fetch('/api/products', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(p) });
            
            // Alanları Temizle
            document.getElementById('in-name').value = ''; 
            document.getElementById('in-code').value = ''; 
            document.getElementById('in-price').value = '';
            document.getElementById('in-cat').value = '';
            document.getElementById('in-stock').value = '';
            
            yukleStok();
        }

        async function cariEkle() {
            const c = { ad: document.getElementById('cari-ad').value, tel: document.getElementById('cari-tel').value, tarih: new Date().toLocaleDateString('tr-TR') };
            if(!c.ad) return alert("Müşteri adı şart!");
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(c) });
            document.getElementById('cari-ad').value = ''; document.getElementById('cari-tel').value = '';
            yukleCari();
        }

        async function yukleCari() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            document.getElementById('cari-list').innerHTML = data.map(i => `
                <div class="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm flex items-center justify-between group hover:border-orange-500 transition-all">
                    <div class="flex items-center gap-5">
                        <div class="w-16 h-16 bg-slate-900 text-orange-500 rounded-3xl flex items-center justify-center text-xl font-black uppercase">${i.ad.substring(0,2)}</div>
                        <div>
                            <b class="text-slate-800 text-lg uppercase block">${i.ad}</b>
                            <span class="text-sm font-bold text-slate-400">${i.tel || 'NO YOK'}</span>
                        </div>
                    </div>
                    <button onclick="sil('${i._id}','customers')" class="opacity-0 group-hover:opacity-100 transition-all text-red-500 p-4"><i class="fas fa-trash-alt"></i></button>
                </div>`).join('');
        }

        async function giderEkle() {
            const g = { ad: document.getElementById('gid-ad').value, tutar: parseFloat(document.getElementById('gid-tutar').value), tarih: new Date().toLocaleDateString('tr-TR') };
            if(!g.ad || !g.tutar) return alert("Bilgileri tam gir!");
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(g) });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const res = await fetch('/api/expenses');
            expenses = await res.json();
            totalGid = 0;
            document.getElementById('gider-list').innerHTML = expenses.map(i => {
                totalGid += i.tutar;
                return `
                <div class="bg-white p-8 rounded-[2.5rem] border-l-[12px] border-red-500 shadow-sm flex justify-between items-center transition-all hover:scale-[1.01]">
                    <div>
                        <b class="uppercase text-slate-800 text-xl font-black">${i.ad}</b>
                        <p class="text-[10px] text-slate-400 font-black uppercase mt-1 tracking-widest">${i.tarih} | İŞLETME GİDERİ</p>
                    </div>
                    <div class="flex items-center gap-8">
                        <div class="font-black text-red-500 text-3xl italic">₺${i.tutar.toLocaleString()}</div>
                        <button onclick="sil('${i._id}','expenses')" class="text-slate-200 hover:text-red-500"><i class="fas fa-trash-alt text-xl"></i></button>
                    </div>
                </div>`;
            }).join('');
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Usta, bu kayıt tamamen silinecek. Onaylıyor musun?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); 
                else if(col==='customers') yukleCari(); 
                else yukleGider();
            }
        }

        function openFinanceModal() {
            document.getElementById('finance-modal').classList.remove('hidden');
            document.getElementById('fin-stok').innerText = '₺' + totalVal.toLocaleString();
            document.getElementById('fin-gider').innerText = '₺' + totalGid.toLocaleString();
            document.getElementById('fin-net').innerText = '₺' + (totalVal - totalGid).toLocaleString();
        }

        function closeFinanceModal() { document.getElementById('finance-modal').classList.add('hidden'); }

        window.onload = () => {
            if(localStorage.getItem('pro_session')) {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
                yukleStok();
            }
        };
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
    change = request.json['change']
    product = db.products.find_one({"_id": ObjectId(id)})
    if change == -1 and product['stock'] <= 0:
        return jsonify({"ok": False})
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
