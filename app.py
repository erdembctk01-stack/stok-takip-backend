from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB Bağlantısı (DNS hataları için connect=False eklendi)
MONGO_URI = "mongodb+srv://ozcanoto:eren9013@cluster0.mongodb.net/ozcan_oto?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, connect=False)
db = client.ozcan_oto

# DOSYA BAĞLANTILARI - init_db kullanarak db nesnesini gönderiyoruz
from satis_yonetimi import satis_bp, init_db as satis_init
from stok_yonetimi import stok_bp, init_db as stok_init

# Veritabanı yetkisini alt dosyalara aktar
satis_init(db)
stok_init(db)

app.register_blueprint(satis_bp)
app.register_blueprint(stok_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    try:
        invoices = list(db.invoices.find())
        kazanc = sum(inv.get('toplam', 0) for inv in invoices)
        expenses = list(db.expenses.find())
        gider = sum(exp.get('tutar', 0) for exp in expenses)
        return jsonify({"kazanc": f"₺{kazanc}", "gider": f"₺{gider}", "depo": "₺0"})
    except:
        return jsonify({"kazanc": "₺0", "gider": "₺0", "depo": "₺0"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
