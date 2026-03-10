import pymysql
import os
import sys
import shutil
import psutil
import getpass
from dotenv import load_dotenv
import subprocess

print("===== Desinstalador SIMSW =====\n")

# =========================
# Cerrar SIMSW si está abierto
# =========================

print("Verificando si SIMSW está en ejecución...")

for proc in psutil.process_iter(["name"]):
    try:
        if proc.info["name"] == "SIMSW.exe":
            print("SIMSW.exe está corriendo. Cerrando...")
            proc.terminate()
            proc.wait(timeout=5)
            print("✔ SIMSW cerrado")
    except Exception:
        pass


# =========================
# Leer .env
# =========================

if not os.path.exists(".env"):
    print("No se encontró .env. No hay instalación activa.")
    input("\nPresione Enter para salir...")
    sys.exit()

load_dotenv()

db_user = os.getenv("DB_USER")
db_name = os.getenv("DB_NAME")


# =========================
# Pedir password ROOT
# =========================

print("\nSe requiere acceso ROOT a MariaDB para eliminar la base de datos.")
root_password = getpass.getpass("Password ROOT de MySQL: ")


# =========================
# Confirmación
# =========================

confirm = input(
    "\nEsto eliminará completamente SIMSW:\n"
    "- Base de datos\n"
    "- Usuario MySQL\n"
    "- Configuración\n"
    "- Archivos subidos\n\n"
    "¿Continuar? (s/n): "
)

if confirm.lower() != "s":
    print("Cancelado.")
    input("\nPresione Enter para salir...")
    sys.exit()


# =========================
# Conectar a MariaDB
# =========================

print("\nConectando a MariaDB...")

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password=root_password
    )

except pymysql.err.OperationalError:
    print("\n❌ Contraseña ROOT incorrecta o MariaDB no permite la conexión.")
    input("\nPresione Enter para salir...")
    sys.exit()

except Exception:
    print("\n❌ Error al conectar con MariaDB.")
    input("\nPresione Enter para salir...")
    sys.exit()

cursor = conn.cursor()


# =========================
# Eliminar DB y usuario
# =========================

print("Eliminando base de datos...")
cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")

print("Eliminando usuario...")
cursor.execute(f"DROP USER IF EXISTS '{db_user}'@'localhost'")

cursor.execute("FLUSH PRIVILEGES")

conn.commit()
cursor.close()
conn.close()


# =========================
# Borrar archivos locales
# =========================

print("Eliminando archivos locales...")

if os.path.exists(".env"):
    os.remove(".env")

if os.path.exists("uploads"):
    shutil.rmtree("uploads")

if os.path.exists("SIMSW.exe"):
    os.remove("SIMSW.exe")


print("\n✔ Desinstalación completada correctamente")


print("Eliminando ejecutables...")

# ruta actual
current_dir = os.getcwd()

# script temporal
bat_path = os.path.join(current_dir, "cleanup.bat")

with open(bat_path, "w") as f:
    f.write(f"""
@echo off
timeout /t 2 >nul
del "{current_dir}\\uninstall.exe"
del "%~f0"
""")

# ejecutar el bat
subprocess.Popen(bat_path, shell=True)

print("\nSIMSW fue eliminado completamente.")

sys.exit()

input("\nPresione Enter para cerrar...")