from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

def parca_duzenle(db, id, data):
    # Stok (miktar) hariç diğer tüm alanları günceller
    update_data = {
        "name": data.get('name'),
        "code": data.get('code'),
        "category": data.get('category'),
        "price": data.get('price')
    }
    db.products.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return {"ok": True}

def parca_ekle(db, data):
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "stock": int(data.get('stock', 1)),
        "price": data.get('price', "0")
    })
    return {"ok": True}
