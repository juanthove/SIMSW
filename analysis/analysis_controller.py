#Controlador, llama a ejecutar analisis y guarda en la base de datos

from .analysis_service import ejecutar_analisis_estatico, ejecutar_analisis_dinamico, ejecutar_analisis_alteraciones
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
        #Crear análisis En Progreso
        analisis = Analisis(
            nombre=f"Análisis Estático - {url}",
            fecha=datetime.now(timezone.utc),
            tipo="estatico",
            metodo="Manual",
            estado="En Progreso",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )

        db.add(analisis)
        db.flush()  #Obtener analisis.id sin commit

        #Ejecutar análisis
        resultado = ejecutar_analisis_estatico(sitio_web_id)

        vulnerabilidades = []
        vulnerabilidades_raw = []
        estado_final = None
        resultado_global = 0
        hubo_datos = True


        #Normalización del resultado
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

        #Procesamiento solo si hubo datos analizables
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

            #Resultado global calculado solo con vulnerabilidades válidas
            resultado_global = calcular_resultado_global(vulnerabilidades)

        #Actualizar análisis con estado final
        analisis.estado = estado_final
        analisis.resultado_global = resultado_global

        #Crear informes solo si hay vulnerabilidades
        if hubo_datos:
            for v in vulnerabilidades:
                informe = Informe(
                    titulo=v["titulo"],
                    descripcion=v["descripcion"],
                    descripcion_humana=v["descripcion_humana"],
                    impacto=v["impacto"],
                    recomendacion=v["recomendacion"],
                    evidencia=v["evidencia"],
                    severidad=v["severidad"],
                    codigo=v["codigo"],
                    analisis_id=analisis.id
                )
                db.add(informe)

        #Guardar todo

        #Actualizar fecha último monitoreo del sitio (UTC)
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        if sitio:
            sitio.fecha_ultimo_monitoreo = datetime.now(timezone.utc)

        db.commit()

        #Enviar alertas de las vulnerabilidades criticas
        enviar_alertas_criticas(sitio_web_id, vulnerabilidades, url, "estatico")

        return {
            "analisis_id": analisis.id,
            "estado": analisis.estado,
            "resultado_global": analisis.resultado_global,
            "cantidad_informes": len(vulnerabilidades)
        }

    except Exception as e:
        db.rollback()

        #Si ocurre un error, marcar análisis como Error
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
    1: 1,   #Baja
    2: 3,   #Media
    3: 6    #Alta
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




#Realiza el analisis dinamico y guarda en la base de datos
def analizar_dinamico(url, sitio_web_id):
    db = SessionLocal()
    analisis = None

    try:
        #Crear Analisis En Progreso
        analisis = Analisis(
            nombre=f"Análisis Dinámico - {url}",
            fecha=datetime.now(timezone.utc),
            tipo="dinamico",
            metodo="Manual",
            estado="En Progreso",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )
        db.add(analisis)
        db.flush()

        #Ejecutar analisis
        resultado = ejecutar_analisis_dinamico(url)

        vulnerabilidades = resultado.get("resultado_json", [])

        #Validar resultados
        vulnerabilidades_validas = []

        for v in vulnerabilidades:
            if isinstance(v, dict):
                vulnerabilidades_validas.append(v)

        #Guardar Informe y DetalleOZ
        for v in vulnerabilidades_validas:
            informe = Informe(
                titulo=v.get("titulo"),
                descripcion=v.get("descripcion"),
                descripcion_humana=v.get("descripcion_humana"),
                impacto=v.get("impacto"),
                recomendacion=v.get("recomendacion"),
                evidencia=v.get("evidencia"),
                severidad=v.get("severidad"),
                codigo=None,
                analisis_id=analisis.id
            )
            db.add(informe)
            db.flush() 

            detalle = DetalleOZ(
                informe_id=informe.id,
                endpoint=v.get("endpoint"),
                metodo=v.get("metodo"),
                parametro=v.get("parametro"),
                payload=v.get("payload")
            )

            db.add(detalle)

        #Finalizar analisis
        analisis.estado = "Finalizado"
        analisis.resultado_global = calcular_resultado_global(vulnerabilidades_validas)

        #Actualizar fecha último monitoreo del sitio (UTC)
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        if sitio:
            sitio.fecha_ultimo_monitoreo = datetime.now(timezone.utc)

        db.commit()

        #Enviar alertas de las vulnerabilidades criticas
        enviar_alertas_criticas(sitio_web_id, vulnerabilidades_validas, url, "dinamico")

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


        return {
            "analisis_id": analisis.id if analisis else None,
            "estado": "Error",
            "error": str(e)
        }

    finally:
        db.close()



#Analizar cambios entre los archivos base y la url
def analizar_alteraciones(url, sitio_web_id, metodo):
    print("[DEBUG] Se llama a analizar alteraciones")
    db = SessionLocal()
    analisis = None

    try:
        #Crear Analisis En Progreso
        print("[DEBUG] Se crea analisis")
        analisis = Analisis(
            nombre=f"Análisis de Alteraciones - {url}",
            fecha=datetime.now(timezone.utc),
            tipo="alteracion",
            metodo=metodo,
            estado="En Progreso",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )

        db.add(analisis)
        db.flush()

        #Ejecutar analisis
        resultado = ejecutar_analisis_alteraciones(sitio_web_id, url)
        estado_final = "Error"
        hubo_datos = False
        vulnerabilidades_raw = []
        resultado_global = 0

        if not resultado or not isinstance(resultado, dict):
            estado_final = "Error"
            hubo_datos = False

        elif not resultado.get("ok"):
            estado_final = "Sin Datos"
            hubo_datos = False

        elif resultado.get("mensaje") == "Sin alteraciones":
            estado_final = "Sin alteraciones"
            hubo_datos = False

        elif isinstance(resultado.get("datos"), list):
            vulnerabilidades_raw = resultado["datos"]
            estado_final = "Finalizado"
            hubo_datos = True

        else:
            estado_final = "Error"
            hubo_datos = False

        #Guardar Informe
        vulnerabilidades_validas = []

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

        if hubo_datos:
            for v in vulnerabilidades_raw:
                if isinstance(v, dict) and CAMPOS_OBLIGATORIOS.issubset(v.keys()):
                    vulnerabilidades_validas.append(v)

                    informe = Informe(
                        titulo=v["titulo"],
                        descripcion=v["descripcion"],
                        descripcion_humana=v["descripcion_humana"],
                        impacto=v["impacto"],
                        recomendacion=v["recomendacion"],
                        evidencia=v["evidencia"],
                        severidad=v["severidad"],
                        codigo=v["codigo"],
                        analisis_id=analisis.id
                    )
                    db.add(informe)

                    resultado_global = calcular_resultado_global(vulnerabilidades_validas)

        #Finalizar analisis
        analisis.estado = estado_final
        analisis.resultado_global = resultado_global

        #Actualizar último monitoreo
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        if sitio:
            if metodo == "Automatico":
                sitio.fecha_ultimo_automatico = datetime.now(timezone.utc)
            else:
                sitio.fecha_ultimo_monitoreo = datetime.now(timezone.utc)

        db.commit()

        #Enviar alertas
        if hubo_datos:
            enviar_alertas_criticas(sitio_web_id, vulnerabilidades_validas, url, "alteracion")

        return {
            "analisis_id": analisis.id,
            "estado": analisis.estado,
            "resultado_global": analisis.resultado_global,
            "cantidad_informes": len(vulnerabilidades_validas)
        }

    except Exception as e:
        print("ERROR EN ANALIZAR ALTERACIONES:", e)
        db.rollback()

        if analisis:
            analisis.estado = "Error"
            analisis.resultado_global = 0
            db.commit()

        return {
            "analisis_id": analisis.id if analisis else None,
            "estado": "Error",
            "mensaje": "Error durante el análisis de alteraciones",
            "detalle": str(e)
        }

    finally:
        db.close()




#Funcion para enviar las alertas
def enviar_alertas_criticas(sitio_web_id, vulnerabilidades, url, tipo_analisis):
    """
    Envía un mail por cada correo relacionado al sitio
    si existen vulnerabilidades de severidad 3
    """

    #Filtrar vulnerabilidades críticas
    vulnerabilidades_criticas = [
        v for v in vulnerabilidades
        if isinstance(v, dict) and v.get("severidad") == 3
    ]

    if not vulnerabilidades_criticas:
        return 0
    
    if tipo_analisis == "alteracion":
        titulo_evento = "Alteraciones críticas"
        descripcion_evento = "Se detectaron alteraciones críticas en el sitio"
    else:
        titulo_evento = "Vulnerabilidades críticas"
        descripcion_evento = "Se detectaron vulnerabilidades críticas"

    db = SessionLocal()

    try:
        #Obtener nombre del sitio
        sitio = db.query(SitioWeb).filter(SitioWeb.id == sitio_web_id).first()
        nombre_sitio = sitio.nombre if sitio else "Sitio desconocido"

        #Obtener mails relacionados al sitio
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
                asunto = f"🚨 [{fecha}] {titulo_evento} - {nombre_sitio}",
                contenido = f"""
                <b>{descripcion_evento}</b><br><br>

                <b>Sitio:</b> {nombre_sitio}<br>
                <b>URL:</b> <a href="{url}">{url}</a><br>
                <b>Cantidad:</b> {len(vulnerabilidades_criticas)}<br><br>

                Se recomienda tomar acciones inmediatas.
                """
            )

        return len(mails)

    except Exception as e:
        #No rompe el análisis si falla el mail
        return 0

    finally:
        db.close()