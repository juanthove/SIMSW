import subprocess
import secrets
import getpass
import traceback
import os
import shutil
import sys
from pathlib import Path
import subprocess
import socket
import pymysql

# =========================
# Verificar MySQL
# =========================

def verificar_mysql():
    try:
        s = socket.create_connection(("127.0.0.1", 3306), timeout=2)
        s.close()
        return True
    except:
        return False


def mariadb_corriendo(root_password):
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password=root_password,
            port=3306,
            connect_timeout=5
        )
        conn.close()
        return True
    except:
        return False
    

def base_datos_existe(root_password, db_name="simsw"):

    try:
        result = subprocess.run(
            [
                "mysql",
                "-u", "root",
                f"-p{root_password}",
                "-e",
                f"SHOW DATABASES LIKE '{db_name}';"
            ],
            capture_output=True,
            text=True
        )

        return db_name in result.stdout

    except Exception:
        return False
    

def usuario_mysql_existe(root_password, db_user):

    try:
        result = subprocess.run(
            [
                "mysql",
                "-u", "root",
                f"-p{root_password}",
                "-e",
                f"SELECT User FROM mysql.user WHERE User='{db_user}';"
            ],
            capture_output=True,
            text=True
        )

        return db_user in result.stdout

    except Exception:
        return False



# =========================
# Rollback
# =========================

def rollback(instalacion, db_root_password, db_user):

    print("\n⚠ Revirtiendo instalación...")

    # eliminar base de datos
    if instalacion["db"]:
        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password=db_root_password
            )

            cursor = conn.cursor()
            cursor.execute("DROP DATABASE IF EXISTS simsw")
            cursor.execute(f"DROP USER IF EXISTS '{db_user}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")

            conn.commit()
            cursor.close()
            conn.close()

            print("✔ Base de datos eliminada")

        except Exception as e:
            print("⚠ No se pudo eliminar la base de datos")
            print(e)

    # eliminar .env
    if instalacion["env"] and os.path.exists(".env"):
        os.remove(".env")
        print("✔ Archivo .env eliminado")

    print("✔ Rollback completado")


# =========================
# Función principal
# =========================

def main():

    print("===== Instalador SIMSW =====\n")

    instalacion = {
        "env": False,
        "db": False,
        "admin": False
    }

    db_root_password = None
    db_user = None

    try:

        if os.path.exists(".env"):
            print("⚠ El programa ya parece estar instalado.")
            print("Instalación cancelada.")
            input("\nPresione Enter para salir...")
            return

        # =========================
        # Verificar MariaDB
        # =========================

        if not verificar_mysql():
            print("❌ MariaDB/MySQL no está instalado o no está en PATH.")
            print("Instale MariaDB antes de ejecutar el instalador.")
            input("\nPresione Enter para salir...")
            return


        # =========================
        # Pedir datos de base de datos y verificar mariaDB
        # =========================

        db_user = input("Usuario de la base de datos (DB_USER): ")
        db_password = getpass.getpass("Password del usuario DB: ")
        db_root_password = getpass.getpass("Password ROOT de MySQL: ")


        if not mariadb_corriendo(db_root_password):
            print("❌ No se pudo conectar a MariaDB con el password proporcionado.")
            print("Asegúrese de que MariaDB esté corriendo y el password sea correcto.")
            input("\nPresione Enter para salir...")
            return

        if base_datos_existe(db_root_password):
            print("❌ La base de datos 'simsw' ya existe.")
            input("\nPresione Enter para salir...")
            return 
        
        if usuario_mysql_existe(db_root_password, db_user):
            print(f"❌ El usuario '{db_user}' ya existe.")
            input("\nPresione Enter para salir...")
            return 


        print("\n===== Usuario Administrador =====")

        nombre_admin = input("Nombre del usuario: ")
        email_admin = input("Email (Gmail): ")
        password_admin = getpass.getpass("Password del usuario: ")

        google_api_key = input("Google API Key: ")

        jwt_secret = secrets.token_hex(32)


        # =========================
        # Crear .env
        # =========================

        env_content = f"""# =========================
# API LLM
# =========================
GOOGLE_API_KEY={google_api_key}

# =========================
# Base de Datos
# =========================
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_NAME=simsw

# =========================
# Seguridad
# =========================
JWT_SECRET={jwt_secret}

# =========================
# Gmail
# =========================
GMAIL_REMITENTE=simsw.meerkatsys@gmail.com
PASS_APLICACION=bwpmkgwtplilpnts
"""

        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        instalacion["env"] = True

        print("\n✔ Archivo .env creado")

        # =========================
        # Inicializar DB
        # =========================

        print("\nInicializando base de datos...")

        from init_db import main as init_db_main

        init_db_main(db_root_password, db_user, db_password)

        instalacion["db"] = True

        print("✔ Base de datos inicializada")

        # =========================
        # Crear usuario admin
        # =========================

        print("\nCreando usuario administrador...")

        from database.connection import SessionLocal
        from database.models.usuario_model import Usuario
        from auth.auth_utils import hash_password

        db = SessionLocal()

        nuevo_usuario = Usuario(
            nombre=nombre_admin,
            email=email_admin,
            password=hash_password(password_admin)
        )

        db.add(nuevo_usuario)
        db.commit()
        db.close()

        instalacion["admin"] = True

        print("✔ Usuario administrador creado correctamente")

        # =========================
        # Crear desinstalador
        # =========================
        
        print("\nCreando desinstalador...")

        uninstall_src = Path(sys.executable).parent / "_internal" / "uninstall.exe"
        uninstall_dst = Path(sys.executable).parent / "uninstall.exe"

        if uninstall_src.exists():
            shutil.copy(uninstall_src, uninstall_dst)
            print("✔ Desinstalador creado")
        else:
            print("⚠ No se encontró uninstall.exe")


        print("\nCreando SIMSW...")

        simsw_src = Path(sys.executable).parent / "_internal" / "SIMSW.exe"
        simsw_dst = Path(sys.executable).parent / "SIMSW.exe"

        if simsw_src.exists():
            shutil.copy(simsw_src, simsw_dst)
            print("✔ SIMSW creado")
        else:
            print("⚠ No se encontró SIMSW.exe")

        print("\n✔ Instalación completada correctamente")

    except Exception:

        print("\n❌ ERROR DURANTE LA INSTALACIÓN\n")
        print(traceback.format_exc())

        rollback(instalacion, db_root_password, db_user)

        input("\nPresione Enter para salir...")


# =========================
# Ejecutar instalador
# =========================

if __name__ == "__main__":
    main()