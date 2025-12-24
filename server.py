<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>StokTakip Pro - Akıllı Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#F8FAFC] font-sans">
    <nav class="bg-white border-b px-8 py-4 flex justify-between items-center sticky top-0 z-50 shadow-sm">
        <div class="flex items-center gap-3">
            <div class="bg-blue-600 p-2.5 rounded-xl text-white shadow-lg shadow-blue-200">
                <i class="fas fa-cubes text-xl"></i>
            </div>
            <h1 class="text-xl font-black text-slate-800">StokTakip Pro</h1>
        </div>
        <div class="text-sm font-medium">Kullanıcı: <b class="text-blue-600">purna</b></div>
    </nav>

    <div class="max-w-7xl mx-auto p-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
                <p class="text-slate-400 text-xs font-black uppercase tracking-widest">Toplam Parça</p>
                <h2 id="total-count" class="text-5xl font-black text-slate-800 mt-3">0</h2>
            </div>
            <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-red-100">
                <p class="text-slate-400 text-xs font-black uppercase tracking-widest text-red-400">Kritik Stok Uyarı</p>
                <h2 id="critical-count" class="text-5xl font-black text-red-500 mt-3">0</h2>
            </div>
            <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
                <p class="text-slate-400 text-xs font-black uppercase tracking-widest">Toplam Değer</p>
                <h2 id="total-value" class="text-5xl font-black text-emerald-500 mt-3">₺0</h2>
            </div>
        </div>

        <div class="flex justify-between items-center mb-8">
            <button onclick="modalAc()" class="bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-2xl font-black text-sm shadow-lg shadow-blue-200 transition-all active:scale-95">
                <i class="fas fa-plus"></i> YENİ PARÇA EKLE
            </button>
        </div>

        <div class="bg-white rounded-[2rem] shadow-xl border border-slate-100 overflow-hidden">
            <table class="w-full text-left">
                <thead class="bg-slate-50 border-b">
                    <tr class="text-slate-400 text-[10px] font-black uppercase tracking-widest">
                        <th class="px-8 py-6">Parça Detayı</th>
                        <th class="px-8 py-6">Kategori</th>
                        <th class="px-8 py-6">Stok</th>
                        <th class="px-8 py-6 text-right">İşlem</th>
                    </tr>
                </thead>
                <tbody id="product-list" class="divide-y divide-slate-50"></tbody>
            </table>
        </div>
    </div>

    <div id="modal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm hidden z-[100] flex items-center justify-center p-4">
        <div class="bg-white rounded-[2.5rem] p-10 w-full max-w-lg shadow-2xl">
            <h2 class="text-2xl font-black text-slate-800 mb-8">Yeni Kayıt Oluştur</h2>
            <div class="space-y-4">
                <input id="in-name" type="text" placeholder="Parça Adı" class="w-full px-6 py-4 bg-slate-50 rounded-2xl border-none outline-none font-bold">
                <input id="in-cat" type="text" placeholder="Kategori (Örn: Motor, Fren)" class="w-full px-6 py-4 bg-slate-50 rounded-2xl border-none outline-none font-bold">
                <div class="grid grid-cols-2 gap-4">
                    <input id="in-stock" type="number" placeholder="Mevcut Stok" class="w-full px-6 py-4 bg-slate-50 rounded-2xl border-none outline-none font-bold">
                    <input id="in-limit" type="number" placeholder="Kritik Limit" class="w-full px-6 py-4 bg-slate-50 rounded-2xl border-none outline-none font-bold">
                </div>
                <input id="in-price" type="number" placeholder="Birim Fiyat (₺)" class="w-full px-6 py-4 bg-slate-50 rounded-2xl border-none outline-none font-bold">
                <button onclick="urunKaydet()" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-black shadow-lg shadow-blue-100 transition-all">KAYDET</button>
                <button onclick="modalKapat()" class="w-full text-slate-400 font-bold py-2">Vazgeç</button>
            </div>
        </div>
    </div>

    <script>
        const API_URL = "https://stok-takip-backend-v2zr.onrender.com"; //

        function modalAc() { document.getElementById('modal').classList.remove('hidden'); }
        function modalKapat() { document.getElementById('modal').classList.add('hidden'); }

        async function verileriYukle() {
            try {
                const res = await fetch(`${API_URL}/products`);
                const data = await res.json();
                const list = document.getElementById('product-list');
                
                document.getElementById('total-count').innerText = data.length;
                let val = 0; let crit = 0;

                list.innerHTML = data.map(i => {
                    const price = i.price || 0;
                    val += (price * i.stock);
                    const limit = i.critical_limit || 10;
                    const isCrit = i.stock <= limit;
                    if(isCrit) crit++;

                    return `
                    <tr class="${isCrit ? 'bg-red-50' : 'hover:bg-slate-50'} transition-all">
                        <td class="px-8 py-6 font-bold text-slate-700">${i.name}<br><span class="text-[9px] text-slate-400 uppercase">Limit: ${limit}</span></td>
                        <td class="px-8 py-6 text-xs font-black text-blue-500 uppercase">${i.category || 'Genel'}</td>
                        <td class="px-8 py-6 font-black ${isCrit ? 'text-red-600' : 'text-slate-900'}">${i.stock} ${isCrit ? '⚠️' : ''}</td>
                        <td class="px-8 py-6 text-right">
                            <button onclick="sil('${i._id}')" class="text-red-300 hover:text-red-500 transition-colors"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    </tr>`;
                }).join('');

                document.getElementById('total-value').innerText = `₺${val.toLocaleString()}`;
                document.getElementById('critical-count').innerText = crit;
            } catch (err) { console.error("Bağlantı sorunu!", err); }
        }

        async function urunKaydet() {
            const doc = {
                name: document.getElementById('in-name').value,
                category: document.getElementById('in-cat').value,
                stock: parseInt(document.getElementById('in-stock').value),
                critical_limit: parseInt(document.getElementById('in-limit').value || 10),
                price: parseFloat(document.getElementById('in-price').value || 0)
            };
            await fetch(`${API_URL}/products`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(doc)
            });
            modalKapat(); verileriYukle();
        }

        async function sil(id) { if(confirm('Silinsin mi?')) { await fetch(`${API_URL}/products/${id}`, {method: 'DELETE'}); verileriYukle(); } }
        verileriYukle();
    </script>
</body>
</html>
