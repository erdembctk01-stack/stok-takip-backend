from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Bağlantısı - Kendi linkini tırnak içine yapıştırdığından emin ol!
client = MongoClient("BURAYA_KENDI_MONGODB_LINKINI_YAPISTIR")
db = client.stok_veritabani

# Yeni eklediğimiz ana sayfa rotası
@app.route('/')
def home():
    return "<h1>Sistem Calisiyor!</h1><p>Butonlarin calismasi icin bilgisayarindaki index.html dosyasini kullanin.</p>"

@app.route('/products', methods=['GET'])
def list_products():
    items = list(db.products.find())
    for i in items: 
        i['_id'] = str(i['_id'])
    return jsonify(items)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    doc = {
        "name": data.get("name"),
        "stock": int(data.get("stock", 0)),
        "price": float(data.get("price", 0)),
        "category": data.get("category", "Genel"),
        "critical_limit": int(data.get("critical_limit", 10))
    }
    res = db.products.insert_one(doc)
    return jsonify({"id": str(res.inserted_id)})

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    # Render'ın otomatik atadığı portu kullanır
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
