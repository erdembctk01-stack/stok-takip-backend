from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime

# --- SİSTEM AYARLARI ---
app = Flask(__name__)
CORS(app)

# --- MONGODB VERİTABANI BAĞLANTISI ---
# Veritabanı bağlantısı detaylandırılarak korundu.
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

# --- KULLANICI ARAYÜZÜ (HTML/JS) ---
HTML_PANEL = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ÖZCAN OTO PRO | Kurumsal Stok Yönetim Sistemi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; scroll-behavior: smooth; }
        .sidebar-link { transition: all 0.2s ease-in-out; color: #cbd5e1; cursor: pointer; }
        .sidebar-link:hover { background-color: #f97316; color: white; transform: translateX(5px); }
        .sidebar-active { background-color: #f97316 !important; color: white !important; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4); }
        .page-content { display: none; }
        .active-section { display: block; animation: fadeIn 0.4s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        .critical-row { background-color: #fef2f2 !important; border-left: 6px solid #ef4444 !important; }
        input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
        .custom-shadow { box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }
    </style>
</head>
<body class="bg-slate-50 min-h-screen selection:bg-orange-100 selection:text-orange-600">

    <div id="login-section" class="fixed inset-0 z-[200] flex items-center justify-center bg-[#1e1b1e]">
        <div class="bg-white p-12 rounded-[3.5rem] shadow-2xl w-full max-w-md border-b-[15px] border-orange-500 transition-all">
            <div class="text-center mb-10">
                <div class="w-24 h-24 bg-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-orange-500/40 rotate-3">
                    <i class="fas fa-wrench text-5xl text-white"></i>
                </div>
                <h1 class="text-4xl font-black text-slate-800 tracking-tighter italic">ÖZCAN OTO PRO</h1>
                <p class="text-slate-400 font-bold uppercase text-[10px] tracking-[0.4em] mt-3">Yönetim Paneli Girişi</p>
            </div>
            <div class="space-y-5">
                <div class="relative">
                    <i class="fas fa-user absolute left-5 top-5 text-slate-400"></i>
                    <input id="log-user" type="text" placeholder="Kullanıcı Adı" class="w-full p-5 pl-12 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none font-bold focus:border-orange-500 transition-all">
                </div>
                <div class="relative">
                    <i class="fas fa-lock absolute left-5 top-5 text-slate-400"></i>
                    <input id="log-pass" type="password" placeholder="Şifre" class="w-full p-5 pl-12 bg-slate-50 border-2 border-slate-100 rounded-2xl outline-none font-bold focus:border-orange-500 transition-all">
                </div>
                <button onclick="handleLogin()" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-black py-6 rounded-2xl shadow-xl shadow-orange-200 transition-all active:scale-95 uppercase tracking-widest">Sisteme Giriş Yap</button>
            </div>
        </div>
    </div>

    <div id="main-section" class="hidden flex min-h-screen">
        
        <aside class="w-80 bg-slate-900 text-white flex-shrink-0 flex flex-col shadow-2xl z-50">
            <div class="p-10 border-b border-slate-800/50">
                <h2 class="text-3xl font-black italic text-orange-500 uppercase tracking-tighter">ÖZCAN OTO</h2>
                <div class="flex items-center gap-2 mt-3">
                    <div class="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse"></div>
                    <p class="text-[11px] text-slate-400 font-bold uppercase tracking-widest">Sistem Çevrimiçi</p>
                </div>
            </div>
            
            <nav class="flex-1 px-5 py-10 space-y-3 overflow-y-auto">
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mb-3 tracking-[0.2em]">Genel Bakış</p>
                <div onclick="showPage('dashboard')" id="btn-dashboard" class="sidebar-link sidebar-active w-full flex items-center gap-4 p-5 rounded-2xl font-bold">
                    <i class="fas fa-chart-line text-xl"></i> Dashboard
                </div>
                
                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mt-10 mb-3 tracking-[0.2em]">Envanter Yönetimi</p>
                <div onclick="showPage('stok')" id="btn-stok" class="sidebar-link w-full flex items-center gap-4 p-5 rounded-2xl font-bold">
                    <i class="fas fa-cubes text-xl"></i> Parça Listesi
                </div>
                <div onclick="showPage('cari')" id="btn-cari" class="sidebar-link w-full flex items-center gap-4 p-5 rounded-2xl font-bold">
                    <i class="fas fa-address-book text-xl"></i> Müşteri / Cari
                </div>

                <p class="text-[10px] text-slate-500 font-black uppercase px-4 mt-10 mb-3 tracking-[0.2em]">Muhasebe</p>
                <div onclick="showPage('gider')" id="btn-gider" class="sidebar-link w-full flex items-center gap-4 p-5 rounded-2xl font-bold">
                    <i class="fas fa-receipt text-xl"></i> Gider Kayıtları
                </div>
                <div onclick="openFinanceModal()" class="w-full flex items-center gap-4 p-5 rounded-2xl font-bold text-orange-400 bg-orange-400/5 hover:bg-orange-500 hover:text-white transition-all border border-orange-500/20 mt-10">
                    <i class="fas fa-vault text-xl"></i> KASA DURUMU
                </div>
            </nav>

            <div class="p-8 bg-slate-950/50">
                <button onclick="handleLogout()" class="w-full flex items-center justify-center gap-3 p-4 text-red-400 font-bold border border-red-500/20 rounded-2xl hover:bg-red-500 hover:text-white transition-all group">
                    <i class="fas fa-power-off group-hover:rotate-90 transition-transform"></i> OTURUMU KAPAT
                </button>
            </div>
        </aside>

        <main class="flex-1 p-10 lg:p-16 overflow-y-auto bg-slate-50">
            
            <div id="page-dashboard" class="page-content active-section">
                <header class="mb-12">
                    <h3 class="text-4xl font-black text-slate-800 uppercase italic tracking-tight">İşletme Özeti</h3>
                    <p id="current-date" class="text-slate-400 font-bold mt-2 text-lg"></p>
                </header>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-10 mb-16">
                    <div class="bg-white p-10 rounded-[3rem] custom-shadow border-b-8 border-orange-500 group hover:-translate-y-2 transition-transform">
                        <i class="fas fa-box text-orange-500 text-3xl mb-6"></i>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Kayıtlı Parça</p>
                        <h4 id="dash-count" class="text-5xl font-black text-slate-800 mt-2">0</h4>
                    </div>
                    <div class="bg-white p-10 rounded-[3rem] custom-shadow border-b-8 border-red-500 group hover:-translate-y-2 transition-transform">
                        <i class="fas fa-triangle-exclamation text-red-500 text-3xl mb-6"></i>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Kritik Stok</p>
                        <h4 id="dash-crit" class="text-5xl font-black text-red-600 mt-2">0</h4>
                    </div>
                    <div class="bg-white p-10 rounded-[3rem] custom-shadow border-b-8 border-emerald-500 group hover:-translate-y-2 transition-transform">
                        <i class="fas fa-user-tie text-emerald-500 text-3xl mb-6"></i>
                        <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Cari Sayısı</p>
                        <h4 id="dash-cari" class="text-5xl font-black text-slate-800 mt-2">0</h4>
                    </div>
                </div>

                <div class="bg-slate-900 p-12 rounded-[3.5rem] shadow-2xl text-white relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-10 opacity-10">
                        <i class="fas fa-file-export text-[150px]"></i>
                    </div>
                    <h4 class="text-2xl font-black mb-8 uppercase italic text-orange-500">Gün Sonu Raporlama Servisi</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <button onclick="exportStokExcel()" class="p-8 bg-white/10 border border-white/20 rounded-[2rem] font-black hover:bg-emerald-600 hover:border-emerald-500 transition-all flex items-center justify-center gap-5 text-lg group">
                            <i class="fas fa-file-excel text-3xl group-hover:scale-110 transition-transform"></i> EXCEL LİSTESİ İNDİR
                        </button>
                        <button onclick="sendGmailReport()" class="p-8 bg-white/10 border border-white/20 rounded-[2rem] font-black hover:bg-orange-600 hover:border-orange-500 transition-all flex items-center justify-center gap-5 text-lg group">
                            <i class="fas fa-envelope-open-text text-3xl group-hover:scale-110 transition-transform"></i> GMAIL RAPORU GÖNDER
                        </button>
                    </div>
                </div>
            </div>

            <div id="page-stok" class="page-content">
                <div class="flex flex-col lg:flex-row justify-between items-center mb-12 gap-6">
                    <div>
                        <h3 class="text-4xl font-black text-slate-800 italic uppercase">Parça Envanteri</h3>
                        <p class="text-slate-400 font-bold mt-2">Stok Durumu ve Birim Fiyat Yönetimi</p>
                    </div>
                    <div class="relative w-full lg:w-96">
                        <i class="fas fa-search absolute left-5 top-5 text-slate-400"></i>
                        <input id="search" oninput="yukleStok()" type="text" placeholder="Parça veya kod ara..." class="w-full p-5 pl-14 bg-white rounded-2xl border-2 border-slate-100 outline-none focus:border-orange-500 font-bold custom-shadow transition-all">
                    </div>
                </div>

                <div class="bg-white p-10 rounded-[3rem] border border-slate-100 mb-12 custom-shadow">
                    <h5 class="text-sm font-black uppercase text-slate-400 mb-6 tracking-widest">Yeni Parça Girişi</h5>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-5">
                        <input id="in-code" type="text" placeholder="Parça Kodu" class="p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-orange-500 transition-all outline-none">
                        <input id="in-name" type="text" placeholder="Parça Adı" class="p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-orange-500 transition-all outline-none">
                        <input id="in-cat" type="text" placeholder="Kategori" class="p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-orange-500 transition-all outline-none">
                        <input id="in-price" type="number" placeholder="Birim Fiyat (₺)" class="p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-orange-500 transition-all outline-none">
                        <input id="in-stock" type="number" placeholder="Adet" class="p-5 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-orange-500 transition-all outline-none">
                        <button onclick="hizliEkle()" class="lg:col-span-5 bg-orange-500 text-white font-black rounded-2xl py-6 hover:bg-orange-600 shadow-xl shadow-orange-100 transition-all uppercase tracking-widest text-lg">Sisteme Parçayı Kaydet</button>
                    </div>
                </div>

                <div class="bg-white rounded-[3.5rem] shadow-2xl border border-slate-100 overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead class="bg-slate-900 text-white uppercase text-[11px] font-black tracking-[0.2em]">
                                <tr>
                                    <th class="px-10 py-8">Parça Bilgisi</th>
                                    <th class="px-10 py-8">Kategori</th>
                                    <th class="px-10 py-8 text-center">Stok Adeti</th>
                                    <th class="px-10 py-8 text-right">Fiyat</th>
                                    <th class="px-10 py-8 text-right">İşlem</th>
                                </tr>
                            </thead>
                            <tbody id="stok-list" class="divide-y divide-slate-100"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="page-cari" class="page-content">
                <h3 class="text-4xl font-black text-slate-800 mb-10 uppercase italic tracking-tighter">Müşteri Rehberi</h3>
                <div class="bg-white p-12 rounded-[3.5rem] custom-shadow border mb-12 flex flex-col lg:flex-row gap-6">
                    <input id="cari-ad" type="text" placeholder="Müşteri / Firma Adı" class="flex-1 p-6 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-emerald-500 outline-none transition-all">
                    <input id="cari-tel" type="text" placeholder="Telefon Numarası" class="flex-1 p-6 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-emerald-500 outline-none transition-all">
                    <button onclick="cariEkle()" class="px-12 bg-emerald-600 text-white font-black rounded-2xl hover:bg-emerald-700 transition-all uppercase shadow-xl shadow-emerald-100">Cari Ekle</button>
                </div>
                <div id="cari-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"></div>
            </div>

            <div id="page-gider" class="page-content">
                <h3 class="text-4xl font-black text-slate-800 mb-10 uppercase italic tracking-tighter">İşletme Harcamaları</h3>
                <div class="bg-white p-12 rounded-[3.5rem] custom-shadow border mb-12 flex flex-col lg:flex-row gap-6">
                    <input id="gid-ad" type="text" placeholder="Gider Açıklaması (Kira, Fatura vb.)" class="flex-1 p-6 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-red-500 outline-none transition-all">
                    <input id="gid-tutar" type="number" placeholder="Tutar (₺)" class="w-full lg:w-72 p-6 bg-slate-50 rounded-2xl font-bold border-2 border-slate-50 focus:border-red-500 outline-none transition-all">
                    <button onclick="giderEkle()" class="px-12 bg-red-500 text-white font-black rounded-2xl hover:bg-red-600 transition-all uppercase shadow-xl shadow-red-100">Gider İşle</button>
                </div>
                <div id="gider-list" class="space-y-6"></div>
            </div>

        </main>
    </div>

    <div id="finance-modal" class="hidden fixed inset-0 z-[250] bg-slate-900/95 flex items-center justify-center p-6 backdrop-blur-xl">
        <div class="bg-white w-full max-w-2xl rounded-[4rem] shadow-2xl overflow-hidden border-b-[20px] border-orange-500 scale-95 transition-transform duration-300">
            <div class="bg-orange-500 p-16 text-white text-center">
                <div class="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce">
                    <i class="fas fa-coins text-4xl"></i>
                </div>
                <h2 class="text-4xl font-black uppercase italic tracking-tighter">Mali Durum Raporu</h2>
                <p class="text-white/80 font-bold uppercase text-xs tracking-[0.3em] mt-3">Anlık Muhasebe Verileri</p>
            </div>
            <div class="p-16 space-y-8">
                <div class="flex justify-between items-center p-8 bg-slate-50 rounded-3xl border-2 border-slate-100">
                    <span class="font-black text-slate-400 uppercase text-xs tracking-widest">Toplam Stok Değeri</span>
                    <span id="fin-stok" class="text-4xl font-black text-emerald-600 tracking-tighter">₺0</span>
                </div>
                <div class="flex justify-between items-center p-8 bg-slate-50 rounded-3xl border-2 border-slate-100">
                    <span class="font-black text-slate-400 uppercase text-xs tracking-widest">Toplam Giderler</span>
                    <span id="fin-gider" class="text-4xl font-black text-red-500 tracking-tighter">₺0</span>
                </div>
                <div class="flex justify-between items-center p-10 bg-slate-900 rounded-[2.5rem] text-white shadow-2xl">
                    <span class="font-black uppercase text-xs tracking-widest text-orange-500">Net Özkaynak</span>
                    <span id="fin-net" class="text-4xl font-black tracking-tighter">₺0</span>
                </div>
                <button onclick="closeFinanceModal()" class="w-full py-7 bg-slate-100 text-slate-500 font-black rounded-3xl uppercase tracking-widest hover:bg-slate-200 transition-all">Pencereyi Kapat</button>
            </div>
        </div>
    </div>

    <script>
        let products = []; let expenses = []; let customers = [];
        let totalVal = 0; let totalGid = 0;

        // --- GİRİŞ KONTROLÜ ---
        function handleLogin() {
            const u = document.getElementById('log-user').value;
            const p = document.getElementById('log-pass').value;
            if(u === "ozcanoto" && p === "eren9013") {
                localStorage.setItem('pro_session', 'active');
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('main-section').classList.remove('hidden');
                showPage('dashboard');
                yukleDashboard();
            } else { alert("Giriş Bilgileri Hatalı, Tekrar Deneyin!"); }
        }

        function handleLogout() { localStorage.clear(); location.reload(); }

        // --- SAYFA YÖNETİMİ ---
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

        // --- VERİ ÇEKME VE LİSTELEME (STOK) ---
        async function yukleStok() {
            const res = await fetch('/api/products');
            products = await res.json();
            const q = document.getElementById('search').value.toLowerCase();
            let tV = 0;

            const listEl = document.getElementById('stok-list');
            listEl.innerHTML = products
                .filter(i => (i.name + i.code + (i.category || '')).toLowerCase().includes(q))
                .reverse()
                .map(i => {
                    tV += (i.stock * i.price);
                    const isCrit = i.stock <= 2;
                    return `
                    <tr class="${isCrit ? 'critical-row' : 'hover:bg-slate-50'} transition-all group">
                        <td class="px-10 py-8">
                            <div class="font-black ${isCrit ? 'text-red-700' : 'text-slate-800'} text-lg uppercase">${i.name}</div>
                            <div class="text-[10px] font-black text-orange-500 tracking-widest mt-1">${i.code}</div>
                        </td>
                        <td class="px-10 py-8">
                            <span class="bg-slate-100 px-4 py-2 rounded-full text-[10px] font-black text-slate-500 uppercase tracking-tighter">${i.category || 'GENEL'}</span>
                        </td>
                        <td class="px-10 py-8 text-center">
                            <div class="flex items-center justify-center gap-4 bg-white border border-slate-200 p-2 rounded-2xl w-fit mx-auto shadow-sm">
                                <button onclick="stokGuncelle('${i._id}',-1)" class="w-10 h-10 text-red-500 font-black hover:bg-red-50 rounded-xl transition-all">-</button>
                                <span class="w-14 text-center font-black text-xl ${isCrit ? 'text-red-600' : 'text-slate-800'}">${i.stock}</span>
                                <button onclick="stokGuncelle('${i._id}',1)" class="w-10 h-10 text-emerald-500 font-black hover:bg-emerald-50 rounded-xl transition-all">+</button>
                            </div>
                        </td>
                        <td class="px-10 py-8 text-right font-black text-slate-700 text-lg italic">₺${i.price.toLocaleString('tr-TR')}</td>
                        <td class="px-10 py-8 text-right">
                            <button onclick="sil('${i._id}','products')" class="text-slate-200 hover:text-red-500 transition-colors p-4"><i class="fas fa-trash-alt text-xl"></i></button>
                        </td>
                    </tr>`;
                }).join('');
            totalVal = tV;
        }

        // --- EXCEL ÇIKTISI (ÇİNCE KARAKTER VE LİSTE DÜZENLEMESİ) ---
        function exportStokExcel() {
            if(products.length === 0) return alert("Raporlanacak Veri Bulunamadı!");
            
            // Excel içeriği için ham veri (Array of Arrays)
            let excelData = [
                ["ÖZCAN OTO - GÜNLÜK STOK LİSTESİ"],
                ["Tarih: " + new Date().toLocaleDateString('tr-TR')],
                ["--------------------------------------------------"],
                [" "]
            ];
            
            products.forEach(p => {
                excelData.push(["PARÇA: " + p.name.toUpperCase()]);
                excelData.push(["KOD: " + p.code]);
                excelData.push(["KATEGORİ: " + (p.category || "GENEL").toUpperCase()]);
                excelData.push(["STOK: " + p.stock + " ADET"]);
                excelData.push(["BİRİM FİYAT: " + p.price.toLocaleString('tr-TR') + " TL"]);
                excelData.push(["TOPLAM DEĞER: " + (p.stock * p.price).toLocaleString('tr-TR') + " TL"]);
                excelData.push(["--------------------------------------------------"]);
            });
            
            excelData.push([" "]);
            excelData.push(["TOPLAM DEPO STOK DEĞERİ: " + totalVal.toLocaleString('tr-TR') + " TL"]);

            // Excel dosyasını oluşturma
            const ws = XLSX.utils.aoa_to_sheet(excelData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Günlük Stok");

            // Çince karakter sorununu çözen bölüm (UTF-8 BOM eklenmiş yazım)
            const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'binary' });
            function s2ab(s) {
                const buf = new ArrayBuffer(s.length);
                const view = new Uint8Array(buf);
                for (let i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
                return buf;
            }

            const blob = new Blob([s2ab(wbout)], { type: "application/octet-stream" });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `OzcanOto_Stok_${new Date().toLocaleDateString('tr-TR')}.xlsx`;
            a.click();
        }

        // --- GMAIL RAPORU ---
        function sendGmailReport() {
            if(products.length === 0) return alert("Raporlanacak parça yok!");
            let body = `ÖZCAN OTO GÜNLÜK RAPOR - ${new Date().toLocaleDateString('tr-TR')}\n\n`;
            products.forEach(p => {
                body += `PARÇA: ${p.name.toUpperCase()}\nKOD: ${p.code}\nSTOK: ${p.stock} ADET\nFİYAT: ₺${p.price.toLocaleString('tr-TR')}\n--------------------------\n`;
            });
            body += `\nTOPLAM DEPO DEĞERİ: ₺${totalVal.toLocaleString('tr-TR')}`;
            window.location.href = `mailto:adanaozcanotoyedekparca@gmail.com?subject=Ozcan Oto Gunluk Rapor&body=${encodeURIComponent(body)}`;
        }

        // --- DİĞER FONKSİYONLAR (DETAYLANDIRILMIŞ) ---
        async function yukleDashboard() {
            const [pRes, gRes, cRes] = await Promise.all([fetch('/api/products'), fetch('/api/expenses'), fetch('/api/customers')]);
            const p = await pRes.json(); const g = await gRes.json(); const c = await cRes.json();
            products = p; expenses = g;
            document.getElementById('dash-count').innerText = p.length;
            document.getElementById('dash-crit').innerText = p.filter(x => x.stock <= 2).length;
            document.getElementById('dash-cari').innerText = c.length;
            document.getElementById('current-date').innerText = new Date().toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            
            totalVal = 0; p.forEach(i => totalVal += (i.stock * i.price));
            totalGid = 0; g.forEach(i => totalGid += i.tutar);
        }

        async function hizliEkle() {
            const n = document.getElementById('in-name').value;
            if(!n) return alert("Parça Adı Boş Olamaz!");
            const obj = {
                code: document.getElementById('in-code').value || 'KODSUZ',
                name: n,
                category: document.getElementById('in-cat').value || 'GENEL',
                price: parseFloat(document.getElementById('in-price').value || 0),
                stock: parseInt(document.getElementById('in-stock').value || 1)
            };
            await fetch('/api/products', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(obj) });
            ['in-name','in-code','in-cat','in-price','in-stock'].forEach(id => document.getElementById(id).value = '');
            yukleStok();
        }

        async function cariEkle() {
            const ad = document.getElementById('cari-ad').value;
            if(!ad) return alert("İsim Giriniz!");
            await fetch('/api/customers', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ad, tel: document.getElementById('cari-tel').value, tarih: new Date().toLocaleDateString('tr-TR')}) });
            document.getElementById('cari-ad').value = ''; document.getElementById('cari-tel').value = '';
            yukleCari();
        }

        async function yukleCari() {
            const r = await fetch('/api/customers'); const d = await r.json();
            document.getElementById('cari-list').innerHTML = d.map(i => `
                <div class="bg-white p-10 rounded-[2.5rem] custom-shadow flex items-center justify-between group hover:border-emerald-500 border-2 border-transparent transition-all">
                    <div><b class="text-xl text-slate-800 uppercase block">${i.ad}</b><span class="text-sm font-bold text-slate-400 mt-1 block tracking-widest">${i.tel || 'NO YOK'}</span></div>
                    <button onclick="sil('${i._id}','customers')" class="text-red-400 opacity-0 group-hover:opacity-100 transition-all"><i class="fas fa-trash-alt text-xl"></i></button>
                </div>`).join('');
        }

        async function giderEkle() {
            const ad = document.getElementById('gid-ad').value; const tutar = parseFloat(document.getElementById('gid-tutar').value);
            if(!ad || !tutar) return alert("Bilgileri Eksiksiz Doldurun!");
            await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ad, tutar, tarih: new Date().toLocaleDateString('tr-TR')}) });
            document.getElementById('gid-ad').value = ''; document.getElementById('gid-tutar').value = '';
            yukleGider();
        }

        async function yukleGider() {
            const r = await fetch('/api/expenses'); const d = await r.json();
            document.getElementById('gider-list').innerHTML = d.map(i => `
                <div class="bg-white p-10 rounded-[2.5rem] border-l-[15px] border-red-500 custom-shadow flex justify-between items-center group">
                    <div><b class="uppercase text-2xl text-slate-800">${i.ad}</b><p class="text-xs text-slate-400 font-black mt-2 tracking-widest uppercase">${i.tarih}</p></div>
                    <div class="flex items-center gap-10">
                        <div class="font-black text-red-500 text-3xl italic tracking-tighter">₺${i.tutar.toLocaleString('tr-TR')}</div>
                        <button onclick="sil('${i._id}','expenses')" class="text-slate-200 hover:text-red-500 transition-colors"><i class="fas fa-trash-alt text-2xl"></i></button>
                    </div>
                </div>`).join('');
        }

        async function stokGuncelle(id, change) {
            await fetch(`/api/products/${id}/stock`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({change}) });
            yukleStok();
        }

        async function sil(id, col) {
            if(confirm('Usta, bu kaydı tamamen siliyorum. Onaylıyor musun?')) {
                await fetch(`/api/${col}/${id}`, {method: 'DELETE'});
                if(col==='products') yukleStok(); else if(col==='customers') yukleCari(); else yukleGider();
            }
        }

        function openFinanceModal() {
            document.getElementById('finance-modal').classList.remove('hidden');
            document.getElementById('fin-stok').innerText = '₺' + totalVal.toLocaleString('tr-TR');
            document.getElementById('fin-gider').innerText = '₺' + totalGid.toLocaleString('tr-TR');
            document.getElementById('fin-net').innerText = '₺' + (totalVal - totalGid).toLocaleString('tr-TR');
        }

        function closeFinanceModal() { document.getElementById('finance-modal').classList.add('hidden'); }

        window.onload = () => { if(localStorage.getItem('pro_session')) { document.getElementById('login-section').classList.add('hidden'); document.getElementById('main-section').classList.remove('hidden'); showPage('dashboard'); } };
    </script>
</body>
</html>
"""

# --- API ROTARI (DETAYLANDIRILMIŞ) ---
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
    return jsonify({"ok": True, "message": "Kayıt Başarıyla Eklendi"})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    db[col].delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

@app.route('/api/products/<id>/stock', methods=['PUT'])
def update_stock(id):
    change = request.json['change']
    product = db.products.find_one({"_id": ObjectId(id)})
    if change == -1 and product['stock'] <= 0:
        return jsonify({"ok": False, "msg": "Stok sıfırın altına düşemez"})
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": change}})
    return jsonify({"ok": True})

# --- SİSTEMİ ÇALIŞTIR ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
