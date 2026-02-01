from flask import Blueprint, jsonify, request
from auth.auth_middleware import jwt_required

from database.controllers.sitioWeb_controller import (
    obtener_sitios,
    obtener_sitio_por_id,
    crear_sitio,
    actualizar_sitio,
    eliminar_sitio,
    obtener_sitios_con_resumen,
    obtener_detalle_sitio,
    obtener_informes_por_sitio,
    subir_un_archivo_base_sitio
)

sitioWeb_bp = Blueprint("sitioWeb", __name__, url_prefix="/api/sitios")


@sitioWeb_bp.route("/", methods=["GET"])
@jwt_required()
def get_sitios():
    sitios = obtener_sitios()
    return jsonify(sitios), 200


@sitioWeb_bp.route("/<int:sitio_id>", methods=["GET"])
@jwt_required()
def get_sitio(sitio_id):
    sitio = obtener_sitio_por_id(sitio_id)
    if sitio is None:
        return jsonify({"error": "Sitio no encontrado"}), 404

    return jsonify(sitio), 200


@sitioWeb_bp.route("/", methods=["POST"])
@jwt_required()
def post_sitio():
    data = request.form

    try:
        sitio = crear_sitio(data)
        return jsonify(sitio), 201

    except ValueError as e:
        if str(e) == "URL_DUPLICADA":
            return jsonify({"error": "La URL ya existe"}), 409
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500




@sitioWeb_bp.route("/<int:sitio_id>", methods=["PUT"])
@jwt_required()
def put_sitio(sitio_id):
    data = request.form

    try:
        sitio = actualizar_sitio(sitio_id, data)

        if sitio is None:
            return jsonify({"error": "Sitio no encontrado"}), 404

        return jsonify(sitio), 200

    except ValueError as e:
        if str(e) == "URL_DUPLICADA":
            return jsonify({"error": "La URL ya existe"}), 409
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500
    

#Subir archivos base
@sitioWeb_bp.route("/<int:sitio_id>/archivos", methods=["POST"])
@jwt_required()
def subir_archivo_base(sitio_id):
    archivo = request.files.get("archivo")
    ruta_relativa = request.form.get("ruta_relativa")

    if not archivo or not ruta_relativa:
        return jsonify({"error": "Faltan datos del archivo"}), 400

    try:
        resultado = subir_un_archivo_base_sitio(sitio_id, archivo, ruta_relativa)
        return jsonify(resultado), 200

    except ValueError as e:
        msg = str(e)

        if "demasiado grande" in msg:
            return jsonify({"error": msg}), 413  # 👈 clave
        
        return jsonify({"error": msg}), 400

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500





@sitioWeb_bp.route("/<int:sitio_id>", methods=["DELETE"])
@jwt_required()
def delete_sitio(sitio_id):
    try:
        eliminado = eliminar_sitio(sitio_id)

        if not eliminado:
            return jsonify({"error": "Sitio no encontrado"}), 404

        return jsonify({"message": "Sitio eliminado correctamente"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500


#Obtener el resumen con cantidad de analisis y fecha del ultimo
@sitioWeb_bp.route("/resumen", methods=["GET"])
@jwt_required()
def obtener_sitios_resumen():
    sitios = obtener_sitios_con_resumen()
    return jsonify(sitios), 200


#Obtener informacion del sitio y de sus analisis
@sitioWeb_bp.route("/<int:sitio_id>/detalle", methods=["GET"])
@jwt_required()
def get_detalle_sitio(sitio_id):
    detalle = obtener_detalle_sitio(sitio_id)

    if not detalle:
        return jsonify({"error": "Sitio no encontrado"}), 404

    return jsonify(detalle), 200


#Obtener todos los informes del sitio
@sitioWeb_bp.route("/<int:site_id>/informes", methods=["GET"])
def listar_informes_por_sitio(site_id):
    informes = obtener_informes_por_sitio(site_id)

    if informes is None:
        return jsonify({"error": "Sitio no encontrado"}), 404

    return jsonify(informes), 200