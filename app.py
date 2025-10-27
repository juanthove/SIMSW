from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.vulberta_api import analizar_url, extraer_codigo
from scripts.owaspZap_api import owaspzap_scanner
from scripts.gemini import armarInforme

app = Flask(__name__)
CORS(app)

@app.route("/analizarAI", methods=["POST"])
def analizarVulBERTa():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    resultado = analizar_url(url)
    return resultado

@app.route("/analizarOW", methods=["POST"])
def analizarOWASPZAP():
    data = request.get_json()
    url = data.get("url")
    resultado = owaspzap_scanner(url)

    return jsonify({"url": url, "resultado": resultado})


@app.route("/informe", methods=["POST"])
def informe():
    data = request.get_json()
    lista_peticiones = data.get("listaPeticiones", [])
    informes = {}

    for peticion in lista_peticiones:
        fragmento = peticion.get("numeroDeFragmento")
        codigo = peticion.get("codigoVulnerable")

        resultado = armarInforme(fragmento, codigo)
        informes[fragmento] = resultado  # ya es dict

    return jsonify(informes)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)