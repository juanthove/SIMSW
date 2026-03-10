import os
from dotenv import load_dotenv

load_dotenv()

from app import app

if __name__ == "__main__":
    try:
        from waitress import serve
        print("Iniciando SIMSW con Waitress...")
        serve(app, host="0.0.0.0", port=5000)
    except ImportError:
        print("Waitress no instalado, usando Flask dev server...")
        app.run(host="0.0.0.0", port=5000)