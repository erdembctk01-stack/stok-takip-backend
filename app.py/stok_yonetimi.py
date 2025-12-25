from bson.objectid import ObjectId

def stok_listele(db):
    items = list(db.products.find())
    for i in items:
        i['_id'] = str(i['_id'])
    return items

def stok_sil(db, id):
    db.products.delete_one({"_id": ObjectId(id)})
    return {"ok": True}
