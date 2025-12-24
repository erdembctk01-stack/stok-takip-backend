from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Bağlantısı (Kendi linkini buraya koy)
app.config["MONGO_URI"] = "BURAYA_KENDI_MONGODB_LINKINI_YAPISTIR"
mongo = PyMongo(app)

@app.route('/products', methods=['GET'])
def get_products():
    products = list(mongo.db.products.find())
    for p in products:
        p['_id'] = str(p['_id'])
    return jsonify(products)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    # Görseldeki yapıya uygun veriler
    new_product = {
        "name": data.get("name"),
        "stock": int(data.get("stock", 0)),
        "price": float(data.get("price", 0)),
        "category": data.get("category", "Genel")
    }
    result = mongo.db.products.insert_one(new_product)
    return jsonify({"_id": str(result.inserted_id)}), 201

@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    mongo.db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "Silindi"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
