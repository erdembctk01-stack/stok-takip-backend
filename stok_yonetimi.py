from bson.objectid import ObjectId

def stok_guncelle(db, id, miktar):
    db.products.update_one({"_id": ObjectId(id)}, {"$inc": {"stock": miktar}})
    return {"ok": True}

from bson.objectid import ObjectId

def parca_duzenle(db, id, data):
    guncellenecek = {}

    if "name" in data:
        guncellenecek["name"] = data["name"]

    if "code" in data:
        guncellenecek["code"] = data["code"]

    if "category" in data:
        guncellenecek["category"] = data["category"]

    if "price" in data:
        guncellenecek["price"] = float(data["price"])

    if "desc" in data:
        guncellenecek["desc"] = data["desc"]

    if "compat" in data:
        guncellenecek["compat"] = data["compat"]

    if not guncellenecek:
        return {"ok": False, "msg": "Güncellenecek veri yok"}

    db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": guncellenecek}
    )

    return {"ok": True}
    
    }
    db.products.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return {"ok": True}

def parca_ekle(db, data):
    db.products.insert_one({
        "name": data['name'],
        "code": data.get('code', '-'),
        "category": data.get('category', 'Genel'),
        "desc": data.get('desc', ''),
        "compat": data.get('compat', ''),
        "stock": int(data.get('stock', 1)),
        "price": data.get('price', "0")
    })
    return {"ok": True}
