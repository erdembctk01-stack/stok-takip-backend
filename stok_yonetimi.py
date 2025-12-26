from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

def parca_ekle(db, data):
    adet = int(data.get('stock')) if data.get('stock') and str(data.get('stock')).strip() != "" else 1
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "description": data.get('description', '-'), # YENİ: Açıklama
        "compatible_cars": data.get('compatible_cars', '-'), # YENİ: Uyumlu Arabalar
        "stock": adet,
        "price": data.get('price', "0")
    })
    return {"ok": True}

# YENİ: Parça detaylarını düzenleme fonksiyonu (opsiyonel ileride kullanman için hazır)
def parca_duzenle(db, id, data):
    db.products.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"ok": True}
