import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import stok_yonetimi 
import satis_yonetimi

app = Flask(__name__)
CORS(app)

# MongoDB Bağlantısı
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

@app.route('/')
def index():
    # Burası beyaz ekranı önleyen kısımdır. templates/index.html'i çağırır.
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_stok():
    return jsonify(stok_yonetimi.stok_listele(db))

@app.route('/api/products/<id>', methods=['DELETE'])
def delete_stok(id):
    return jsonify(stok_yonetimi.stok_sil(db, id))

@app.route('/api/fatura-kes', methods=['POST'])
def post_fatura():
    return jsonify(satis_yonetimi.fatura_kes(db, request.json))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
