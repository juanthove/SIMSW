#Endpoint de la api para realizar los analisis

from flask import Blueprint, request, jsonify
from .analysis_controller import analizar_estatico, analizar_dinamico, analizar_alteraciones
from auth.auth_middleware import jwt_required

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analizarEstatico", methods=["POST"])
@jwt_required()
def analizar_estatico_endpoint():
    data = request.get_json()

    url = data.get("url")
    sitio_web_id = data.get("sitio_web_id")

    if not url or sitio_web_id is None:
        return jsonify({"error": "Faltan datos"}), 400

    sitio_web_id = int(sitio_web_id)

    try:
        resultado = analizar_estatico(url, sitio_web_id)
        return jsonify(resultado), 200

    except Exception as e:
        # HTTP error, pero el estado ya quedó guardado
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Falló el análisis estático",
            "detalle": str(e)
        }), 500


    

@analysis_bp.route("/analizarDinamico", methods=["POST"])
@jwt_required()
def analizar_dinamico_endpoint():
    data = request.get_json()

    url = data.get("url")
    sitio_web_id = data.get("sitio_web_id")

    if not url or sitio_web_id is None:
        return jsonify({"error": "Faltan datos"}), 400

    sitio_web_id = int(sitio_web_id)

    try:
        resultado = analizar_dinamico(url, sitio_web_id)
        return jsonify(resultado), 200

    except Exception as e:
        # HTTP error, pero el estado ya quedó guardado
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Falló el análisis dinámico",
            "detalle": str(e)
        }), 500

    
#Analizar cambios entre los archivos base y la url
@analysis_bp.route("/analizarAlteraciones", methods=["POST"])
@jwt_required()
def analizar_alteraciones_endpoint():
    data = request.get_json()

    url = data.get("url")
    sitio_web_id = data.get("sitio_web_id")

    if not url or sitio_web_id is None:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        sitio_web_id = int(sitio_web_id)
    except ValueError:
        return jsonify({"error": "sitio_web_id inválido"}), 400

    try:
        resultado = analizar_alteraciones(url, sitio_web_id)
        return jsonify(resultado), 200

    except Exception as e:
        # El estado interno ya debería quedar persistido
        return jsonify({
            "estado": "ERROR",
            "mensaje": "Falló el análisis de alteraciones",
            "detalle": str(e)
        }), 500
