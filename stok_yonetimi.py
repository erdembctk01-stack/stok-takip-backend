from bson.objectid import ObjectId

def stok_listele(db):
    items = list(db.products.find())
    for i in items:
        i['_id'] = str(i['_id'])
        i['stock'] = int(i.get('stock', 0))
        i['category'] = i.get('category', 'Genel')
        i['code'] = i.get('code', '-')
    return items

def stok_guncelle(db, id, miktar):
    # miktar pozitifse artırır, negatifse azaltır
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

def parca_ekle(db, data):
    # Adet boşsa 1 kabul et
    adet = int(data.get('stock')) if data.get('stock') else 1
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "stock": adet,
        "price": data.get('price', "0")
    })
    return {"ok": True}
