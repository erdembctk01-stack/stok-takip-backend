import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import stok_yonetimi 
import satis_yonetimi

app = Flask(__name__, template_folder='templates')
CORS(app)

# MongoDB Bağlantısı
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<col>', methods=['GET', 'POST'])
def handle_generic_api(col):
    if request.method == 'GET':
        items = list(db[col].find())
        for i in items: i['_id'] = str(i['_id'])
        return jsonify(items)
    db[col].insert_one(request.json)
    return jsonify({"ok": True})

@app.route('/api/<col>/<id>', methods=['DELETE'])
def handle_delete(col, id):
    return jsonify(stok_yonetimi.genel_sil(db, col, id))

@app.route('/api/fatura-kes', methods=['POST'])
def post_fatura():
    return jsonify(satis_yonetimi.fatura_kes(db, request.json))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
