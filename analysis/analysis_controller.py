#Controlador, llama a ejecutar analisis y guarda en la base de datos

from .analysis_service import ejecutar_analisis_estatico, ejecutar_analisis_dinamico, ejecutar_analisis_sonar_qube
from database.connection import SessionLocal
from database.models.analisis_model import Analisis
from database.models.informe_model import Informe
from database.models.detalleOZ_model import DetalleOZ
from database.models.sitioWeb_model import SitioWeb
from database.models.sitioMail_model import SitioMail
from database.models.mail_model import Mail
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
import json
from database.controllers.mail_controller import obtener_mails_por_sitio
from scripts.EnviarAlerta import EnviarAlerta
from datetime import datetime


#Realiza el analisis estatico y guarda en la base de datos
def analizar_estatico(url, sitio_web_id):
    db = SessionLocal()

    try:
        # 1️⃣ Crear análisis EN PROGRESO
        analisis = Analisis(
            nombre=f"Análisis Estático - {url}",
            fecha=datetime.now(timezone.utc),
            tipo="estatico",
            estado="En Progreso",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )

        db.add(analisis)
        db.flush()  # Para obtener analisis.id sin commit

        # 2️⃣ Ejecutar análisis (Playwright + IA)
        resultado = ejecutar_analisis_estatico(sitio_web_id)

        vulnerabilidades = []
        vulnerabilidades_raw = []
        estado_final = None
        resultado_global = 0
        hubo_datos = True

        # 3️⃣ Normalización del resultado
        if isinstance(resultado, list) and len(resultado) == 0:
            estado_final = "Sin Datos"
            hubo_datos = False
        
        elif isinstance(resultado, dict) and not resultado.get("vulnerabilidades"):
            estado_final = "Sin Datos"
            hubo_datos = False

        elif isinstance(resultado, list):
            vulnerabilidades_raw = resultado
            estado_final = "Finalizado"

        elif isinstance(resultado, dict):
            vulnerabilidades_raw = resultado.get("vulnerabilidades", [])
            estado_final = "Finalizado"

        else:
            estado_final = "Error"
            hubo_datos = False

        # 4️⃣ Procesamiento SOLO si hubo datos analizables
        if hubo_datos:
            CAMPOS_OBLIGATORIOS = {
                "titulo",
                "descripcion",
                "descripcion_humana",
                "impacto",
                "recomendacion",
                "evidencia",
                "severidad",
                "codigo"
            }

            for v in vulnerabilidades_raw:
                if isinstance(v, dict) and CAMPOS_OBLIGATORIOS.issubset(v.keys()):
                    vulnerabilidades.append(v)

            # 🔹 Resultado global calculado SOLO con vulnerabilidades válidas
            resultado_global = calcular_resultado_global(vulnerabilidades)

        # 5️⃣ Actualizar análisis con estado final
        analisis.estado = estado_final
        analisis.resultado_global = resultado_global

        # 6️⃣ Crear informes SOLO si hay vulnerabilidades
        if hubo_datos:
            for v in vulnerabilidades:
                informe = Informe(
                    titulo=v["titulo"],
                    descripcion=v["descripcion"],
                    descripcion_humana=v["descripcion_humana"],
                    impacto=v["impacto"],
                    recomendacion=v["recomendacion"],
                    evidencia=v["evidencia"],
                    severidad=v["severidad"],  # 1, 2 o 3 (Baja, Media, Alta en frontend)
                    codigo=v["codigo"],
                    analisis_id=analisis.id
                )
                db.add(informe)

        # 7️⃣ Guardar todo

        #Actualizar fecha último monitoreo del sitio (UTC)
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        if sitio:
            sitio.fecha_ultimo_monitoreo = datetime.now(timezone.utc)

        db.commit()

        #Enviar alertas de las vulnerabilidades criticas
        enviar_alertas_criticas(sitio_web_id, vulnerabilidades, url)

        return {
            "analisis_id": analisis.id,
            "estado": analisis.estado,
            "resultado_global": analisis.resultado_global,
            "cantidad_informes": len(vulnerabilidades)
        }

    except Exception as e:
        db.rollback()

        # 🟥 Si ocurre un error, marcar análisis como ERROR
        analisis.estado = "Error"
        analisis.resultado_global = 0
        db.commit()

        return {
            "analisis_id": analisis.id,
            "estado": "Error",
            "mensaje": "Ocurrió un error durante el análisis"
        }

    finally:
        db.close()







PESOS = {
    1: 1,   # Baja
    2: 3,   # Media
    3: 6    # Alta
}

def calcular_resultado_global(vulnerabilidades):
    if not vulnerabilidades:
        return 0

    total = 0
    maximo = 0

    for v in vulnerabilidades:
        sev = v.get("severidad")
        if sev in PESOS:
            total += PESOS[sev]
            maximo += PESOS[3]

    if maximo == 0:
        return 0

    return round((total / maximo) * 100)




def enviar_alertas_criticas(sitio_web_id, vulnerabilidades, url):
    """
    Envía un mail por cada correo relacionado al sitio
    si existen vulnerabilidades de severidad 3
    """

    # 🔴 Filtrar vulnerabilidades críticas
    vulnerabilidades_criticas = [
        v for v in vulnerabilidades
        if isinstance(v, dict) and v.get("severidad") == 3
    ]

    if not vulnerabilidades_criticas:
        return 0

    db = SessionLocal()

    try:
        # 🏷️ Obtener nombre del sitio
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        nombre_sitio = sitio.nombre if sitio else "Sitio desconocido"

        # 📬 Obtener mails relacionados al sitio
        mails = (
            db.query(Mail)
            .join(SitioMail, SitioMail.mail_id == Mail.id)
            .filter(SitioMail.sitio_web_id == sitio_web_id)
            .all()
        )

        if not mails:
            return 0

        alerta = EnviarAlerta()

        for mail in mails:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            alerta.enviar_alerta(
                destinatario=mail.correo,
                asunto = f"🚨 [{fecha}] Vulnerabilidades críticas - {nombre_sitio}",
                contenido = f"""
                <b>Se detectaron vulnerabilidades críticas</b><br><br>

                <b>Sitio:</b> {nombre_sitio}<br>
                <b>URL:</b> <a href="{url}">{url}</a><br>
                <b>Cantidad:</b> {len(vulnerabilidades_criticas)}<br><br>

                Se recomienda tomar acciones inmediatas.
                """
            )

        return len(mails)

    except Exception as e:
        # ⚠️ No rompe el análisis si falla el mail
        print("[WARN] Error enviando alertas críticas:", str(e))
        return 0

    finally:
        db.close()








#Realiza el analisis dinamico y guarda en la base de datos
def analizar_dinamico(url, sitio_web_id):
    db = SessionLocal()
    analisis = None

    try:
        # ===============================
        # CREAR ANÁLISIS
        # ===============================
        analisis = Analisis(
            nombre=f"Análisis Dinámico - {url}",
            fecha=datetime.now(timezone.utc),
            tipo="dinamico",
            estado="En Progreso",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )
        db.add(analisis)
        db.flush()

        # ===============================
        # EJECUTAR DAST
        # ===============================
        resultado = ejecutar_analisis_dinamico(url)

        vulnerabilidades = resultado.get("resultado_json", [])

        print("[DEBUG] Vulnerabilidades IA:", len(vulnerabilidades))

        # ===============================
        # VALIDAR RESULTADO IA
        # ===============================
        vulnerabilidades_validas = []

        for v in vulnerabilidades:
            if isinstance(v, dict):
                vulnerabilidades_validas.append(v)

        # ===============================
        # GUARDAR INFORMES + DETALLE OZ (1 a 1)
        # ===============================
        for v in vulnerabilidades_validas:
            informe = Informe(
                titulo=v.get("titulo"),
                descripcion=v.get("descripcion"),
                descripcion_humana=v.get("descripcion_humana"),
                impacto=v.get("impacto"),
                recomendacion=v.get("recomendacion"),
                evidencia=v.get("evidencia"),
                severidad=v.get("severidad"),
                codigo=None,  # explícito
                analisis_id=analisis.id
            )
            db.add(informe)
            db.flush()  # para obtener informe.id

            detalle = DetalleOZ(
                informe_id=informe.id,
                endpoint=v.get("endpoint"),
                metodo=v.get("metodo"),
                parametro=v.get("parametro"),
                payload=v.get("payload")
            )

            db.add(detalle)

        # ===============================
        # FINALIZAR ANÁLISIS
        # ===============================
        analisis.estado = "Finalizado"
        analisis.resultado_global = calcular_resultado_global(vulnerabilidades_validas)

        #Actualizar fecha último monitoreo del sitio (UTC)
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        if sitio:
            sitio.fecha_ultimo_monitoreo = datetime.now(timezone.utc)

        db.commit()

        #Enviar alertas de las vulnerabilidades criticas
        enviar_alertas_criticas(sitio_web_id, vulnerabilidades_validas, url)

        return {
            "analisis_id": analisis.id,
            "estado": analisis.estado,
            "resultado_global": analisis.resultado_global,
            "vulnerabilidades": len(vulnerabilidades_validas)
        }

    except Exception as e:
        db.rollback()

        if analisis:
            analisis.estado = "Error"
            analisis.resultado_global = 0
            db.commit()

        print("[ERROR] analizar_dinamico:", str(e))

        return {
            "analisis_id": analisis.id if analisis else None,
            "estado": "Error",
            "error": str(e)
        }

    finally:
        db.close()







def analizar_sonar_qube(url):
    pass