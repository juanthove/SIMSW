from database.connection import SessionLocal
from database.models.analisis_model import Analisis
from sqlalchemy.exc import IntegrityError

# Obtener todos los análisis
def obtener_analisis():
    db = SessionLocal()
    try:
        analisis = db.query(Analisis).all()
        return [a.to_dict() for a in analisis]
    finally:
        db.close()


# Obtener análisis por ID
def obtener_analisis_por_id(analisis_id):
    db = SessionLocal()
    try:
        analisis = db.query(Analisis).filter(Analisis.id == analisis_id).first()
        return analisis.to_dict() if analisis else None
    finally:
        db.close()

#Obtener todos los analisis de un sitio web por id
def obtener_analisis_por_sitio(sitio_web_id):
    db = SessionLocal()
    try:
        analisis = (
            db.query(Analisis)
            .filter(Analisis.sitio_web_id == sitio_web_id)
            .order_by(Analisis.fecha.desc())
            .all()
        )

        return [a.to_dict() for a in analisis]

    finally:
        db.close()


# Crear análisis
def crear_analisis(data):
    db = SessionLocal()
    try:
        analisis = Analisis(
            nombre=data.get("nombre"),
            tipo=data.get("tipo"),
            estado=data.get("estado"),
            resultado_global=data.get("resultado_global", 0),
            sitio_web_id=data.get("sitio_web_id")
        )

        db.add(analisis)
        db.commit()
        db.refresh(analisis)

        return analisis.to_dict()

    except IntegrityError:
        db.rollback()
        raise ValueError("ERROR_INTEGRIDAD")

    finally:
        db.close()


# Actualizar análisis
def actualizar_analisis(analisis_id, data):
    db = SessionLocal()
    try:
        analisis = db.query(Analisis).filter(Analisis.id == analisis_id).first()
        if not analisis:
            return None

        analisis.nombre = data.get("nombre", analisis.nombre)
        analisis.tipo = data.get("tipo", analisis.tipo)
        analisis.estado = data.get("estado", analisis.estado)
        analisis.resultado_global = data.get(
            "resultado_global", analisis.resultado_global
        )
        analisis.sitio_web_id = data.get(
            "sitio_web_id", analisis.sitio_web_id
        )

        db.commit()
        db.refresh(analisis)

        return analisis.to_dict()

    finally:
        db.close()


# Eliminar análisis
def eliminar_analisis(analisis_id):
    db = SessionLocal()
    try:
        analisis = db.query(Analisis).filter(Analisis.id == analisis_id).first()
        if not analisis:
            return False

        db.delete(analisis)
        db.commit()
        return True

    finally:
        db.close()
