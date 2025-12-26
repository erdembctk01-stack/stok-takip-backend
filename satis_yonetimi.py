from bson.objectid import ObjectId

def toplu_fatura_kes(db, data):
    ad = data.get('ad')
    tel = data.get('tel', '-')
    items = data.get('items', [])
    tarih = data.get('tarih')
    
    toplam_tutar = 0
    parca_isimleri = []

    for item in items:
        p_id = item['parcaId']
        adet = int(item['adet'])
        fiyat = float(str(item['fiyat']).replace(',','.'))
        db.products.update_one({"_id": ObjectId(p_id)}, {"$inc": {"stock": -adet}})
        toplam_tutar += (adet * fiyat)
        parca_isimleri.append(f"{item['name']} (x{adet})")

    db.invoices.insert_one({
        "ad": ad, "tel": tel, "parca_ad": ", ".join(parca_isimleri),
        "tarih": tarih, "toplam": toplam_tutar
    })
    
    db.customers.update_one({"tel": tel}, {"$set": {"ad": ad, "son_islem": tarih}}, upsert=True)
    return {"ok": True}

def fatura_kes(db, data):
    # Tekli satış fonksiyonu (Geriye dönük uyumluluk için duruyor)
    parca = db.products.find_one({"_id": ObjectId(data['parcaId'])})
    db.products.update_one({"_id": ObjectId(data['parcaId'])}, {"$inc": {"stock": -int(data['adet'])}})
    db.invoices.insert_one({
        "ad": data['ad'], "tel": data['tel'], "parca_ad": parca['name'],
        "tarih": data['tarih'], "toplam": float(str(data['fiyat']).replace(',','.')) * int(data['adet'])
    })
    return {"ok": True}
