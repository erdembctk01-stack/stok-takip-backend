# DASHBOARD HESAPLAMALARI
@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    # Toplam Kazanç (Invoices üzerinden)
    invoices = list(db.invoices.find())
    # Sayısal değerleri toplarken virgül/nokta hatasını önlüyoruz
    toplam_kazanc = sum(float(str(i.get('toplam', 0)).replace(',', '.')) for i in invoices)
    
    # Depo Değeri (Products üzerinden)
    products = list(db.products.find())
    depo_degeri = sum(int(p.get('stock', 0)) * float(str(p.get('price', 0)).replace(',', '.')) for p in products)
    
    return jsonify({
        "kazanc": f"₺{toplam_kazanc:,.2f}",
        "depo": f"₺{depo_degeri:,.2f}"
    })
