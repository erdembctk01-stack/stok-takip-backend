from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

# DOSYA BAĞLANTILARI
from satis_yonetimi import satis_bp
from stok_yonetimi import stok_bp

app = Flask(__name__)

# MONGODB BAĞLANTISI
MONGO_URI = "mongodb+srv://ozcanoto:eren9013@cluster0.mongodb.net/ozcan_oto?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client.ozcan_oto

# BLUEPRINT KAYITLARI
app.register_blueprint(satis_bp)
app.register_blueprint(stok_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    # Eski mantık: Sadece veritabanındaki toplamları döner
    invoices = list(db.invoices.find())
    kazanc = sum(inv.get('toplam', 0) for inv in invoices)
    
    expenses = list(db.expenses.find())
    gider = sum(exp.get('tutar', 0) for exp in expenses)
    
    return jsonify({
        "kazanc": f"₺{kazanc}",
        "gider": f"₺{gider}",
        "depo": "₺0"
    })

if __name__ == '__main__':
    app.run(debug=True)
