from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scripts.vulberta_api import analizar_url

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html') 


@app.route("/analizarEstatico", methods=["POST"])
def analizarVulBERTa():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    resultado = analizar_url(url)
    return resultado


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    