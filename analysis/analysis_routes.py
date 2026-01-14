#Endpoint de la api para realizar los analisis

from flask import Blueprint, request, jsonify
from .analysis_controller import analizar_estatico, analizar_dinamico,analizar_sonar_qube
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
    

@analysis_bp.route("/analizarDinamico", methods=["POST"])
@jwt_required()
def analizar_dinamico_endpoint():
    print("Entre en el de rutass")
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400

    try:
        print("A")
        resultado = analizar_dinamico(url)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@analysis_bp.route("/analizarSonarQube", methods=["POST"])
@jwt_required()
def analizar_sonar_endpoint():
    #Tendria que fijarme si existe la direccion de la carpeta que me llega
    #Si existe, voy directo a ella. 
    #Si no existe, debo descargarla y ponerla en documentos/SIMSW/Proyectos(?)
    #Una ves descargado, comienzo el analisis
    pass