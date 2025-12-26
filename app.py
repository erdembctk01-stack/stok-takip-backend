import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import stok_yonetimi 
import satis_yonetimi

app = Flask(__name__, template_folder='templates')
CORS(app)

MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<col>', methods=['GET', 'POST'])
def handle_generic_api(col):
    if request.method == 'GET':
        items = list(db[col].find().sort('_id', -1))
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    
    data = request.json
    if col == 'products':
        return jsonify(stok_yonetimi.parca_ekle(db, data))
    
    db[col].insert_one(data)
    return jsonify({"ok": True})

@app.route('/api/products/update/<id>', methods=['POST'])
def update_stock(id):
    miktar = request.json.get('miktar', 0)
    return jsonify(stok_yonetimi.stok_guncelle(db, id, miktar))
    
@app.route('/api/products/edit/<id>', methods=['POST'])
def edit_product(id):
    data = request.json
    return jsonify(stok_yonetimi.parca_duzenle(db, id, data))

@app.route('/api/toplu-satis', methods=['POST'])
def toplu_satis():
    return jsonify(satis_yonetimi.toplu_fatura_kes(db, request.json))

@app.route('/api/import/<col>', methods=['POST'])
def import_data(col):
    data_list = request.json
    if isinstance(data_list, list):
        for item in data_list:
            if '_id' in item: del item['_id']
            db[col].insert_one(item)
    return jsonify({"ok": True})

@app.route('/api/reset-finance', methods=['POST'])
def reset_finance():
    db.invoices.delete_many({})
    db.expenses.delete_many({})
    return jsonify({"ok": True})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    db[col].delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    invoices = list(db.invoices.find())
    expenses = list(db.expenses.find())
    products = list(db.products.find())
    
    def temizle(val):
        try: return float(str(val).replace('₺','').replace(' ','').replace(',','.'))
        except: return 0.0

    kazanc = sum(temizle(i.get('toplam', 0)) for i in invoices)
    gider = sum(temizle(e.get('tutar', 0)) for e in expenses)
    depo = sum(int(p.get('stock', 0)) * temizle(p.get('price', 0)) for p in products)

    return jsonify({"kazanc": f"₺{kazanc:,.2f}", "gider": f"₺{gider:,.2f}", "depo": f"₺{depo:,.2f}"})

if __name__ == '__main__':
    # Render için kritik düzeltme: Portu çevresel değişkenden al, hostu 0.0.0.0 yap
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
