#Controlador, llama a ejecutar analisis y guarda en la base de datos

from .analysis_service import ejecutar_analisis_estatico, ejecutar_analisis_dinamico, ejecutar_analisis_sonar_qube
from database.connection import SessionLocal
from database.models.analisis_model import Analisis
from database.models.informe_model import Informe
from database.models.detalleOZ_model import DetalleOZ
from database.models.sitioWeb_model import SitioWeb
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import json

#Realiza el analisis estatico y guarda en la base de datos
def analizar_estatico(url, sitio_web_id):
    db = SessionLocal()

    try:
        # 1️⃣ Crear análisis EN PROGRESO
        analisis = Analisis(
            nombre=f"Análisis Estático - {url}",
            fecha=datetime.now(),
            tipo="estatico",
            estado="En Progreso",
            resultado_global=0,
            sitio_web_id=sitio_web_id
        )

        db.add(analisis)
        db.flush()  # Para obtener analisis.id sin commit

        # 2️⃣ Ejecutar análisis (Playwright + IA)
        resultado = ejecutar_analisis_estatico(url)

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
        db.commit()

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
            fecha=datetime.now(),
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

        db.commit()

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