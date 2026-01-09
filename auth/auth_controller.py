from auth.auth_service import login_user


def login(email: str, password: str):
    return login_user(email, password)
