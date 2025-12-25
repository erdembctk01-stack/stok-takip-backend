from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime

satis_bp = Blueprint('satis_bp', __name__)
db = None

def init_db(database_instance):
    global db
    db = database_instance

@satis_bp.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    data = request.json
    product = db.products.find_one({"_id": ObjectId(data['parcaId'])})
    
    # Eski mantık: Fiyatı sadece stoktan çeker
    satis_fiyati = float(product.get('price', 0))
    adet = int(data.get('adet', 1))
    
    fatura = {
        "ad": data['ad'],
        "parca_ad": product['name'],
        "adet": adet,
        "toplam": satis_fiyati * adet,
        "tarih": datetime.now().strftime('%d.%m.%Y')
    }
    
    db.invoices.insert_one(fatura)
    db.products.update_one({"_id": ObjectId(data['parcaId'])}, {"$inc": {"stock": -adet}})
    return jsonify({"status": "success"})

@satis_bp.route('/api/invoices', methods=['GET'])
def get_invoices():
    invoices = list(db.invoices.find())
    for inv in invoices:
        inv['_id'] = str(inv['_id'])
    return jsonify(invoices)

@satis_bp.route('/api/invoices/<id>', methods=['DELETE'])
def delete_invoice(id):
    db.invoices.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "success"})
