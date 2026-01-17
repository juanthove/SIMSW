from sqlalchemy.exc import IntegrityError
from database.connection import SessionLocal
from database.models.informe_model import Informe
from database.models.analisis_model import Analisis
from database.models.sitioWeb_model import SitioWeb


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
        result = (
            db.query(Informe, Analisis, SitioWeb)
            .join(Analisis, Informe.analisis_id == Analisis.id)
            .join(SitioWeb, Analisis.sitio_web_id == SitioWeb.id)
            .filter(Informe.id == informe_id)
            .first()
        )

        if result is None:
            return None

        informe, analisis, sitio = result

        return {
            # ===== INFORME =====
            "id": informe.id,
            "titulo": informe.titulo,
            "descripcion": informe.descripcion,
            "impacto": informe.impacto,
            "recomendacion": informe.recomendacion,
            "evidencia": informe.evidencia,
            "severidad": informe.severidad,
            "codigo": informe.codigo,

            # ===== CONTEXTO DEL ANÁLISIS =====
            "analisisId": analisis.id,
            "tipoAnalisis": analisis.tipo,
            "estadoAnalisis": analisis.estado,
            "resultadoGlobal": analisis.resultado_global,
            "fechaAnalisis": analisis.fecha.isoformat() if analisis.fecha else None,

            # ===== CONTEXTO DEL SITIO =====
            "siteId": sitio.id,
            "url": sitio.url,
        }

    finally:
        db.close()



# Obtener informes por análisis
def obtener_informes_por_analisis(analisis_id):
    db = SessionLocal()
    try:
        # Verifico que el análisis exista
        analisis = db.query(Analisis).filter(
            Analisis.id == analisis_id
        ).first()

        if not analisis:
            return None

        informes = (
            db.query(Informe)
            .filter(Informe.analisis_id == analisis_id)
            .order_by(Informe.severidad.desc())
            .all()
        )

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
