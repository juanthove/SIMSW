from datetime import datetime, timezone, timedelta
from database.connection import SessionLocal
from database.models.sitioWeb_model import SitioWeb
from analysis.analysis_controller import analizar_alteraciones
import logging

logger = logging.getLogger(__name__)


def debe_ejecutarse(sitio):
    if not sitio.frecuencia_monitoreo_minutos:
        return False
    
    if not sitio.archivos_base:
        return False

    if not sitio.fecha_ultimo_automatico:
        return True  #Si nunca se realizó analisis

    proxima_ejecucion = sitio.fecha_ultimo_automatico.replace(tzinfo=timezone.utc) + timedelta(minutes=sitio.frecuencia_monitoreo_minutos)

    return datetime.now(timezone.utc) >= proxima_ejecucion


def ejecutar_analisis_automaticos(app):

    with app.app_context():
        db = SessionLocal()

        try:
            #Obtener sitios
            try:
                sitios = db.query(SitioWeb).all()
            except Exception:
                logger.exception("Error obteniendo sitios desde la base de datos")
                return

            #Procesar cada sitio de forma aislada
            for sitio in sitios:
                try:
                    if debe_ejecutarse(sitio):
                        analizar_alteraciones(
                            url=sitio.url,
                            sitio_web_id=sitio.id,
                            metodo="Automatico"
                        )
                except Exception:
                    logger.exception(f"Error analizando sitio id={sitio.id}, url={sitio.url}")

        finally:
            db.close()

