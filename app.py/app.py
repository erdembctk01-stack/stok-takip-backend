from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import stok_yonetimi  # Diğer dosyayı çağırır
import satis_yonetimi # Diğer dosyayı çağırır

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
