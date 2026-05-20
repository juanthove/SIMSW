from flask import Blueprint, request, jsonify
from auth.auth_middleware import jwt_required

from .ia_service import (
    obtener_configuracion_ia,
    actualizar_configuracion_ia
)

ia_bp = Blueprint("ia", __name__)


#Obtener configuración IA
@ia_bp.route("/config/ia", methods=["GET"])
@jwt_required()
def obtener_configuracion():

    try:
        data = obtener_configuracion_ia()

        return jsonify(data), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


#Actualizar configuración IA
@ia_bp.route("/config/ia", methods=["PUT"])
@jwt_required()
def actualizar_configuracion():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No se recibieron datos"
        }), 400

    try:
        actualizar_configuracion_ia(data)

        return jsonify({
            "mensaje": "Configuración actualizada correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500