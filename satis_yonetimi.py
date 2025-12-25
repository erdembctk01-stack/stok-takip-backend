from bson.objectid import ObjectId

def fatura_kes(db, data):
    parca_id = data.get('parcaId')
    adet = int(data.get('adet', 0))
    parca = db.products.find_one({"_id": ObjectId(parca_id)})
    
    if not parca: return {"ok": False, "error": "Parça bulunamadı"}
    
    # Stok Güncelleme
    yeni_stok = int(parca.get('stock', 0)) - adet
    db.products.update_one({"_id": ObjectId(parca_id)}, {"$set": {"stock": yeni_stok}})
    
    # Detaylı Fatura Kaydı
    db.invoices.insert_one({
        "musteri": data['ad'],
        "parca_ad": parca['name'],
        "adet": adet,
        "fiyat": parca['price'],
        "toplam": float(parca['price'].replace(',','.')) * adet if parca.get('price') else 0,
        "tarih": data['tarih']
    })
    return {"ok": True}

def satis_gecmisi(db):
    items = list(db.invoices.find())
    for i in items: i['_id'] = str(i['_id'])
    return items
