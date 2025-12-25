from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime

# Veritabanı bağlantısının app.py üzerinden geldiğini varsayıyoruz
# Eğer bu dosya bağımsız çalışıyorsa db tanımı buraya eklenmelidir.
from app import db 

satis_bp = Blueprint('satis_bp', __name__)

@satis_bp.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    try:
        data = request.json
        # Parça bilgilerini çekiyoruz
        product = db.products.find_one({"_id": ObjectId(data['parcaId'])})
        
        if not product:
            return jsonify({"status": "error", "message": "Parça bulunamadı"}), 404

        # Arayüzden gelen fiyatı alıyoruz (Limit yoktur, 1 TL bile yazılabilir)
        satis_fiyati = float(data.get('fiyat', 0))
        adet = int(data.get('adet', 1))
        toplam_tutar = satis_fiyati * adet

        fatura = {
            "ad": data['ad'],
            "tel": data.get('tel', ""),
            "parca_id": data['parcaId'],
            "parca_ad": product['name'],
            "adet": adet,
            "birim_fiyat": satis_fiyati,
            "toplam": toplam_tutar,
            "tarih": data.get('tarih', datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        }
        
        # Faturayı kaydet
        db.invoices.insert_one(fatura)
        
        # Stoktan düş
        db.products.update_one(
            {"_id": ObjectId(data['parcaId'])},
            {"$inc": {"stock": -adet}}
        )
        
        # Müşteriyi Cari Rehber'e ekle veya güncelle
        if data['ad']:
            db.customers.update_one(
                {"ad": data['ad']},
                {"$set": {"tel": data.get('tel', "")}},
                upsert=True
            )
            
        return jsonify({"status": "success", "message": "Satış başarıyla kaydedildi"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

@satis_bp.route('/api/reset-finance', methods=['POST'])
def reset_finance():
    # Finansal verileri sıfırla (Faturalar ve Giderler silinir)
    db.invoices.delete_many({})
    db.expenses.delete_many({})
    return jsonify({"status": "success"})
