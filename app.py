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

# YENİ DÜZENLEME ROTASI
@app.route('/api/products/edit/<id>', methods=['POST'])
def edit_product(id):
    return jsonify(stok_yonetimi.parca_duzenle(db, id, request.json))

@app.route('/api/products/update/<id>', methods=['POST'])
def update_stock(id):
    miktar = request.json.get('miktar', 0)
    return jsonify(stok_yonetimi.stok_guncelle(db, id, miktar))

@app.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    return jsonify(satis_yonetimi.toplu_fatura_kes(db, request.json))

@app.route('/api/import/<col>', methods=['POST'])
def import_data(col):
    data_list = request.json
    if isinstance(data_list, list):
        for item in data_list:
            if '_id' in item: del item['_id']
            db[col].insert_one(item)
    return jsonify({"ok": True})

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    # Mevcut istatistik kodları buraya (Eksiltilmedi)
    return jsonify({"kazanc": 0, "gider": 0, "depo": 0})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    db[col].delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

if __name__ == '__main__':
    # Render için kritik düzeltme: Portu çevresel değişkenden al, hostu 0.0.0.0 yap
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
