from flask import Blueprint, jsonify, request
from auth.auth_middleware import jwt_required
from database.controllers.analisis_controller import (
    obtener_analisis,
    obtener_analisis_por_id,
    obtener_analisis_por_sitio,
    crear_analisis,
    actualizar_analisis,
    eliminar_analisis
)

analisis_bp_db = Blueprint("analisis", __name__, url_prefix="/api/analisis")


#Obtener todos
@analisis_bp_db.route("/", methods=["GET"])
@jwt_required()
def get_analisis():
    return jsonify(obtener_analisis()), 200


#Obtener por id
@analisis_bp_db.route("/<int:analisis_id>", methods=["GET"])
@jwt_required()
def get_analisis_id(analisis_id):
    analisis = obtener_analisis_por_id(analisis_id)
    if not analisis:
        return jsonify({"error": "Análisis no encontrado"}), 404
    return jsonify(analisis), 200


#Obtener analisis por sitio
@analisis_bp_db.route("/sitio/<int:sitio_web_id>", methods=["GET"])
@jwt_required()
def get_analisis_por_sitio(sitio_web_id):
    analisis = obtener_analisis_por_sitio(sitio_web_id)
    return jsonify(analisis), 200


#Crear
@analisis_bp_db.route("/", methods=["POST"])
@jwt_required()
def post_analisis():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    try:
        analisis = crear_analisis(data)
        return jsonify(analisis), 201

    except ValueError:
        return jsonify({"error": "Error al crear análisis"}), 400

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


#Editar
@analisis_bp_db.route("/<int:analisis_id>", methods=["PUT"])
@jwt_required()
def put_analisis(analisis_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    analisis = actualizar_analisis(analisis_id, data)
    if not analisis:
        return jsonify({"error": "Análisis no encontrado"}), 404

    return jsonify(analisis), 200


#Eliminar
@analisis_bp_db.route("/<int:analisis_id>", methods=["DELETE"])
@jwt_required()
def delete_analisis(analisis_id):
    eliminado = eliminar_analisis(analisis_id)
    if not eliminado:
        return jsonify({"error": "Análisis no encontrado"}), 404

    return jsonify({"mensaje": "Análisis eliminado correctamente"}), 200
