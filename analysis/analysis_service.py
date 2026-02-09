#Funcion que realiza el analisis
from scripts.tools import *
import json
import re
from scripts.Informe import Informe
from scripts.AST import *
from scripts.vulberta_api import Vulberta as Vulberta
from scripts.Owaspzap import OwaspZap as OW
import time
from flask import current_app
import os
from pathlib import Path
import shutil
import time


#Extensiones para analizarlas
EXTENSIONES_ANALIZABLES = {
    ".js",
    ".html",
    ".htm",
    ".php",
    ".py",
    ".json"
}


def extraer_json(texto):
    #Elimina bloques ```json ``` o ```
    texto = re.sub(r"```json|```", "", texto).strip()

    #Intenta extraer desde el primer [ hasta el último ]
    inicio = texto.find("[")
    fin = texto.rfind("]")

    if inicio == -1 or fin == -1:
        raise ValueError("No se encontró un JSON válido")

    return texto[inicio:fin+1]



def promt_default(lista_mayores):
    
    prompt = """
        Actúas como un analista de seguridad de aplicaciones senior.

        Recibirás DOS CONJUNTOS DE INFORMACIÓN:

        1) Fragmentos de código que un modelo ML (VulBERTa) clasificó como VULNERABLES.
        → Estos tienen ALTA PRIORIDAD.

        2) Hallazgos detectados por Semgrep (análisis estático basado en reglas).
        → Estos pueden contener FALSOS POSITIVOS.

        Tu tarea:
        - Analizar TODOS los fragmentos.
        - Verificar si existe sanitización o mitigación real.
        - Detectar falsos positivos.
        - Devolver SOLO vulnerabilidades reales.
        - Si un fragmento NO es vulnerable, IGNORARLO.

        Devuelve EXCLUSIVAMENTE un JSON válido.
        NO agregues texto adicional.
        NO uses ```json.

        Estructura exacta del JSON:

        [
        {
            "titulo":  nombre técnico corto de la vulnerabilidad,
            "descripcion": explicación técnica del problema,
            "descripcion_humana": explicacion breve en lenguaje simple y entendible,
            "impacto":  consecuencias reales si se explota,
            "recomendacion": cómo corregir o mitigar la vulnerabilidad,
            "evidencia": descripción observable del problema (request, endpoint, comportamiento) y nombre del archivo donde se encuentra la vulnerabilidad sin su ruta,
            "severidad": nivel de severidad del 1 al 3 (1=baja, 2=media, 3=alta),
            "codigo": fragmento exacto de código vulnerable
        }
        ]

        Si no hay vulnerabilidades reales, devuelve [].
        """

    prompt += "\n=== FRAGMENTOS MARCADOS COMO VULNERABLES POR VulBERTa ===\n"

    for frag in lista_mayores:
        prompt += f"Código:\n{frag['code_fragment']}\n"
    
    prompt += "\n=== HALLAZGOS DETECTADOS POR SEMGREP ===\n"

    return prompt


def dividir_en_chunks(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i+n]



def ejecutar_analisis_estatico(sitio_web_id):

    """Analiza el sitio de forma estatica"""



    #Buscar sitio en carpeta
    ruta_base = os.path.join(current_app.config["UPLOADS_DIR"], "sitios", str(sitio_web_id))

    try:
        print(ruta_base)
        vulberta_data = run_semgrep_analysis(ruta_base)
        if not vulberta_data:
            return {
                "mensaje": "No se generaron fragmentos para análisis",
                "vulnerabilidades": []
            }

        # 🔥 Llamada directa a VulBERTa, sin SitioWeb ni Analisis
        herramienta = Vulberta(
            nombre="VulBERTa",
            version="1.0",
        )
        
        archivos = []
        for data in vulberta_data:
            archivos.append(data["code_context"])

        resultado = herramienta.analizar_sitio(list(set(archivos)))
        

        if not resultado:
            return {
                "mensaje": "No se detectaron vulnerabilidades",
                "vulnerabilidades": []
            }


        lista_mayores = []

        for item in resultado:
            if item.get_label() == "Vulnerable":
                lista_mayores.append({
                        "id": item.get_id(),
                        "code_fragment": item.get_code_fragment()
                    })
        
        resultados_finales = []
        chunk_size = 15
        informe = Informe()
        for bloque in dividir_en_chunks(vulberta_data, chunk_size):
            prompt = promt_default(lista_mayores)
            for f in bloque:
                prompt += f"""
                Archivo: {f['path']}
                CWE: {f['cwe']}
                OWASP: {f['owasp']}
                Check ID: {f['check_id']}

                Codigo sin contexto:
                {f['code']}
                Código con contexto:
                {f['code_context']}
                """
            respuesta = informe.preguntar(prompt)

            texto_ia = (
                respuesta.content
                if hasattr(respuesta, "content")
                else respuesta
            )


            # 4️⃣ Parsear JSON
            try:
                json_limpio = extraer_json(texto_ia)
                resultado_chunk = json.loads(json_limpio)

                if isinstance(resultado_chunk, list):
                    resultados_finales.extend(resultado_chunk)

            except Exception as e:
                #Pongo continue para que no se rompa por el fallo de un chunk
                continue

        return resultados_finales
    
    except Exception as e:
        print(f"[!] Error inesperado en análisis estático: {e}")
        return {
            "mensaje": "Error inesperado durante el análisis estático",
            "vulnerabilidades": [],
            "error_tecnico": str(e)
        }





def ejecutar_analisis_dinamico(url):
    """
    Análisis dinámico usando OWASP ZAP + IA
    - ZAP se ejecuta
    - Se obtienen alertas
    - Se deduplican
    - Se llama a la IA UNA SOLA VEZ
    - Devuelve SOLO el JSON final (igual que el análisis estático)
    """

    try:
        # ===============================
        # 1️⃣ Inicializar ZAP
        # ===============================
        herramienta = OW(
            nombre="OWASP ZAP",
            version="2.17.0"
        )
        herramienta.start_zap()

        # ===============================
        # 2️⃣ Ejecutar escaneo activo
        # ===============================
        alertas = herramienta.scan_activo(url)

        if not alertas or not isinstance(alertas, list):
            return {
                "mensaje": "ZAP no devolvió alertas",
                "resultado_json": []
            }

        # ===============================
        # 3️⃣ Deduplicar alertas
        # ===============================
        alertas = deduplicar_alertas(alertas)

        if not alertas:
            return {
                "mensaje": "No se detectaron vulnerabilidades dinámicas",
                "resultado_json": []
            }


        # ===============================
        # 4️⃣ Construir PROMPT (UNA VEZ)
        # ===============================
        prompt = """
        Eres un analista de seguridad especializado en pruebas DAST y OWASP.

        Se te proporcionará un conjunto de alertas detectadas por OWASP ZAP
        correspondientes a un único análisis dinámico de un sitio web.

        Tu tarea es analizar TODAS las alertas en conjunto y devolver
        EXCLUSIVAMENTE un JSON válido.

        NO incluyas texto adicional.
        NO markdown.
        NO ```.

        Devuelve un ARRAY con esta estructura EXACTA:

        [
        {
            "titulo":  nombre técnico corto de la vulnerabilidad,
            "descripcion": explicación técnica del problema,
            "descripcion_humana": explicacion breve en lenguaje simple y entendible,
            "impacto":  consecuencias reales si se explota,
            "recomendacion": cómo corregir o mitigar la vulnerabilidad utilizando la solucion sugeria por owasp zap como referencia principal adaptada al contexto general del sitio,
            "evidencia": Descripción concreta y observable que demuestra la vulnerabilidad y debe explicar QUÉ se observó y POR QUÉ confirma el problema,
            "severidad": nivel de severidad del 1 al 3 (1=baja, 2=media, 3=alta),
            "endpoint": "...",
            "metodo": "...",
            "parametro": "Nombre del parámetro afectado. Puede ser un parámetro de query/body, un header HTTP o una cookie",
            "payload": "Valor o carga utilizada por OWASP ZAP para evidenciar el problema (por ejemplo: payload de inyección, valor malicioso o inesperado). Si no hay payload claro, dejar vacío. NO inventar payloads"
        }
        ]

        Reglas:
        - Usa el CWE como referencia principal.
        - NO inventes código fuente.
        - Usa la evidencia proporcionada.
        - Severidad:
            Low → 1
            Medium → 2
            High → 3
        - Si una alerta es meramente informativa, duplicada o falso positivo,
        NO la incluyas en el resultado final.
        - Cada objeto del array representa UNA vulnerabilidad real.

        Alertas detectadas por OWASP ZAP:
        """

        for alerta in alertas:
            prompt += f"""
            ---
            Nombre de la alerta: {alerta.get("tipo")}
            Nivel de riesgo: {alerta.get("riesgo")}
            CWE asociado: {alerta.get("cwe")}
            Descripción técnica: {alerta.get("descripcion")}
            Impacto potencial: {alerta.get("impacto")}
            Recomendación de ZAP: {alerta.get("solucion")}
            Evidencia técnica: {json.dumps(alerta.get("evidencia"), ensure_ascii=False)}
            """

        # ===============================
        # 5️⃣ Llamada a IA (UNA SOLA VEZ)
        # ===============================
        informe = Informe()
        respuesta_ia = informe.preguntar(prompt)

        texto_ia = (
            respuesta_ia.content
            if hasattr(respuesta_ia, "content")
            else respuesta_ia
        )

        # ===============================
        # 6️⃣ Parsear JSON de IA
        # ===============================
        try:
            json_limpio = extraer_json(texto_ia)
            resultado_json = json.loads(json_limpio)
        except Exception as e:
            return {
                "mensaje": "La IA no devolvió un JSON válido",
                "resultado_json": [],
                "error_tecnico": str(e)
            }

        if not isinstance(resultado_json, list):
            return {
                "mensaje": "La IA no devolvió un array válido",
                "resultado_json": []
            }

        # ===============================
        # 7️⃣ Resultado final (IGUAL AL ESTÁTICO)
        # ===============================
        return {
            "resultado_json": resultado_json
        }

    except Exception as e:
        print(f"[!] Error inesperado en análisis dinámico: {e}")
        return {
            "mensaje": "Error inesperado durante el análisis dinámico",
            "resultado_json": [],
            "error_tecnico": str(e)
        }






#Eliminar alertas iguales
def deduplicar_alertas(alertas):
    vistas = {}
    resultado = []

    for a in alertas:
        key = (
            a.get("alert"),                 # Nombre técnico
            a.get("risk"),                  # Severidad
            a.get("cweid") or a.get("cwe"), # CWE
            a.get("param", "").lower()      # Header / parámetro
        )

        if key not in vistas:
            # Clonar alerta base
            a["evidencias"] = [a.get("url")]
            vistas[key] = a
            resultado.append(a)
        else:
            # Acumular endpoints como evidencia
            vistas[key]["evidencias"].append(a.get("url"))

    return resultado


#Analizar cambios entre los archivos base y la url
def ejecutar_analisis_alteraciones(sitio_web_id, url):

    BASE_UPLOADS = current_app.config["UPLOADS_DIR"]

    # 📁 Carpetas
    base_dir = Path(BASE_UPLOADS) / "sitios" / str(sitio_web_id)
    tmp_dir = Path(BASE_UPLOADS) / "alteraciones_tmp" / f"{sitio_web_id}_{int(time.time())}"

    os.makedirs(tmp_dir, exist_ok=True)

    try:
        # ===============================
        # 1️⃣ Descargar recursos actuales
        # ===============================

        res = crawl_light(url)
        relevantes = seleccionar_urls_relevantes(res)

        resources_globales = {}

        for page_url in relevantes:
            fetched = fetch_site_resources(page_url)

            for resource_url, content in fetched.items():
                # deduplicar por URL
                if resource_url not in resources_globales:
                    resources_globales[resource_url] = content
        

        if not resources_globales:
            return {
                "ok": False,
                "datos": [],
                "mensaje": "No se pudieron obtener recursos"
            }
        

        save_resources_to_folder(resources_globales, tmp_dir, url)

        # ===============================
        # 2️⃣ Comparar archivos
        # ===============================
        diferencias = []

        archivos_nuevos = set()

        for new_file in tmp_dir.rglob("*"):
            if not new_file.is_file():
                continue

            ext = new_file.suffix.lower()

            # 🚫 Ignorar archivos no analizables
            if ext not in EXTENSIONES_ANALIZABLES:
                continue

            # 📂 Path relativo respecto a tmp_dir
            relative_path = new_file.relative_to(tmp_dir)
            relative_path_str = relative_path.as_posix()

            archivos_nuevos.add(relative_path_str)

            old_file = base_dir / relative_path


            if old_file.exists() and not old_file.is_file():
                continue

            if not old_file.exists():
                # 🆕 Archivo nuevo → potencial riesgo
                diferencias.append({
                    "archivo": relative_path_str,
                    "type": "insert",
                    "category": "archivo_nuevo",
                    "old_start_line": None,
                    "old_end_line": None,
                    "new_start_line": None,
                    "new_end_line": None,
                    "old_content": "",
                    "new_content": "Archivo nuevo no presente en versión base"
                })
                continue

            # ===============================
            # Comparar según tipo
            # ===============================
            try:
                if ext in {".html", ".htm"}:
                    cambios = compare_html_files(old_file, new_file)

                else:
                    cambios = compare_text_files(old_file, new_file)

            except Exception as e:
                #Error
                diferencias.append({
                    "archivo": relative_path_str,
                    "type": "error",
                    "category": "error_lectura",
                    "old_start_line": None,
                    "old_end_line": None,
                    "new_start_line": None,
                    "new_end_line": None,
                    "old_content": "",
                    "new_content": str(e)
                })
                continue

            if cambios:
                for c in cambios:
                    c["archivo"] = relative_path_str
                    diferencias.append(c)




        #FALTARIA AGREGAR LOS ARCHIVOS QUE SE HAYAN ELIMINADO PERO ESO SOLO SIRVE SI DESCARGAMOS TODO
        '''archivos_base = {
            f.relative_to(base_dir).as_posix()
            for f in base_dir.rglob("*")
            if f.is_file() and f.suffix.lower() in EXTENSIONES_ANALIZABLES
        }

        #Archivos eliminados
        for archivo in archivos_base - archivos_nuevos:
            diferencias.append({
                "archivo": archivo,
                "type": "delete",
                "category": "archivo_eliminado",
                "old_start_line": None,
                "old_end_line": None,
                "new_start_line": None,
                "new_end_line": None,
                "old_content": "Archivo presente en versión base",
                "new_content": ""
            })'''
        



        #Si no existen diferencias termino y mando el estado de sin alteraciones
        if not diferencias:
            return {
                "ok": True,
                "datos": [],
                "mensaje": "Sin alteraciones"
            }

        # ===============================
        # 3️⃣ Llamar IA
        # ===============================
        prompt = prompt_alteraciones(diferencias)

        informe = Informe()
        respuesta = informe.preguntar(prompt)

        texto_ia = (
            respuesta.content
            if hasattr(respuesta, "content")
            else respuesta
        )

        try:
            json_limpio = extraer_json(texto_ia)
            resultado = json.loads(json_limpio)
        except Exception:
            resultado = []

        return {
            "ok": True,
            "datos": resultado,  # lista de alteraciones
            "mensaje": None
        }

    finally:
        #Eliminar carpeta descargada
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass



def prompt_alteraciones(diffs):
    prompt = """
    Actúas como un analista de seguridad senior especializado en
    detección de alteraciones maliciosas en código web.

    Se te proporcionarán DIFERENCIAS entre archivos BASE confiables
    y archivos ACTUALES descargados desde producción.

    Tu tarea:
    - Analizar los cambios
    - Detectar inyecciones maliciosas, backdoors, obfuscación,
      scripts sospechosos, trackers no autorizados, etc.
    - Ignorar cambios legítimos
    - Devolver SOLO alteraciones con impacto en seguridad
    - Ten en cuenta que el proyecto puede ser ASP.NET

    Devuelve EXCLUSIVAMENTE un JSON válido con esta estructura EXACTA:

    [
      {
        "titulo": "...",
        "descripcion": "...",
        "descripcion_humana": "...",
        "impacto": "...",
        "recomendacion": "...",
        "evidencia": "...",
        "severidad": 1|2|3,
        "codigo": "fragmento alterado"
      }
    ]

    Si no hay alteraciones de seguridad, devuelve [].
    """

    for d in diffs:
        prompt += f"""
        ---
        Archivo: {d.get("archivo")}
        Tipo de cambio: {d.get("type", "unknown")}
        Categoría: {d.get("category", "unknown")}

        Código anterior:
        {d.get("old_content", "")}

        Código actual:
        {d.get("new_content", "")}
        """

    return prompt
