import pymysql
import os
import sys


def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


def main(root_password, db_user, db_password):
    uso_root = False
    print("Conectando a MariaDB como root...")

    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password=root_password
        )
    except Exception as e:
        raise RuntimeError("No se pudo conectar como root. Verifique el password.") from e

    cursor = conn.cursor()

    print("Creando base de datos...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS simsw;")

    print("Creando usuario de aplicación...")

    try:
        cursor.execute(f"""
            CREATE USER IF NOT EXISTS '{db_user}'@'localhost'
            IDENTIFIED BY '{db_password}';
        """)

        print("Asignando permisos...")
        cursor.execute(f"""
            GRANT ALL PRIVILEGES ON simsw.* TO '{db_user}'@'localhost';
        """)

        cursor.execute("FLUSH PRIVILEGES;")

    except pymysql.err.OperationalError as e:
        if e.args[0] == 1227:
            print("⚠ Root no tiene permisos para crear usuarios.")
            print("⚠ Se usará root como conexión.")

            db_user = "root"
            db_password = root_password
            uso_root = True
        else:
            raise


    cursor.execute("USE simsw;")

    print("Ejecutando script SQL inicial...")
    sql_path = get_resource_path("dbSIMSW.sql")

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    for statement in sql_script.split(";"):
        if statement.strip():
            cursor.execute(statement)

    conn.commit()
    cursor.close()
    conn.close()

    print("✔ Base de datos y usuario creados correctamente")

    return uso_root