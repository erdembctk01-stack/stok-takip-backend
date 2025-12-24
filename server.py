from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Her yerden güvenli erişim

# MongoDB Bağlantısı
MONGO_URL = "SENIN_MONGODB_LINKIN" # <--- Burayı kendi linkinle değiştir
client = MongoClient(MONGO_URL)
db = client.stok_veritabani

@app.route('/products', methods=['GET'])
def list_products():
    try:
        items = list(db.products.find())
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(data=items, status="success"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        # Profesyonel veri yapısı
        doc = {
            "name": data.get("name"),
            "stock": int(data.get("stock", 0)),
            "price": float(data.get("price", 0)),
            "category": data.get("category", "Genel"),
            "sku": data.get("sku", "YOK")
        }
        res = db.products.insert_one(doc)
        return jsonify(id=str(res.inserted_id), status="created"), 201
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify(status="deleted"), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
