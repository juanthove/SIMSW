import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import socket
import ctypes

load_dotenv()

if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
else:
    base_path = Path(__file__).parent
os.chdir(base_path)


def puerto_en_uso(puerto):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", puerto))
        s.close()
        return False
    except:
        return True

if puerto_en_uso(5000):
    ctypes.windll.user32.MessageBoxW(
        0,
        "SIMSW ya está en ejecución.",
        "Información",
        0x40
    )
    sys.exit()

from app import app

if __name__ == "__main__":
    from waitress import serve
    print("Iniciando SIMSW con Waitress...")
    serve(app, host="0.0.0.0", port=5000)