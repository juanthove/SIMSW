from flask import Flask, request, jsonify, render_template
from flask_cors import CORS


from datetime import datetime

from scripts.SitioWeb import SitioWeb
from scripts.Analisis import Analisis
from scripts.Archivo import Archivo
from scripts.tools import *
import json
import re
from scripts.Informe import Informe
from scripts.AST import *

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html') 

def extraer_json(texto):
    # elimina bloques ```json ``` o ```
    texto = re.sub(r"```json|```", "", texto).strip()

    # intenta extraer desde el primer [ hasta el último ]
    inicio = texto.find("[")
    fin = texto.rfind("]")

    if inicio == -1 or fin == -1:
        raise ValueError("No se encontró un JSON válido")

    return texto[inicio:fin+1]


@app.route("/analizarEstatico", methods=["POST"])
def ejecutar_estatico():

    """Analiza el sitio de forma estatica"""

    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    
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
        print(f"-LA data extraida es: {extracted_data}")
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

    # Supongamos que ya armaste lista_mayores con los dicts de cada fragmento
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
        texto_ia = str(resultadoFinal)

    print(f"\n\n{texto_ia}\n\n\n")

    try:
        json_limpio = extraer_json(texto_ia)
        resultado_json = json.loads(json_limpio)
    except Exception as e:
        return jsonify({
            "error": "La IA no devolvió JSON válido",
            "detalle": str(e),
            "respuesta_ia": resultadoFinal
        }), 500


    # return jsonify({
    #     "url": url,
    #     "resultado": [f.to_dict() for f in resultado]
    # })

    return jsonify({
        "url": url,
        "resultado": resultado_json
    })


@app.route("/analizarDinamico", methods=["POST"])
def analizar_dinamico():
    
    """Analiza el sitio de forma dinamica"""
    
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No se proporcionó URL"}), 400
    
    id = 0
    archivos = []
    scripts = extraer_scripts_con_playwright(url)
    

    # === EXTERNOS ===
    if "externos" in scripts and scripts["externos"]:
        for name, codigo in scripts["externos"].items():
            archivos.append(Archivo(id, name, url, None, "externo", len(codigo or ""), codigo))
            id += 1

    # === INTERNOS ===
    if "internos" in scripts and scripts["internos"]:
        for name, codigo in scripts["internos"].items():
            archivos.append(Archivo(id, name, url, None, "interno", len(codigo or ""), codigo))
            id += 1

    # === NETWORK ===
    if "network" in scripts and scripts["network"]:
        for name, codigo in scripts["network"].items():
            archivos.append(Archivo(id, name, url, None, "network", len(codigo or ""), codigo))
            id += 1

    # === WORKERS ===
    if "workers" in scripts and scripts["workers"]:
        for name, codigo in scripts["workers"].items():
            archivos.append(Archivo(id, name, url, None, "worker", len(codigo or ""), codigo))
            id += 1

    # === BLOBS ===
    if "blobs" in scripts and scripts["blobs"]:
        for name, codigo in scripts["blobs"].items():
            archivos.append(Archivo(id, name, url, None, "blob", len(codigo or ""), codigo))
            id += 1  

    # === EVENTOS INLINE ===
    if "eventos_inline" in scripts and scripts["eventos_inline"]:
        for name, info in scripts["eventos_inline"].items():
            codigo = info.get("codigo", "")
            archivos.append(Archivo(id, name, url, None, "evento_inline", len(codigo), codigo))
            id += 1
        
    
    st = SitioWeb(1, "No se", url, "propietario", None, None, archivos)


    fecha_actual = datetime.now()


    analisis = Analisis(1, fecha_actual, "No terminado", "Dinamico", st)

    resultado = analisis.ejectutar_dinamico()

            

    return jsonify({"url": url, "resultado": resultado})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    


#https://mixy.ba/webplala/sso.login/ Esta url es vulnerable

#https://app.y.gy/captcha?&id=295481 Otro vulnerable