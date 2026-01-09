from auth.auth_utils import verify_password, generate_token

# Más adelante esto va a la BD
USERS = [
    {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "password": "$2b$12$LNbL9qxsAyP5KACHsWveaOaI8qLG41sVXKixjAlStRSQdgTDSlNRi"  # bcrypt
    }
]


def login_user(email: str, password: str):
    user = next((u for u in USERS if u["email"] == email), None)

    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None

    token = generate_token(user)

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"]
        }
    }
