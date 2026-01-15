#Funcion que realiza el analisis

from datetime import datetime

from scripts.SitioWeb import SitioWeb
from scripts.Analisis import Analisis
from scripts.Archivo import Archivo
from scripts.tools import *
import json
import re
from scripts.Informe import Informe
from scripts.AST import *


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
    
    print("[*] Iniciando crawling liviano...")
    crawl_results = crawl_light(url)
    print(f"[*] Páginas analizadas: {len(crawl_results)}")
    top_urls = seleccionar_urls_relevantes(crawl_results, max_urls=1)
    print(f"[*] {len(top_urls)} URLs seleccionadas para análisis profundo:\n")

    deep_results = analizar_urls_con_playwright(top_urls)

    #Hacer checkeo para cuando no hay datos para analizar
    #Checkear que esto ande bien para todos los casos, y que no de el error de
    #Si el primero (internos) es {}, los demas, por mas de que no sean {}, no los toma

    print("[*] Construyendo AST del sitio...")
    site_ast = []

    #Corregir error de que no se esta cargando datos en arbol para https://mixy.ba/webplala/sso.login/
    for url, extracted_data in deep_results.items():
        #print(f"-LA data extraida es: {extracted_data}")
        page_ast = build_page_ast(url, extracted_data)
        site_ast.append(page_ast)


    print("[*] Preparando fragmentos para VulBERTa...")
    vulberta_inputs = preparar_inputs_vulberta(site_ast)

    #Armar despues los archivos y pasarlos al SitioWeb
    st = SitioWeb(1, "No se", url, "propietario", None, None, vulberta_inputs)


    fecha_actual = datetime.now()


    analisis = Analisis(1, fecha_actual, "No terminado", "estatico", st)

    resultado = analisis.ejectutar_estatico()
    son = 0
    noson = 0 
    lista_mayores = []
    for item in resultado:
        if(item.get_label() == "Vulnerable"):
            if(item.get_confidence() > 0.5):
                print(f"Es mayor a 0.7, el condidebnce es: {item.get_confidence()}\n")
                
                lista_mayores.append({
                    "id": item.get_id(),
                    "code_fragment": item.get_code_fragment()
                })
                son = son + 1
            else:
                print(f"confidence es menor o igual a 0.7, es: {item.get_confidence()}\n")
                noson = noson + 1
        else:
            print(f"El label no es vulnerable, es: {item.get_confidence()}\n")


    print(f"La cantidad que son mayores son:{son}, y menores: {noson}")


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
        raise Exception(f"La IA no devolvió JSON válido: {str(e)}")

    return resultado_json


def ejecutar_analisis_dinamico(url):
    "Analisis del sitio en forma dinamica, mediante el uso de Owasp Zap"

    print("Entre en el de servicios")
    st = SitioWeb(1, "No se", url, "propietario", None, None, None)
    fecha_actual = datetime.now()
    analisis = Analisis(1, fecha_actual, "No terminado", "Dinamico", st)

    resultado = analisis.ejectutar_dinamico()

    return resultado

def ejecutar_analisis_sonar_qube(ruta):
    pass