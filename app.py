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
    
    id = 1 #Se obitiene llendo a la base de datos y sumandole 1 al maximo
    nombre = " " #Se obtiene: Analizando el HTML <title> o el dominio
    propietario = " " #Se obtienen: Usando WHOIS, pero no siempre viene dueño real, a veces está privado
    archivos = None #Se obtienen: Haciendo un análisis del sitio (scraping o crawling)
    fechaRegistro = None #Se va a la base, y si eciste la url, se trae el dato, sino se obiene con la fecha actual
    fechaUltimoMonitoreo = None #Se obtiene llendo a la base de datos


    st = SitioWeb(id,nombre ,url , propietario, fechaRegistro, fechaUltimoMonitoreo, archivos)

    fechaAtual = None
    analisis = Analisis(1, fechaAtual, "No terminado", "estatico", st)

    resultado = analisis.ejectutarEstatico()

    return resultado




    return 0


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    