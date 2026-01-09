from flask import Blueprint, request, jsonify
from auth.auth_controller import login

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email y contraseña requeridos"
        }), 400

    result = login(email, password)

    if not result:
        return jsonify({
            "success": False,
            "message": "Credenciales inválidas"
        }), 401

    return jsonify({
        "success": True,
        "message": "Login exitoso",
        **result
    }), 200
