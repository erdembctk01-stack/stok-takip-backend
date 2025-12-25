@app.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    data = request.json
    # Parça bilgilerini çekiyoruz
    product = db.products.find_one({"_id": ObjectId(data['parcaId'])})
    
    # Arayüzden gelen fiyatı alıyoruz (Eğer boşsa 0 kabul et)
    # float(data['fiyat']) sayesinde 1 TL yazarsan 1 TL olarak işlenir
    satis_fiyati = float(data.get('fiyat', 0))
    adet = int(data.get('adet', 1))
    toplam_tutar = satis_fiyati * adet

    fatura = {
        "ad": data['ad'],
        "tel": data.get('tel', ""),
        "parca_id": data['parcaId'],
        "parca_ad": product['name'],
        "adet": adet,
        "birim_fiyat": satis_fiyati,
        "toplam": toplam_tutar,
        "tarih": data['tarih']
    }
    
    # Faturayı kaydet
    db.invoices.insert_one(fatura)
    
    # Stoktan düş
    db.products.update_one(
        {"_id": ObjectId(data['parcaId'])},
        {"$inc": {"stock": -adet}}
    )
    
    # Cari rehbere ekle (Yoksa)
    if data['ad']:
        db.customers.update_one(
            {"ad": data['ad']},
            {"$set": {"tel": data.get('tel', "")}},
            upsert=True
        )
        
    return jsonify({"status": "success"})
