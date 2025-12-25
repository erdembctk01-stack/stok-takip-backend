from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from app import db # Eski yöntemde db doğrudan app'den çekiliyordu

satis_bp = Blueprint('satis_bp', __name__)

@satis_bp.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    data = request.json
    # Eski mantık: Fiyatı veritabanından çekmeye çalışır veya limit koyar
    product = db.products.find_one({"_id": ObjectId(data['parcaId'])})
    
    satis_fiyati = float(product.get('price', 0)) # Fiyatı stoktan alıyordu
    adet = int(data.get('adet', 1))
    
    fatura = {
        "ad": data['ad'],
        "parca_ad": product['name'],
        "adet": adet,
        "toplam": satis_fiyati * adet,
        "tarih": datetime.now().strftime('%d.%m.%Y')
    }
    
    db.invoices.insert_one(fatura)
    return jsonify({"status": "success"})

@satis_bp.route('/api/invoices', methods=['GET'])
def get_invoices():
    invoices = list(db.invoices.find())
    for inv in invoices:
        inv['_id'] = str(inv['_id'])
    return jsonify(invoices)
