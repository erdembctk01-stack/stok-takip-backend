from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId

stok_bp = Blueprint('stok_bp', __name__)
db = None

def init_db(db_instance):
    global db
    db = db_instance

@stok_bp.route('/api/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        db.products.insert_one({
            "name": request.json['name'],
            "code": request.json['code'],
            "category": request.json.get('category', 'Genel'),
            "price": request.json.get('price', '0'),
            "stock": int(request.json.get('stock', 0))
        })
        return jsonify({"status": "success"})
    p_list = list(db.products.find())
    for p in p_list: p['_id'] = str(p['_id'])
    return jsonify(p_list)

@stok_bp.route('/api/products/update/<id>', methods=['POST'])
def update_p(id):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": int(request.json['miktar'])}})
    return jsonify({"status": "success"})

@stok_bp.route('/api/products/<id>', methods=['DELETE'])
def del_p(id):
    db.products.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})
