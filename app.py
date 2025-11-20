from flask import Flask, request, jsonify, render_template
from flask_cors import CORS


from datetime import datetime

from scripts.SitioWeb import SitioWeb
from scripts.Analisis import Analisis
from scripts.Archivo import Archivo
from scripts.tools import extraer_scripts_con_playwright

app = Flask(__name__)
CORS(app)



@app.route('/')
def index():
    return render_template('index.html') 


@app.route("/analizarEstatico", methods=["POST"])
def ejecutar_estatico():

    """Analiza el sitio de forma estatica"""

    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    #Tendria que checkear que la url no existe
    #En caso de que no exista, hago lo siguiente, en caso de que si, voy a buscar los datos a la base. 
    
    id = 0
    archivos = []
    scripts = extraer_scripts_con_playwright(url)
    

    # === EXTERNOS ===
    if "externos" in scripts and scripts["externos"]:
        for name, codigo in scripts["externos"].items():
            archivos.append(Archivo(id, name, url, None, "externo", len(codigo or ""), codigo))
            id += 1

    # === INTERNOS ===
    if "internos" in scripts and scripts["internos"]:
        for name, codigo in scripts["internos"].items():
            archivos.append(Archivo(id, name, url, None, "interno", len(codigo or ""), codigo))
            id += 1

    # === NETWORK ===
    if "network" in scripts and scripts["network"]:
        for name, codigo in scripts["network"].items():
            archivos.append(Archivo(id, name, url, None, "network", len(codigo or ""), codigo))
            id += 1

    # === WORKERS ===
    if "workers" in scripts and scripts["workers"]:
        for name, codigo in scripts["workers"].items():
            archivos.append(Archivo(id, name, url, None, "worker", len(codigo or ""), codigo))
            id += 1

    # === BLOBS ===
    if "blobs" in scripts and scripts["blobs"]:
        for name, codigo in scripts["blobs"].items():
            archivos.append(Archivo(id, name, url, None, "blob", len(codigo or ""), codigo))
            id += 1  

    # === EVENTOS INLINE ===
    if "eventos_inline" in scripts and scripts["eventos_inline"]:
        for name, info in scripts["eventos_inline"].items():
            codigo = info.get("codigo", "")
            archivos.append(Archivo(id, name, url, None, "evento_inline", len(codigo), codigo))
            id += 1
        
    

    st = SitioWeb(1, "No se", url, "propietario", None, None, archivos)


    fecha_actual = datetime.now()


    analisis = Analisis(1, fecha_actual, "No terminado", "estatico", st)

    resultado = analisis.ejectutar_estatico()

    return jsonify({
        "url": url,
        "resultado": [f.to_dict() for f in resultado]
    })
    


@app.route("/analizarDinamico", methods=["POST"])
def analizar_dinamico():
    
    """Analiza el sitio de forma dinamica"""
    
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    id = 0
    archivos = []
    scripts = extraer_scripts_con_playwright(url)
    

    # === EXTERNOS ===
    if "externos" in scripts and scripts["externos"]:
        for name, codigo in scripts["externos"].items():
            archivos.append(Archivo(id, name, url, None, "externo", len(codigo or ""), codigo))
            id += 1

    # === INTERNOS ===
    if "internos" in scripts and scripts["internos"]:
        for name, codigo in scripts["internos"].items():
            archivos.append(Archivo(id, name, url, None, "interno", len(codigo or ""), codigo))
            id += 1

    # === NETWORK ===
    if "network" in scripts and scripts["network"]:
        for name, codigo in scripts["network"].items():
            archivos.append(Archivo(id, name, url, None, "network", len(codigo or ""), codigo))
            id += 1

    # === WORKERS ===
    if "workers" in scripts and scripts["workers"]:
        for name, codigo in scripts["workers"].items():
            archivos.append(Archivo(id, name, url, None, "worker", len(codigo or ""), codigo))
            id += 1

    # === BLOBS ===
    if "blobs" in scripts and scripts["blobs"]:
        for name, codigo in scripts["blobs"].items():
            archivos.append(Archivo(id, name, url, None, "blob", len(codigo or ""), codigo))
            id += 1  

    # === EVENTOS INLINE ===
    if "eventos_inline" in scripts and scripts["eventos_inline"]:
        for name, info in scripts["eventos_inline"].items():
            codigo = info.get("codigo", "")
            archivos.append(Archivo(id, name, url, None, "evento_inline", len(codigo), codigo))
            id += 1
        
    
    st = SitioWeb(1, "No se", url, "propietario", None, None, archivos)


    fecha_actual = datetime.now()


    analisis = Analisis(1, fecha_actual, "No terminado", "Dinamico", st)

    resultado = analisis.ejectutar_dinamico()

    return jsonify({"url": url, "resultado": resultado})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    