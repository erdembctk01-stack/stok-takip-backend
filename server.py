from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Bağlantısı - Kendi linkini tırnak içine yapıştır!
client = MongoClient("BURAYA_KENDI_MONGODB_LINKINI_YAPISTIR")
db = client.stok_veritabani

@app.route('/products', methods=['GET'])
def listele():
    urunler = list(db.products.find())
    for u in urunler: u['_id'] = str(u['_id'])
    return jsonify(urunler)

@app.route('/products', methods=['POST'])
def ekle():
    data = request.json
    # Profesyonel veri yapısı
    yeni_urun = {
        "name": data.get("name"),
        "stock": int(data.get("stock", 0)),
        "price": float(data.get("price", 0)),
        "category": data.get("category", "Genel")
    }
    res = db.products.insert_one(yeni_urun)
    return jsonify({"id": str(res.inserted_id)}), 201

@app.route('/products/<id>', methods=['DELETE'])
def sil(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"durum": "silindi"}), 200

if __name__ == '__main__':
    # Render'ın istediği port ayarı
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
