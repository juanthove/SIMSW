from functools import wraps
from flask import request, jsonify
from auth.auth_utils import verify_token


def jwt_required():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({
                    "success": False,
                    "message": "Acceso denegado. Token requerido."
                }), 401

            token = auth_header.split(" ")[1]

            try:
                user = verify_token(token)
                request.user = user
            except Exception:
                return jsonify({
                    "success": False,
                    "message": "Token inválido o expirado"
                }), 403

            return f(*args, **kwargs)

        return wrapper
    return decorator
