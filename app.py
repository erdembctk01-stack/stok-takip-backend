from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

from satis_yonetimi import satis_bp, init_db as satis_init
from stok_yonetimi import stok_bp, init_db as stok_init

app = Flask(__name__)

# DNS ve Bağlantı Sorunlarını Çözen Bağlantı
MONGO_URI = "mongodb+srv://ozcanoto:eren9013@cluster0.mongodb.net/ozcan_oto?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, connect=False, serverSelectionTimeoutMS=5000)
db = client.ozcan_oto

# Alt modüllere veritabanı yetkisi ver
satis_init(db)
stok_init(db)
app.register_blueprint(satis_bp)
app.register_blueprint(stok_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard-stats')
def get_stats():
    try:
        inv = list(db.invoices.find())
        kazanc = sum(float(i.get('toplam', 0)) for i in inv)
        exp = list(db.expenses.find())
        gider = sum(float(e.get('tutar', 0)) for e in exp)
        prd = list(db.products.find())
        depo = sum(int(p.get('stock', 0)) * float(str(p.get('price', 0)).replace(',','.')) for p in prd)
        
        return jsonify({
            "kazanc": f"₺{kazanc:,.2f}".replace(',','X').replace('.',',').replace('X','.'),
            "gider": f"₺{gider:,.2f}".replace(',','X').replace('.',',').replace('X','.'),
            "depo": f"₺{depo:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        })
    except:
        return jsonify({"kazanc": "₺0,00", "gider": "₺0,00", "depo": "₺0,00"})

@app.route('/api/expenses', methods=['GET', 'POST'])
def manage_expenses():
    if request.method == 'POST':
        db.expenses.insert_one({"aciklama": request.json['aciklama'], "tutar": float(request.json['tutar']), "tarih": datetime.now().strftime('%d.%m.%Y')})
        return jsonify({"status": "success"})
    e_list = list(db.expenses.find())
    for e in e_list: e['_id'] = str(e['_id'])
    return jsonify(e_list)

@app.route('/api/expenses/<id>', methods=['DELETE'])
def del_exp(id):
    db.expenses.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
