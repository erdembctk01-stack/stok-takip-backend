from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

# DOSYA BAĞLANTILARI
from satis_yonetimi import satis_bp, init_db as satis_init
from stok_yonetimi import stok_bp, init_db as stok_init

app = Flask(__name__)

# MONGODB BAĞLANTISI
# DNS hatalarını önlemek için connect=False eklendi ve parametreler düzeltildi
MONGO_URI = "mongodb+srv://ozcanoto:eren9013@cluster0.mongodb.net/ozcan_oto?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, connect=False)
    db = client.ozcan_oto
    # Uygulama başladığında db'nin varlığını garanti ediyoruz
    satis_init(db)
    stok_init(db)
    print("MongoDB Yapılandırması Tamamlandı.")
except Exception as e:
    print(f"Bağlantı Kurulamadı: {e}")
    db = None

app.register_blueprint(satis_bp)
app.register_blueprint(stok_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    try:
        if db is None: return jsonify({"kazanc": "₺0,00", "gider": "₺0,00", "depo": "₺0,00"})
        
        invoices = list(db.invoices.find())
        toplam_kazanc = sum(float(inv.get('toplam', 0)) for inv in invoices)
        
        expenses = list(db.expenses.find())
        toplam_gider = sum(float(exp.get('tutar', 0)) for exp in expenses)
        
        products = list(db.products.find())
        stok_degeri = sum(int(p.get('stock', 0)) * float(str(p.get('price', 0)).replace(',', '.')) for p in products)
        
        def format_tl(tutar):
            return f"₺{tutar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        return jsonify({
            "kazanc": format_tl(toplam_kazanc),
            "gider": format_tl(toplam_gider),
            "depo": format_tl(stok_degeri)
        })
    except:
        return jsonify({"kazanc": "₺0,00", "gider": "₺0,00", "depo": "₺0,00"})

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
    for e in expenses: e['_id'] = str(e['_id'])
    return jsonify(expenses)

@app.route('/api/expenses/<id>', methods=['DELETE'])
def delete_expense(id):
    db.expenses.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = list(db.customers.find())
    for c in customers: c['_id'] = str(c['_id'])
    return jsonify(customers)

@app.route('/api/customers/<id>', methods=['DELETE'])
def delete_customer(id):
    db.customers.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

@app.route('/api/veresiye', methods=['GET', 'POST'])
def manage_veresiye():
    if request.method == 'POST':
        data = request.json
        db.veresiye.insert_one({
            "ad": data['ad'], "tel": data['tel'], "islem": data['islem'],
            "para": data['para'], "tarih": datetime.now().strftime('%d.%m.%Y')
        })
        return jsonify({"status": "success"})
    v_list = list(db.veresiye.find())
    for v in v_list: v['_id'] = str(v['_id'])
    return jsonify(v_list)

@app.route('/api/veresiye/<id>', methods=['DELETE'])
def delete_veresiye(id):
    db.veresiye.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
