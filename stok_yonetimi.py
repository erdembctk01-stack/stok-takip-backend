from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    # Mevcut miktar üzerine ekleme/çıkarma yapar (+/-)
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

def parca_duzenle(db, id, data):
    # Kullanıcının talebi üzerine stok hariç her şeyi düzenler
    db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": data.get('name'),
            "code": data.get('code', '-'),
            "category": data.get('category', 'Genel'),
            "price": data.get('price', "0")
        }}
    )
    return {"ok": True}

def parca_ekle(db, data):
    # Orijinal parça ekleme fonksiyonu (hiçbir satırı değişmedi)
    adet = int(data.get('stock')) if data.get('stock') and str(data.get('stock')).strip() != "" else 1
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "stock": adet,
        "price": data.get('price', "0")
    })
    return {"ok": True}
