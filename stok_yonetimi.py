from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId

stok_bp = Blueprint('stok_bp', __name__)

from app import db

@stok_bp.route('/api/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        data = request.json
        db.products.insert_one({
            "name": data['name'],
            "code": data['code'],
            "price": data['price'],
            "stock": int(data['stock'])
        })
        return jsonify({"status": "success"})
    
    products = list(db.products.find())
    for p in products:
        p['_id'] = str(p['_id'])
    return jsonify(products)

@stok_bp.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})
