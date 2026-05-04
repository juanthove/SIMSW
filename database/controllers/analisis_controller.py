from database.connection import SessionLocal
from database.models.analisis_model import Analisis
from database.models.informe_model import Informe
from database.models.sitioWeb_model import SitioWeb
from database.models.detalleOZ_model import DetalleOZ
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import timezone
from scripts.Reporte import generar_pdf_reporte

#Obtener todos los análisis
def obtener_analisis():
    db = SessionLocal()
    try:
        analisis = db.query(Analisis).all()
        return [a.to_dict() for a in analisis]
    finally:
        db.close()


#Obtener análisis por ID
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


#Crear análisis
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


#Actualizar análisis
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


#Eliminar análisis
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


#Obtener cantidad de analisis y fecha del ultimo
def obtener_resumen_analisis_por_sitio(sitio_web_id):
    db = SessionLocal()
    try:
        resultado = db.query(
            func.count(Analisis.id).label("cantidad"),
            func.max(Analisis.fecha).label("ultima_fecha")
        ).filter(
            Analisis.sitio_web_id == sitio_web_id
        ).one()

        return {
            "cantidad_analisis": resultado.cantidad,
            "fecha_ultimo_analisis": (
                resultado.ultima_fecha.replace(tzinfo=timezone.utc).isoformat()
                if resultado.ultima_fecha else None
            )
        }
    finally:
        db.close()


#Obtener lo datos del analisis y todos sus informes
def obtener_detalle_analisis_con_informes(analisis_id):
    db = SessionLocal()
    try:
        analisis = (
            db.query(Analisis)
            .filter(Analisis.id == analisis_id)
            .first()
        )

        if not analisis:
            return None

        informes = (
            db.query(Informe)
            .filter(Informe.analisis_id == analisis_id)
            .all()
        )

        return {
            "analisis": {
                "id_analisis": analisis.id,
                "tipo": analisis.tipo,
                "estado": analisis.estado,
                "resultado_global": analisis.resultado_global,
                "fecha": analisis.fecha.replace(tzinfo=timezone.utc).isoformat() if analisis.fecha else None
            },
            "informes": [
                {
                    "id": i.id,
                    "titulo": i.titulo,
                    "descripcion_humana": i.descripcion_humana,
                    "severidad": i.severidad
                }
                for i in informes
            ]
        }

    finally:
        db.close()

#Obtener el reporte completo de todos los informes del analisis
def obtener_reporte_completo(analisis_id):
    db = SessionLocal()
    try:
        analisis = (
            db.query(Analisis)
            .filter(Analisis.id == analisis_id)
            .first()
        )

        if not analisis:
            return None

        #Traer sitio
        sitio = db.query(SitioWeb).filter(SitioWeb.id == analisis.sitio_web_id).first()

        #Traer informes
        informes = (
            db.query(Informe)
            .filter(Informe.analisis_id == analisis_id)
            .all()
        )

        resultado_informes = []

        for i in informes:
            #Detalle OZ si existe
            detalle = db.query(DetalleOZ).filter(DetalleOZ.informe_id == i.id).first()

            detalle_oz = None

            if detalle:
                detalle_oz = {
                    "endpoint": detalle.endpoint,
                    "metodo": detalle.metodo,
                    "parametro": detalle.parametro,
                    "payload": detalle.payload
                }

            resultado_informes.append({
                "id": i.id,
                "titulo": i.titulo,
                "severidad": i.severidad,
                "descripcion": i.descripcion,
                "impacto": i.impacto,
                "recomendacion": i.recomendacion,
                "evidencia": i.evidencia,
                "codigo": i.codigo,

                "detalleOZ": detalle_oz
            })

        return {
            "analisis": {
                "id": analisis.id,
                "tipo": analisis.tipo,
                "estado": analisis.estado,
                "resultado_global": analisis.resultado_global,
                "fecha": analisis.fecha.replace(tzinfo=timezone.utc).isoformat()
                if analisis.fecha else None
            },
            "sitio": {
                "id": sitio.id if sitio else None,
                "nombre": sitio.nombre if sitio else "Sitio",
                "url": sitio.url if sitio else ""
            },
            "informes": resultado_informes
        }

    finally:
        db.close()

#Genera el PDF del analisis
def generar_pdf_analisis(analisis_id):
    """
    1. Obtiene los datos del análisis
    2. Genera el PDF
    3. Devuelve el buffer listo para enviar
    """

    data = obtener_reporte_completo(analisis_id)

    if not data:
        return None, None

    pdf_buffer = generar_pdf_reporte(data)

    nombre_archivo = (
        f"{data['sitio']['nombre']}_"
        f"{data['analisis']['tipo']}_"
        f"{data['analisis']['fecha']}"
    ).replace("/", "-")

    return pdf_buffer, nombre_archivo