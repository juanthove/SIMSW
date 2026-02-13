from datetime import datetime, timezone, timedelta
from database.connection import SessionLocal
from database.models.sitioWeb_model import SitioWeb
from analysis.analysis_controller import analizar_alteraciones


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
    print("Se llama a ejecutar automatico")

    with app.app_context():   # 👈 CLAVE
        db = SessionLocal()

        try:
            sitios = db.query(SitioWeb).all()

            for sitio in sitios:
                print(f"[DEBUG] SITIO {sitio.url}, {sitio.nombre}")
                print("[DEBUG] INFO SITIO", sitio.url, sitio.fecha_ultimo_automatico, sitio.fecha_ultimo_automatico.tzinfo if sitio.fecha_ultimo_automatico else None)
                if debe_ejecutarse(sitio):
                    print(f"Ejecutando análisis automático para {sitio.url}")

                    analizar_alteraciones(url=sitio.url, sitio_web_id=sitio.id, metodo="Automatico")

        except Exception as e:
            print("Error en scheduler:", e)

        finally:
            db.close()

