from database.connection import SessionLocal
from database.models.sitioWeb_model import SitioWeb
from database.models.analisis_model import Analisis
from database.models.informe_model import Informe
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import timezone
from pathlib import Path
import os
import shutil
from werkzeug.utils import secure_filename
from flask import current_app

EXTENSIONES_PERMITIDAS = {"py", "js", "ts", "java", "php", "json", "yml", "yaml", "xml", "html", "css", "sh", "env", "md"}


#Saber si un archivo tiene una extension permitida
def archivo_permitido(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS
    )

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Obtener todos los sitios
def obtener_sitios():
    db = SessionLocal()
    try:
        sitios = db.query(SitioWeb).all()
        return [s.to_dict() for s in sitios]
    finally:
        db.close()


# Obtener un sitio por ID
def obtener_sitio_por_id(sitio_id):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()
        return sitio.to_dict() if sitio else None
    finally:
        db.close()


# Crear sitio web
def crear_sitio(data):
    db = SessionLocal()
    try:
        sitio = SitioWeb(
            nombre=data.get("nombre"),
            url=data.get("url"),
            propietario=data.get("propietario"),
            frecuencia_monitoreo_minutos=int(data.get("frecuenciaAnalisis")),
            archivos_base=False
        )

        db.add(sitio)
        db.commit()
        db.refresh(sitio)

        return sitio.to_dict()

    except IntegrityError:
        db.rollback()
        raise ValueError("URL_DUPLICADA")

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()




#Actualizar sitio web
def actualizar_sitio(sitio_id, data):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()

        if sitio is None:
            return None

        if "nombre" in data:
            sitio.nombre = data.get("nombre")

        if "url" in data:
            sitio.url = data.get("url")

        if "propietario" in data:
            sitio.propietario = data.get("propietario")

        if "frecuenciaAnalisis" in data:
            sitio.frecuencia_monitoreo_minutos = int(data.get("frecuenciaAnalisis"))

        # Eliminar archivos base si viene el flag
        eliminar_archivos = data.get("eliminarArchivos") == "true"

        if eliminar_archivos:
            ruta_sitio = os.path.join(
                current_app.config["UPLOADS_DIR"],
                "sitios",
                str(sitio.id)
            )

            if os.path.exists(ruta_sitio):
                shutil.rmtree(ruta_sitio)

            sitio.archivos_base = False

        db.commit()
        db.refresh(sitio)

        return sitio.to_dict()

    except IntegrityError:
        db.rollback()
        raise ValueError("URL_DUPLICADA")

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()



#Eliminar un sitio web
def eliminar_sitio(sitio_id):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()

        if sitio is None:
            return False

        #Ruta de archivos del sitio
        ruta_sitio = os.path.join(current_app.config["UPLOADS_DIR"], "sitios", str(sitio.id))

        #Eliminar carpeta de archivos (si existe)
        if os.path.exists(ruta_sitio):
            shutil.rmtree(ruta_sitio)

        #Eliminar registro DB
        db.delete(sitio)
        db.commit()

        return True

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


#Obtener sitios con cantidad de analisis y fecha del ultimo
def obtener_sitios_con_resumen():
    db = SessionLocal()
    try:
        resultados = (
            db.query(
                SitioWeb.id,
                SitioWeb.nombre,
                SitioWeb.url,
                SitioWeb.fecha_ultimo_monitoreo,
                func.count(Analisis.id).label("cantAnalisis"),
            )
            .outerjoin(
                Analisis, Analisis.sitio_web_id == SitioWeb.id
            )
            .group_by(
                SitioWeb.id,
                SitioWeb.nombre,
                SitioWeb.url,
                SitioWeb.fecha_ultimo_monitoreo
            )
            .all()
        )
        

        return [
            {
                "id": r.id,
                "nombre": r.nombre,
                "url": r.url,
                "cantAnalisis": r.cantAnalisis,
                "ultimoAnalisis": (
                    r.fecha_ultimo_monitoreo.replace(tzinfo=timezone.utc).isoformat()
                    if r.fecha_ultimo_monitoreo else None
                )
            }
            for r in resultados
        ]
    finally:
        db.close()



#Obtener informacion del sitio y de sus analisis
def obtener_detalle_sitio(sitio_id):
    db = SessionLocal()
    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()

        if not sitio:
            return None

        analisis = (
            db.query(Analisis)
            .filter(Analisis.sitio_web_id == sitio_id)
            .order_by(Analisis.fecha.desc())
            .all()
        )

        resultado = []

        for a in analisis:
            cantidad_informes = (
                db.query(func.count(Informe.id))
                .filter(Informe.analisis_id == a.id)
                .scalar()
            )

            resultado.append({
                "id": a.id,
                "nombre": a.nombre,
                "estado": a.estado,
                "tipo": a.tipo,
                "resultado_global": a.resultado_global,
                "fecha": a.fecha.replace(tzinfo=timezone.utc).isoformat(),
                "cantidad_informes": cantidad_informes
            })

        return {
            "siteId": sitio.id,
            "nombre": sitio.nombre,
            "url": sitio.url,
            "propietario": sitio.propietario,
            "analisis": resultado
        }

    finally:
        db.close()



#Obtener todos los informes de un sitio
def obtener_informes_por_sitio(site_id):
    db = SessionLocal()
    try:
        resultados = (
            db.query(
                Informe.id,
                Informe.titulo,
                Informe.severidad,
                Analisis.fecha.label("fecha_analisis")
            )
            .join(Analisis, Informe.analisis_id == Analisis.id)
            .filter(Analisis.sitio_web_id == site_id)
            .all()
        )

        return [
            {
                "id": r.id,
                "titulo": r.titulo,
                "severidad": r.severidad,
                "fecha": r.fecha_analisis.replace(tzinfo=timezone.utc).isoformat() if r.fecha_analisis else None
            }
            for r in resultados
        ]

    finally:
        db.close()

def subir_un_archivo_base_sitio(sitio_id, archivo, ruta_relativa):
    db = SessionLocal()

    try:
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_id).first()
        if sitio is None:
            raise ValueError("Sitio no encontrado")

        # 🔒 sanitizar ruta
        ruta = Path(ruta_relativa)

        if ".." in ruta.parts:
            raise ValueError("Ruta inválida")

        filename = secure_filename(archivo.filename)

        if not archivo_permitido(filename):
            # ⛔ ignorar archivo sin romper nada
            return {
                "archivo": filename,
                "estado": "ignorado"
            }


        # 🔍 tamaño real del archivo
        archivo.seek(0, os.SEEK_END)
        size = archivo.tell()
        archivo.seek(0)

        if size > MAX_FILE_SIZE:
            raise ValueError(f"Archivo demasiado grande ({size} bytes)")

        # 📂 carpeta base del sitio
        base_sitio = os.path.join(
            current_app.config["UPLOADS_DIR"],
            "sitios",
            str(sitio.id)
        )

        # 📂 destino final respetando carpetas
        destino_final = os.path.join(
            base_sitio,
            ruta.parent
        )

        os.makedirs(destino_final, exist_ok=True)

        archivo.save(
            os.path.join(destino_final, filename)
        )

        # ✅ marcar solo si se guardó correctamente
        if not sitio.archivos_base:
            sitio.archivos_base = True
            db.commit()

        return {
            "archivo": str(ruta),
            "estado": "subido"
        }

    finally:
        db.close()
