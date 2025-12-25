from bson.objectid import ObjectId

def stok_listele(db):
    items = list(db.products.find())
    for i in items:
        i['_id'] = str(i['_id'])
        i['stock'] = int(i.get('stock', 0))
    return items

def genel_sil(db, col, id):
    db[col].delete_one({"_id": ObjectId(id)})
    return {"ok": True}
