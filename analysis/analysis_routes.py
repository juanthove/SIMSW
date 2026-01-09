#Endpoint de la api para realizar los analisis

from flask import Blueprint, request, jsonify
from .analysis_controller import analizar_estatico
from auth.auth_middleware import jwt_required

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analizarEstatico", methods=["POST"])
@jwt_required()
def analizar():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400

    try:
        resultado = analizar_estatico(url)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
