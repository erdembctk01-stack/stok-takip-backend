from bson.objectid import ObjectId

def fatura_kes(db, data):
    try:
        parca_id = data.get('parcaId')
        adet = int(data.get('adet', 0))
        parca = db.products.find_one({"_id": ObjectId(parca_id)})
        
        # Stoktan Düşme
        yeni_stok = int(parca.get('stock', 0)) - adet
        db.products.update_one({"_id": ObjectId(parca_id)}, {"$set": {"stock": yeni_stok}})
        
        # Fatura Kaydı (Tüm detaylarıyla)
        db.invoices.insert_one({
            "ad": data['ad'],
            "tel": data.get('tel', ''),
            "parca_ad": parca['name'],
            "adet": adet,
            "tarih": data['tarih'],
            "fiyat": parca.get('price', 0)
        })
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
