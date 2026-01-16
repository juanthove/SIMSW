from flask import Blueprint, jsonify, request
from auth.auth_middleware import jwt_required

from database.controllers.informe_controller import (
    obtener_informes,
    obtener_informe_por_id,
    obtener_informes_por_analisis,
    crear_informe,
    actualizar_informe,
    eliminar_informe
)

informe_bp = Blueprint("informe", __name__, url_prefix="/api/informes")


#Obtener todos
@informe_bp.route("/", methods=["GET"])
@jwt_required()
def get_informes():
    informes = obtener_informes()
    return jsonify(informes), 200


#Obtener informe por id
@informe_bp.route("/<int:informe_id>", methods=["GET"])
@jwt_required()
def get_informe(informe_id):
    informe = obtener_informe_por_id(informe_id)
    if informe is None:
        return jsonify({"error": "Informe no encontrado"}), 404

    return jsonify(informe), 200


#Obtener todos los informes de un analisis con id
@informe_bp.route("/analisis/<int:analisis_id>", methods=["GET"])
@jwt_required()
def get_informes_por_analisis_route(analisis_id):
    informes = obtener_informes_por_analisis(analisis_id)
    return jsonify(informes), 200


#Crear
@informe_bp.route("/", methods=["POST"])
@jwt_required()
def post_informe():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    informe = crear_informe(data)

    if informe is None:
        return jsonify({"error": "Error al crear el informe"}), 400

    return jsonify(informe), 201


#Editar
@informe_bp.route("/<int:informe_id>", methods=["PUT"])
@jwt_required()
def put_informe(informe_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    informe = actualizar_informe(informe_id, data)

    if informe is None:
        return jsonify({"error": "Informe no encontrado"}), 404

    return jsonify(informe), 200


#Eliminar
@informe_bp.route("/<int:informe_id>", methods=["DELETE"])
@jwt_required()
def delete_informe(informe_id):
    eliminado = eliminar_informe(informe_id)

    if not eliminado:
        return jsonify({"error": "Informe no encontrado"}), 404

    return jsonify({"mensaje": "Informe eliminado correctamente"}), 200
