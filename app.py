from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# DOSYA BAĞLANTILARI
from satis_yonetimi import satis_bp, init_db as satis_init
from stok_yonetimi import stok_bp, init_db as stok_init

app = Flask(__name__)

# MONGODB BAĞLANTISI (Buradaki URI adresini kendi adresinle kontrol et)
MONGO_URI = "mongodb+srv://ozcanoto:eren9013@cluster0.mongodb.net/ozcan_oto?retryWrites=True&w=majority"
client = MongoClient(MONGO_URI)
db = client.ozcan_oto

# BLUEPRINT BAĞLANTILARI VE VERİTABANI AKTARIMI
# satis_yonetimi.py içine db nesnesini gönderiyoruz
satis_init(db)
app.register_blueprint(satis_bp)

# stok_yonetimi.py içine db nesnesini gönderiyoruz
stok_init(db)
app.register_blueprint(stok_bp)

# ANA SAYFA
@app.route('/')
def index():
    return render_template('index.html')

# DASHBOARD İSTATİSTİKLERİ
@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    try:
        # Toplam Kazanç (Faturalardaki 'toplam' alanlarının toplamı)
        invoices = list(db.invoices.find())
        toplam_kazanc = sum(float(inv.get('toplam', 0)) for inv in invoices)
        
        # Toplam Gider
        expenses = list(db.expenses.find())
        toplam_gider = sum(float(exp.get('tutar', 0)) for exp in expenses)
        
        # Stok Değeri (Adet * Ortalama Fiyat)
        products = list(db.products.find())
        stok_degeri = sum(int(p.get('stock', 0)) * float(str(p.get('price', 0)).replace(',', '.')) for p in products)
        
        return jsonify({
            "kazanc": f"₺{toplam_kazanc:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "gider": f"₺{toplam_gider:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "depo": f"₺{stok_degeri:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        })
    except Exception as e:
        return jsonify({"kazanc": "₺0,00", "gider": "₺0,00", "depo": "₺0,00", "error": str(e)})

# GİDER İŞLEMLERİ
@app.route('/api/expenses', methods=['GET', 'POST'])
def manage_expenses():
    if request.method == 'POST':
        data = request.json
        db.expenses.insert_one({
            "aciklama": data['aciklama'],
            "tutar": float(str(data['tutar']).replace(',', '.')),
            "tarih": datetime.now().strftime('%d.%m.%Y')
        })
        return jsonify({"status": "success"})
    
    expenses = list(db.expenses.find())
    for e in expenses:
        e['_id'] = str(e['_id'])
    return jsonify(expenses)

@app.route('/api/expenses/<id>', methods=['DELETE'])
def delete_expense(id):
    db.expenses.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

# CARİ REHBER / MÜŞTERİLER
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = list(db.customers.find())
    for c in customers:
        c['_id'] = str(c['_id'])
    return jsonify(customers)

@app.route('/api/customers/<id>', methods=['DELETE'])
def delete_customer(id):
    db.customers.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

# VERESİYE İŞLEMLERİ
@app.route('/api/veresiye', methods=['GET', 'POST'])
def manage_veresiye():
    if request.method == 'POST':
        data = request.json
        db.veresiye.insert_one({
            "ad": data['ad'],
            "tel": data['tel'],
            "islem": data['islem'],
            "para": data['para'],
            "tarih": datetime.now().strftime('%d.%m.%Y')
        })
        return jsonify({"status": "success"})
    
    veresiye_list = list(db.veresiye.find())
    for v in veresiye_list:
        v['_id'] = str(v['_id'])
    return jsonify(veresiye_list)

@app.route('/api/veresiye/<id>', methods=['DELETE'])
def delete_veresiye(id):
    db.veresiye.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
