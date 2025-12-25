from bson.objectid import ObjectId

def fatura_kes(db, data):
    parca_id = data.get('parcaId')
    adet = int(data.get('adet', 1))
    parca = db.products.find_one({"_id": ObjectId(parca_id)})
    
    if not parca: return {"ok": False}
    
    # Stok Düş
    db.products.update_one({"_id": ObjectId(parca_id)}, {"$inc": {"stock": -adet}})
    
    fiyat = float(str(parca.get('price', 0)).replace('.', '').replace(',', '.'))
    toplam = fiyat * adet
    
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
