from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": int(miktar)}})
    return {"ok": True}

def parca_duzenle(db, id, data):
    # Kritik Düzeltme: Front-end'den gelen verileri güvenli çekme
    update_data = {
        "name": data.get('name'),
        "code": data.get('code'),
        "category": data.get('category'),
        "price": data.get('price'),
        "desc": data.get('desc', ''),
        "compat": data.get('compat', '')
    }
    
    # Boş verileri temizle (opsiyonel ama önerilir)
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    db.products.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return {"ok": True}

def parca_ekle(db, data):
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "desc": data.get('desc', ''),
        "compat": data.get('compat', ''),
        "stock": int(data.get('stock', 0)),
        "price": data.get('price', "0")
    })
    return {"ok": True}
