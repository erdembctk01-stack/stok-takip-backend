from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# ÖNEMLİ: MongoDB linkini tırnak içine yapıştır
client = MongoClient("BURAYA_MONGODB_LINKINI_YAPISTIR")
db = client.stok_takip

@app.route('/')
def index():
    return "Sunucu Calisiyor"

@app.route('/products', methods=['GET'])
def get_products():
    items = list(db.products.find())
    for i in items:
        i['_id'] = str(i['_id'])
    return jsonify(items)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    res = db.products.insert_one(data)
    return jsonify({"id": str(res.inserted_id)})

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "silindi"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
