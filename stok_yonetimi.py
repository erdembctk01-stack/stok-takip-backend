from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

def parca_duzenle(db, id, data):
    # FİYAT HARİÇ her şeyi günceller
    update_data = {
        "name": data.get('name'),
        "code": data.get('code'),
        "category": data.get('category'),
        "desc": data.get('desc', ''),        # Yeni: Açıklama
        "compat": data.get('compat', '')     # Yeni: Uyumlu Araç
    }
    db.products.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return {"ok": True}

def parca_ekle(db, data):
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "desc": data.get('desc', ''),        # Yeni: Açıklama
        "compat": data.get('compat', ''),    # Yeni: Uyumlu Araç
        "stock": int(data.get('stock', 1)),
        "price": data.get('price', "0")
    })
    return {"ok": True}
