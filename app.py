import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import stok_yonetimi 
import satis_yonetimi

# Klasör yollarını kesinleştiriyoruz
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
CORS(app)

# MongoDB Bağlantısı
MONGO_URI = "mongodb+srv://erdembctk01_db_user:Dyta96252@cluster0.o27rfmv.mongodb.net/stok_veritabani?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.stok_veritabani

@app.route('/')
def index():
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

@app.route('/api/invoices', methods=['GET'])
def get_gecmis():
    return jsonify(satis_yonetimi.satis_gecmisi(db))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
