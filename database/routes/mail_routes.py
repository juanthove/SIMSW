from flask import Blueprint, jsonify, request
from auth.auth_middleware import jwt_required
from database.controllers.mail_controller import (
    obtener_mails,
    crear_mail,
    actualizar_mail,
    eliminar_mail,
    obtener_mails_por_sitio
)

mail_bp = Blueprint("mail", __name__, url_prefix="/api/mails")


@mail_bp.route("/", methods=["GET"])
@jwt_required()
def get_mails():
    return jsonify(obtener_mails()), 200


@mail_bp.route("/", methods=["POST"])
@jwt_required()
def post_mail():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    mail = crear_mail(data)
    if mail is None:
        return jsonify({"error": "Correo ya existente"}), 400

    return jsonify(mail), 201


@mail_bp.route("/<int:mail_id>", methods=["PUT"])
@jwt_required()
def put_mail(mail_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON requerido"}), 400

    mail = actualizar_mail(mail_id, data)
    if mail is None:
        return jsonify({"error": "Mail no encontrado"}), 404

    return jsonify(mail), 200


@mail_bp.route("/<int:mail_id>", methods=["DELETE"])
@jwt_required()
def delete_mail(mail_id):
    eliminado = eliminar_mail(mail_id)
    if not eliminado:
        return jsonify({"error": "Mail no encontrado"}), 404

    return jsonify({"mensaje": "Mail eliminado correctamente"}), 200



@mail_bp.route("/sitio/<int:sitio_id>", methods=["GET"])
@jwt_required()
def get_mails_por_sitio(sitio_id):
    try:
        mails = obtener_mails_por_sitio(sitio_id)

        if not mails:
            return jsonify({
                "error": "No hay correos asociados a este sitio"
            }), 404

        return jsonify(mails), 200

    except Exception as e:
        return jsonify({
            "error": "Error al obtener correos del sitio",
            "detalle": str(e)
        }), 500

