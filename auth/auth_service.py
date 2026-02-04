from auth.auth_utils import verify_password, generate_token
from database.connection import SessionLocal
from database.models.usuario_model import Usuario


def login_user(email: str, password: str):
    db = SessionLocal()

    try:
        user = (
            db.query(Usuario)
            .filter(Usuario.email == email)
            .first()
        )

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        token = generate_token(user)

        return {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email
            }
        }

    finally:
        db.close()
