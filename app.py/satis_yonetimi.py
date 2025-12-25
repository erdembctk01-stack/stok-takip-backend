from bson.objectid import ObjectId

def fatura_kes(db, data):
    parca_id = data.get('parcaId')
    adet = int(data.get('adet', 0))
    parca = db.products.find_one({"_id": ObjectId(parca_id)})
    
    current_stock = int(parca.get('stock', 0))
    db.products.update_one({"_id": ObjectId(parca_id)}, {"$set": {"stock": current_stock - adet}})
    
    db.invoices.insert_one({
        "ad": data['ad'], 
        "parca_ad": parca['name'], 
        "adet": adet, 
        "tarih": data['tarih']
    })
    return {"ok": True}
