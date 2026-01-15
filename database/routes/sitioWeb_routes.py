from flask import Blueprint, jsonify, request

from database.controllers.sitioWeb_controller import (
    obtener_sitios,
    obtener_sitio_por_id,
    crear_sitio,
    actualizar_sitio,
    eliminar_sitio
)

sitioWeb_bp = Blueprint("sitioWeb", __name__, url_prefix="/api/sitios")


@sitioWeb_bp.route("/", methods=["GET"])
def get_sitios():
    sitios = obtener_sitios()
    return jsonify(sitios), 200


@sitioWeb_bp.route("/<int:sitio_id>", methods=["GET"])
def get_sitio(sitio_id):
    sitio = obtener_sitio_por_id(sitio_id)
    if sitio is None:
        return jsonify({"error": "Sitio no encontrado"}), 404

    return jsonify(sitio), 200


@sitioWeb_bp.route("/", methods=["POST"])
def post_sitio():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    try:
        sitio = crear_sitio(data)
        return jsonify(sitio), 201

    except ValueError:
        # URL duplicada
        return jsonify({"error": "La URL ya existe"}), 409

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500



@sitioWeb_bp.route("/<int:sitio_id>", methods=["PUT"])
def put_sitio(sitio_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    try:
        sitio = actualizar_sitio(sitio_id, data)

        if sitio is None:
            return jsonify({"error": "Sitio no encontrado"}), 404

        return jsonify(sitio), 200

    except ValueError:
        # URL duplicada
        return jsonify({"error": "La URL ya existe"}), 409

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500



@sitioWeb_bp.route("/<int:sitio_id>", methods=["DELETE"])
def delete_sitio(sitio_id):
    eliminado = eliminar_sitio(sitio_id)

    if not eliminado:
        return jsonify({"error": "Sitio no encontrado"}), 404

    return jsonify({"message": "Sitio eliminado correctamente"}), 200
