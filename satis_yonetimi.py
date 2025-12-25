from bson.objectid import ObjectId

def fatura_kes(db, data):
    parca_id = data.get('parcaId')
    adet = int(data.get('adet', 1))
    parca = db.products.find_one({"_id": ObjectId(parca_id)})
    
    if not parca: return {"ok": False}
    
    db.products.update_one({"_id": ObjectId(parca_id)}, {"$inc": {"stock": -adet}})
    
    try:
        satis_fiyati = float(str(data.get('fiyat', 0)).replace(',', '.'))
    except:
        satis_fiyati = 0.0
    
    toplam = satis_fiyati * adet
    
    fatura_verisi = {
        "ad": data['ad'],
        "tel": data.get('tel', '-'),
        "parca_ad": parca['name'],
        "adet": adet,
        "tarih": data['tarih'],
        "toplam": toplam
    }
    
    db.invoices.insert_one(fatura_verisi)
    db.customers.update_one(
        {"tel": data.get('tel')},
        {"$set": {"ad": data['ad'], "son_islem": data['tarih']}},
        upsert=True
    )
    return {"ok": True}
