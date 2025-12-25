from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
import sys

# satis_yonetimi.py - TAM HALİ
satis_bp = Blueprint('satis_bp', __name__)

# Veritabanı referansı için global bir değişken
db = None

def init_db(database_instance):
    """Ana app.py'den gelen db bağlantısını buraya aktarır"""
    global db
    db = database_instance

@satis_bp.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    try:
        global db
        data = request.json
        
        # Parça bilgilerini çekiyoruz
        product = db.products.find_one({"_id": ObjectId(data['parcaId'])})
        
        if not product:
            return jsonify({"status": "error", "message": "Parça bulunamadı"}), 404

        # Kullanıcının girdiği fiyatı alıyoruz (HİÇBİR SINIRLAMA YOKTUR)
        try:
            # Gelen verideki virgülü noktaya çevirip sayıya dönüştürür
            raw_fiyat = str(data.get('fiyat', '0')).replace(',', '.')
            satis_fiyati = float(raw_fiyat)
        except:
            satis_fiyati = 0.0

        adet = int(data.get('adet', 1))
        toplam_tutar = satis_fiyati * adet

        fatura = {
            "ad": data.get('ad', 'İsimsiz Müşteri'),
            "tel": data.get('tel', ""),
            "parca_id": data['parcaId'],
            "parca_ad": product['name'],
            "adet": adet,
            "birim_fiyat": satis_fiyati,
            "toplam": toplam_tutar,
            "tarih": data.get('tarih', datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        }
        
        # 1. Faturayı kaydet
        db.invoices.insert_one(fatura)
        
        # 2. Stoktan düş
        db.products.update_one(
            {"_id": ObjectId(data['parcaId'])},
            {"$inc": {"stock": -adet}}
        )
        
        # 3. Müşteriyi Cari Rehber'e ekle/güncelle
        if data.get('ad'):
            db.customers.update_one(
                {"ad": data['ad']},
                {"$set": {"tel": data.get('tel', "")}},
                upsert=True
            )
            
        return jsonify({"status": "success", "message": "Satış başarıyla kaydedildi"})
    except Exception as e:
        print(f"HATA: {str(e)}") # Loglarda hatayı görmek için
        return jsonify({"status": "error", "message": str(e)}), 500

@satis_bp.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        invoices = list(db.invoices.find().sort("_id", -1)) # En yeni en üstte
        for inv in invoices:
            inv['_id'] = str(inv['_id'])
        return jsonify(invoices)
    except:
        return jsonify([])

@satis_bp.route('/api/invoices/<id>', methods=['DELETE'])
def delete_invoice(id):
    try:
        db.invoices.delete_one({"_id": ObjectId(id)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})

@satis_bp.route('/api/reset-finance', methods=['POST'])
def reset_finance():
    try:
        db.invoices.delete_many({})
        db.expenses.delete_many({})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"})
