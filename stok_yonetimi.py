from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId

stok_bp = Blueprint('stok_bp', __name__)
db = None

def init_db(db_instance):
    """Ana app.py'den gelen veritabanı bağlantısını tanımlar"""
    global db
    db = db_instance

@stok_bp.route('/api/products', methods=['GET', 'POST'])
def manage_products():
    try:
        if db is None:
            return jsonify({"status": "error", "message": "Veritabanı bağlantısı yok"}), 500

        if request.method == 'POST':
            data = request.json
            db.products.insert_one({
                "name": data['name'],
                "code": data['code'],
                "category": data.get('category', 'Genel'),
                "price": data.get('price', '0'),
                "stock": int(data.get('stock', 0))
            })
            return jsonify({"status": "success"})
        
        products = list(db.products.find())
        for p in products:
            p['_id'] = str(p['_id'])
        return jsonify(products)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@stok_bp.route('/api/products/update/<id>', methods=['POST'])
def update_stock(id):
    try:
        miktar = int(request.json.get('miktar', 0))
        db.products.update_one(
            {"_id": ObjectId(id)},
            {"$inc": {"stock": miktar}}
        )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@stok_bp.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    try:
        db.products.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})
