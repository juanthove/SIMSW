#Controlador, llama a ejecutar analisis y guarda en la base de datos

from .analysis_service import ejecutar_analisis_estatico, ejecutar_analisis_dinamico, ejecutar_analisis_sonar_qube
from database.connection import SessionLocal
from database.models.analisis_model import Analisis
from database.models.informe_model import Informe
from database.models.sitioWeb_model import SitioWeb
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import json

#Realiza el analisis y guarda en la base de datos
def analizar_estatico(url, sitio_web_id):
    db = SessionLocal()

    try:
        # 1️⃣ Ejecutar análisis (Playwright + IA)
        resultado = ejecutar_analisis_estatico(url)

        vulnerabilidades = []
        estado_general = None
        resultado_global = 0
        hubo_datos = True

        # 2️⃣ Normalización del resultado
        if resultado == 0:
            # ❌ No se encontraron scripts
            estado_general = "SIN_DATOS"
            hubo_datos = False

        elif isinstance(resultado, list):
            vulnerabilidades_raw = resultado

        elif isinstance(resultado, dict):
            vulnerabilidades_raw = resultado.get("vulnerabilidades", [])

        else:
            estado_general = "ERROR"
            hubo_datos = False

        # 3️⃣ Procesamiento SOLO si hubo datos analizables
        if hubo_datos:
            CAMPOS_OBLIGATORIOS = {
                "titulo",
                "descripcion",
                "impacto",
                "recomendacion",
                "evidencia",
                "severidad",
                "codigo"
            }

            for v in vulnerabilidades_raw:
                if isinstance(v, dict) and CAMPOS_OBLIGATORIOS.issubset(v.keys()):
                    vulnerabilidades.append(v)

            # 🔹 Estado SOLO basado en vulnerabilidades
            estado_general = calcular_estado_general(vulnerabilidades)
            resultado_global = calcular_resultado_global(vulnerabilidades)

        # 4️⃣ Crear análisis
        analisis = Analisis(
            nombre=f"Análisis Estático - {url}",
            fecha=datetime.now(),
            tipo="estatico",
            estado=estado_general,
            resultado_global=resultado_global,
            sitio_web_id=sitio_web_id
        )

        db.add(analisis)
        db.flush()

        # 5️⃣ Crear informes SOLO si hay vulnerabilidades
        if hubo_datos:
            for v in vulnerabilidades:
                informe = Informe(
                    titulo=v["titulo"],
                    descripcion=v["descripcion"],
                    impacto=v["impacto"],
                    recomendacion=v["recomendacion"],
                    evidencia=v["evidencia"],
                    severidad=v["severidad"],
                    codigo=v["codigo"],
                    analisis_id=analisis.id
                )
                db.add(informe)

        db.commit()

        return {
            "analisis_id": analisis.id,
            "estado": estado_general,
            "resultado_global": resultado_global,
            "vulnerabilidades": vulnerabilidades
        }

    except Exception as e:
        db.rollback()

        # 🟥 Guardar análisis fallido
        analisis = Analisis(
            nombre=f"Análisis Estático - {url}",
            fecha=datetime.now(),
            tipo="estatico",
            estado="ERROR",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )
        db.add(analisis)
        db.commit()

        return {
            "analisis_id": analisis.id,
            "estado": "ERROR",
            "mensaje": "Ocurrió un error durante el análisis"
        }

    finally:
        db.close()






def calcular_estado_general(vulnerabilidades):
    if not vulnerabilidades:
        return "SIN_VULNERABILIDADES"

    severidades = [v["severidad"] for v in vulnerabilidades]

    if any(s >= 4 for s in severidades):
        return "CRITICO"
    elif any(s == 3 for s in severidades):
        return "ALTO"
    elif any(s == 2 for s in severidades):
        return "MEDIO"
    else:
        return "BAJO"




def calcular_resultado_global(vulnerabilidades):
    if not vulnerabilidades:
        return 0

    total = 0
    cantidad = 0

    for v in vulnerabilidades:
        if not isinstance(v, dict):
            continue

        sev = v.get("severidad")
        if isinstance(sev, int):
            total += sev
            cantidad += 1

    if cantidad == 0:
        return 0

    maximo = cantidad * 3
    return round((total / maximo) * 100)









def analizar_dinamico(url):
    print("Entre en el de control")
    resultado = ejecutar_analisis_dinamico(url)

    return {
        "url": url,
        "resultado": resultado
    }

def analizar_sonar_qube(url):
    pass