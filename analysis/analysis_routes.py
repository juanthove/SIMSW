#Endpoint de la api para realizar los analisis

from flask import Blueprint, request, jsonify
from .analysis_controller import analizar_estatico, analizar_dinamico,analizar_sonar_qube
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

    
    print(f"La ruta base es: {sitio_web_id}")
    try:
        print("Entrando análisis estático...")
        resultado = analizar_estatico(url, sitio_web_id)
        return jsonify(resultado), 200

    except Exception as e:
        # HTTP error, pero el estado ya quedó guardado
        print("Saliendo análisis estático con error...")
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

    

    
@analysis_bp.route("/analizarSonarQube", methods=["POST"])
@jwt_required()
def analizar_sonar_endpoint():
    #Tendria que fijarme si existe la direccion de la carpeta que me llega
    #Si existe, voy directo a ella. 
    #Si no existe, debo descargarla y ponerla en documentos/SIMSW/Proyectos(?)
    #Una ves descargado, comienzo el analisis
    pass