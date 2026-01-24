#Funcion que realiza el analisis

from datetime import datetime

from scripts.Archivo import Archivo
from scripts.tools import *
import json
import re
from scripts.Informe import Informe
from scripts.AST import *
from scripts.vulberta_api import Vulberta as Vulberta
from scripts.Owaspzap import OwaspZap as OW
import time
from scripts.EnviarAlerta import EnviarAlerta


def extraer_json(texto):
    #Elimina bloques ```json ``` o ```
    texto = re.sub(r"```json|```", "", texto).strip()

    #Intenta extraer desde el primer [ hasta el último ]
    inicio = texto.find("[")
    fin = texto.rfind("]")

    if inicio == -1 or fin == -1:
        raise ValueError("No se encontró un JSON válido")

    return texto[inicio:fin+1]



def ejecutar_analisis_estatico(url):

    """Analiza el sitio de forma estatica"""

    try:
        print("[*] Iniciando crawling liviano...")
        crawl_results = crawl_light(url)
        print(f"[*] Páginas analizadas: {len(crawl_results)}")

        top_urls = seleccionar_urls_relevantes(crawl_results, max_urls=1)
        print(f"[*] {len(top_urls)} URLs seleccionadas para análisis profundo:\n")

        if not top_urls:
            return {
                "mensaje": "No se encontraron URLs para analizar",
                "vulnerabilidades": []
            }

        deep_results = analizar_urls_con_playwright(top_urls)

        #Quedarse solo con resultados validos
        deep_results = {
            url: data
            for url, data in deep_results.items()
            if data and isinstance(data, dict)
        }

        #Hacer checkeo para cuando no hay datos para analizar
        if not deep_results:
            return {
                "mensaje": "No se pudieron analizar las páginas del sitio",
                "vulnerabilidades": []
            }

        print("[*] Construyendo AST del sitio...")
        site_ast = []

        #Corregir error de que no se esta cargando datos en arbol para https://mixy.ba/webplala/sso.login/
        for url, extracted_data in deep_results.items():
            #print(f"-LA data extraida es: {extracted_data}")

            if not extracted_data:
                print(f"[!] Sin datos extraídos para {url}, se omite")
                continue

            page_ast = build_page_ast(url, extracted_data)
            site_ast.append(page_ast)

        if not site_ast:
            return {
                "mensaje": "No se pudo construir el AST del sitio",
                "vulnerabilidades": []
            }

        print("[*] Preparando fragmentos para VulBERTa...")
        vulberta_inputs = preparar_inputs_vulberta(site_ast)

        print("[*] VulBERTa inputs:", vulberta_inputs)
        print("[*] Cantidad de fragmentos:", len(vulberta_inputs))

        if not vulberta_inputs:
            return {
                "mensaje": "No se generaron fragmentos para análisis",
                "vulnerabilidades": []
            }

        # 🔥 Llamada directa a VulBERTa, sin SitioWeb ni Analisis
        herramienta = Vulberta(
            nombre="VulBERTa",
            version="1.0",
        )

        resultado = herramienta.analizar_sitio(vulberta_inputs)

        if not resultado:
            return {
                "mensaje": "No se detectaron vulnerabilidades",
                "vulnerabilidades": []
            }


        son = 0
        noson = 0
        lista_mayores = []

        for item in resultado:
            if item.get_label() == "Vulnerable":
                if item.get_confidence() > 0.5:
                    print(f"Es mayor a 0.5, el confidence es: {item.get_confidence()}\n")

                    lista_mayores.append({
                        "id": item.get_id(),
                        "code_fragment": item.get_code_fragment()
                    })
                    son += 1
                else:
                    print(f"Confidence es menor o igual a 0.5, es: {item.get_confidence()}\n")
                    noson += 1
            else:
                print(f"El label no es 'Vulnerable', es: {item.get_label()}\n")

        print(f"La cantidad que son mayores son: {son}, y menores: {noson}")

        if not lista_mayores:
            print(f"NO LISTA MAYORES")
            return {
                "mensaje": "No se detectaron vulnerabilidades",
                "vulnerabilidades": []
            }

        #Luego de armar la lista hacemos el prompt
        prompt = """
            Analiza la siguiente lista de fragmentos de código vulnerables segun VulBERTa(aunque pueden ser falsos positivos).

            Devuelve EXCLUSIVAMENTE un JSON válido.
            NO incluyas texto adicional.
            NO incluyas ```json ni ```.

            El JSON debe ser un array de objetos con esta estructura exacta:

            [
            {
                "titulo":  nombre técnico corto de la vulnerabilidad,
                "descripcion": explicación técnica del problema,
                "descripcion_humana": explicacion breve en lenguaje simple y entendible,
                "impacto":  consecuencias reales si se explota,
                "recomendacion": cómo corregir o mitigar la vulnerabilidad,
                "evidencia": descripción observable del problema (request, endpoint, comportamiento),
                "severidad": nivel de severidad del 1 al 3 (1=baja, 2=media, 3=alta),
                "codigo": fragmento exacto de código vulnerable
            }
            ]

            Verifica si se trata de un falso positivo, en caso de serlo, no me lo devuelvas, ignoralo.
            En caso de que ninguno sea valido, devuelve un array vacío:

            Aquí están los fragmentos:
            """

        for frag in lista_mayores:
            prompt += f"\nID: {frag['id']}, Código:\n{frag['code_fragment']}\n"

        informe = Informe()
        resultadoFinal = informe.preguntar(prompt)

        print("Respuesta de la IA recibida:\n")

        if hasattr(resultadoFinal, "content"):
            texto_ia = resultadoFinal.content
        else:
            texto_ia = resultadoFinal

        print(f"\n\n{texto_ia}\n\n\n")

        try:
            json_limpio = extraer_json(texto_ia)
            resultado_json = json.loads(json_limpio)
        except Exception as e:
            return {
                "mensaje": "La IA no devolvió un JSON válido",
                "vulnerabilidades": [],
                "error_tecnico": str(e)
            }

        return resultado_json

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

        print(f"[DEBUG] Alertas finales enviadas a IA: {len(alertas)}")

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

        print(f"[DEBUG] Vulnerabilidades finales IA: {(resultado_json)}")

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




def ejecutar_analisis_sonar_qube(ruta):
    pass