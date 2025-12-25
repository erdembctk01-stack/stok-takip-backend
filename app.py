from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- MONGODB BAĞLANTISI ---
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

@app.route('/')
def index():
    # Flask otomatik olarak templates klasöründeki index.html'i arar
    return render_template('index.html')

@app.route('/api/<col>', methods=['GET', 'POST'])
def handle_api(col):
    if request.method == 'GET':
        items = list(db[col].find())
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    db[col].insert_one(request.json)
    return jsonify({"ok": True})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    db[col].delete_one({"_id": ObjectId(id)})
    return jsonify({"ok": True})

@app.route('/api/fatura-kes', methods=['POST'])
def fatura_kes():
    try:
        data = request.json
        parca_id = data.get('parcaId')
        adet = int(data.get('adet', 0))
        parca = db.products.find_one({"_id": ObjectId(parca_id)})
        current_stock = int(parca.get('stock', 0))
        db.products.update_one({"_id": ObjectId(parca_id)}, {"$set": {"stock": current_stock - adet}})
        db.invoices.insert_one({"ad": data['ad'], "tel": data['tel'], "parca_id": parca_id, "parca_ad": parca['name'], "adet": adet, "tarih": data['tarih']})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)
