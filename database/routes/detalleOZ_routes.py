from flask import Blueprint, jsonify, request
from auth.auth_middleware import jwt_required

from database.controllers.detalleOZ_controller import (
    obtener_detalles_oz,
    obtener_detalle_oz_por_id,
    obtener_detalle_oz_por_informe,
    crear_detalle_oz,
    actualizar_detalle_oz,
    eliminar_detalle_oz
)

detalleOZ_bp = Blueprint("detalle_oz", __name__, url_prefix="/api/detalle-oz")


@detalleOZ_bp.route("/", methods=["GET"])
@jwt_required()
def get_detalles_oz():
    detalles = obtener_detalles_oz()
    return jsonify(detalles), 200


@detalleOZ_bp.route("/<int:detalle_id>", methods=["GET"])
@jwt_required()
def get_detalle_oz(detalle_id):
    detalle = obtener_detalle_oz_por_id(detalle_id)

    if detalle is None:
        return jsonify({"error": "Detalle OZ no encontrado"}), 404

    return jsonify(detalle), 200


@detalleOZ_bp.route("/informe/<int:informe_id>", methods=["GET"])
@jwt_required()
def get_detalle_oz_por_informe(informe_id):
    detalle = obtener_detalle_oz_por_informe(informe_id)

    if detalle is None:
        return jsonify({"error": "Detalle OZ no encontrado para este informe"}), 404

    return jsonify(detalle), 200


@detalleOZ_bp.route("/", methods=["POST"])
@jwt_required()
def post_detalle_oz():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    detalle = crear_detalle_oz(data)

    if detalle is None:
        return jsonify({
            "error": "Error al crear el detalle OZ (puede que ya exista para este informe)"
        }), 400

    return jsonify(detalle), 201


@detalleOZ_bp.route("/<int:detalle_id>", methods=["PUT"])
@jwt_required()
def put_detalle_oz(detalle_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    detalle = actualizar_detalle_oz(detalle_id, data)

    if detalle is None:
        return jsonify({"error": "Detalle OZ no encontrado"}), 404

    return jsonify(detalle), 200


@detalleOZ_bp.route("/<int:detalle_id>", methods=["DELETE"])
@jwt_required()
def delete_detalle_oz(detalle_id):
    eliminado = eliminar_detalle_oz(detalle_id)

    if not eliminado:
        return jsonify({"error": "Detalle OZ no encontrado"}), 404

    return jsonify({
        "mensaje": "Detalle OZ eliminado correctamente"
    }), 200

