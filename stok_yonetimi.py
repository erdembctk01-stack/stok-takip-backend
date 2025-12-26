from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

def parca_ekle(db, data):
    # Stock değerini kontrol et ve sayıya çevir
    try:
        adet = int(data.get('stock')) if data.get('stock') else 1
    except:
        adet = 1

    db.products.insert_one({
        "name": data.get('name'),
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "stock": adet,
        "price": data.get('price', "0"),
        "description": data.get('description', ''),   # Yeni alan
        "compatibility": data.get('compatibility', '') # Yeni alan
    })
    return {"ok": True}
