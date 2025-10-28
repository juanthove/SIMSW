import os
import sys
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
#from scripts.vulberta_api import analizar_url

from scripts.SitioWeb import SitioWeb
from scripts.Analisis import Analisis
from scripts.vulberta_api import Vulberta



app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html') 


@app.route("/analizarEstatico", methods=["POST"])
def ejecutarEstatico():
    # data = request.get_json()
    # url = data.get("url")
    # if not url:
    #     return jsonify({"error": "No se proporcionó URL"}), 400
    
    # resultado = analizar_url(url)
    # return resultado
    
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    st = SitioWeb(1, "google.com",url , "google", None, None, None)
    analisis = Analisis(1, None, "No terminado", "estatico", st)

    resultado = analisis.ejectutarEstatico()

    return resultado




    return 0


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    