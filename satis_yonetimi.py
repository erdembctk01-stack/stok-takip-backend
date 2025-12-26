from bson.objectid import ObjectId

def toplu_fatura_kes(db, data):
    ad = data.get('ad')
    tel = data.get('tel', '-')
    items = data.get('items', [])
    tarih = data.get('tarih')
    
    toplam_fatura = 0
    parca_isimleri = []

    for item in items:
        p_id = item['parcaId']
        adet = int(item['adet'])
        fiyat = float(item['fiyat'])
        
        # Stoktan düş
        db.products.update_one({"_id": ObjectId(p_id)}, {"$inc": {"stock": -adet}})
        
        toplam_fatura += (adet * fiyat)
        parca_isimleri.append(f"{item['name']} (x{adet})")

    db.invoices.insert_one({
        "ad": ad,
        "tel": tel,
        "parca_ad": ", ".join(parca_isimleri),
        "tarih": tarih,
        "toplam": toplam_fatura
    })
    
    db.customers.update_one(
        {"tel": tel},
        {"$set": {"ad": ad, "son_islem": tarih}},
        upsert=True
    )
    return {"ok": True}
