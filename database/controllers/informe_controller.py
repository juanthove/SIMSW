from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models.informe_model import Informe


# Obtener todos los informes
def obtener_informes():
    db = SessionLocal()
    try:
        informes = db.query(Informe).all()
        return [i.to_dict() for i in informes]
    finally:
        db.close()


# Obtener informe por ID
def obtener_informe_por_id(informe_id):
    db = SessionLocal()
    try:
        informe = db.query(Informe).filter(Informe.id == informe_id).first()
        if informe is None:
            return None
        return informe.to_dict()
    finally:
        db.close()


# Obtener informes por análisis
def obtener_informes_por_analisis(analisis_id):
    db = SessionLocal()
    try:
        informes = db.query(Informe).filter(
            Informe.analisis_id == analisis_id
        ).all()
        return [i.to_dict() for i in informes]
    finally:
        db.close()


# Crear informe
def crear_informe(data):
    db = SessionLocal()
    try:
        informe = Informe(
            titulo=data.get("titulo"),
            descripcion=data.get("descripcion"),
            impacto=data.get("impacto"),
            recomendacion=data.get("recomendacion"),
            evidencia=data.get("evidencia"),
            severidad=data.get("severidad"),
            codigo=data.get("codigo"),
            analisis_id=data.get("analisis_id")
        )

        db.add(informe)
        db.commit()
        db.refresh(informe)

        return informe.to_dict()

    except IntegrityError:
        db.rollback()
        return None
    finally:
        db.close()


# Actualizar informe
def actualizar_informe(informe_id, data):
    db = SessionLocal()
    try:
        informe = db.query(Informe).filter(Informe.id == informe_id).first()

        if informe is None:
            return None

        informe.titulo = data.get("titulo", informe.titulo)
        informe.descripcion = data.get("descripcion", informe.descripcion)
        informe.impacto = data.get("impacto", informe.impacto)
        informe.recomendacion = data.get("recomendacion", informe.recomendacion)
        informe.evidencia = data.get("evidencia", informe.evidencia)
        informe.severidad = data.get("severidad", informe.severidad)
        informe.codigo = data.get("codigo", informe.codigo)

        db.commit()
        db.refresh(informe)

        return informe.to_dict()

    finally:
        db.close()


# Eliminar informe
def eliminar_informe(informe_id):
    db = SessionLocal()
    try:
        informe = db.query(Informe).filter(Informe.id == informe_id).first()

        if informe is None:
            return False

        db.delete(informe)
        db.commit()
        return True

    finally:
        db.close()
