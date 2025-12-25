from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime

satis_bp = Blueprint('satis_bp', __name__)
db = None

def init_db(db_instance):
    global db
    db = db_instance

@satis_bp.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    data = request.json
    product = db.products.find_one({"_id": ObjectId(data['parcaId'])})
    fiyat = float(str(data.get('fiyat', '0')).replace(',','.'))
    adet = int(data.get('adet', 1))
    
    db.invoices.insert_one({
        "ad": data.get('ad', 'Müşteri'),
        "tel": data.get('tel', ''),
        "parca_ad": product['name'],
        "adet": adet,
        "toplam": fiyat * adet,
        "tarih": datetime.now().strftime('%d.%m.%Y %H:%M')
    })
    db.products.update_one({"_id": ObjectId(data['parcaId'])}, {"$inc": {"stock": -adet}})
    return jsonify({"status": "success"})

@satis_bp.route('/api/invoices', methods=['GET'])
def get_inv():
    inv = list(db.invoices.find().sort("_id", -1))
    for i in inv: i['_id'] = str(i['_id'])
    return jsonify(inv)

@satis_bp.route('/api/invoices/<id>', methods=['DELETE'])
def del_inv(id):
    db.invoices.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})
