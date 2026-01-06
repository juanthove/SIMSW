#from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib



#from pprint import pprint
import requests

#PAra lo de guardado
import os
import re

#De aca 

from urllib.parse import urljoin, urlparse
from collections import deque



from playwright.sync_api import sync_playwright
def crawl_light(start_url: str, timeout: int = 5, maximo = 1):
    """
    Crawling liviano SIN profundidad:
    - Recorre todo el dominio
    - Extrae solo metadatos relevantes
    - NO descarga JS externos
    """

    visited = set()
    queue = deque([start_url])
    results = []

    #urlparse recibe un url como string, lo parsea y devuelve un objeto con sus componentes
    #netloc devuelve el dominio (y purto, en casod e que exista)
    base_domain = urlparse(start_url).netloc

    while queue and len(visited) < maximo:
        url = queue.popleft() #Saca el primer elemento de la cola

        if url in visited:
            continue

        visited.add(url) #Lo marca como visitado

        try:
            #resp es la respuesta HTTP
            resp = requests.get(url, timeout=timeout)
            
            content_type = resp.headers.get("Content-Type", "") #Obtiene el tipo de contenido de la respuesta HTTP

            if "text/html" not in content_type: #verifica que sea HTML
                continue

            html = resp.text
            soup = BeautifulSoup(html, "html.parser") #en soup se almacena el HTML parseado

            #Métricas livianas
            scripts = soup.find_all("script") #Encuentra todas las etiquetas <script>
            forms = soup.find_all("form") #Encuentra todas las etiquetas <form>
            inputs = soup.find_all(["input", "textarea", "select"]) #Encuentra todas las etiquetas de entrada de datos

            #en external_scripts se almacenan las URLs de los scripts externos
            external_scripts = [
                s.get("src") for s in scripts if s.get("src")
            ]

            inline_events = [
                tag for tag in soup.find_all(True)
                if any(attr.startswith("on") for attr in tag.attrs.keys())
            ]

            page_info = {
                "url": url,
                "html_size": len(html),
                "num_scripts": len(scripts),
                "num_external_scripts": len(external_scripts),
                "num_forms": len(forms),
                "num_inputs": len(inputs),
                "has_inline_events": len(inline_events) > 0
            }

            results.append(page_info)

            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                parsed = urlparse(next_url)

                #Filtrar recursos no analizables, en caso de ser true, continue
                if parsed.path.lower().endswith((
                    ".pdf", ".jpg", ".jpeg", ".png", ".gif",
                    ".zip", ".rar", ".7z",
                    ".mp4", ".mp3",
                    ".css", ".ico"
                )):
                    continue

                # 🔗 Solo mismo dominio
                if parsed.netloc == base_domain:
                    if next_url not in visited:
                        queue.append(next_url)


        except Exception as e:
            print(f"[!] Error en crawling {url}: {e}")

    return results


def seleccionar_urls_relevantes(
    crawl_results: list,
    max_urls: int = 10
):
    """
    Selecciona las URLs más relevantes para análisis profundo
    basándose en heurísticas de seguridad.
    """

    scored = []

    for page in crawl_results:
        score = 0
        # Heurísticas (ajustables)

        score += page.get("num_forms", 0) * 5
        score += page.get("num_inputs", 0) * 2
        score += page.get("num_scripts", 0) * 1
        score += page.get("num_external_scripts", 0) * 2

        if page.get("has_inline_events"):
            score += 4

        # HTML grande → más lógica
        score += min(page.get("html_size", 0) // 5000, 5)

        scored.append({
            "url": page["url"],
            "score": score
        })

        

    # Ordenar por score descendente
    scored.sort(key=lambda x: x["score"], reverse=True)
    # Devolver solo URLs
    return [item["url"] for item in scored[:max_urls]]



# def extraer_scripts_con_playwright2(page, url: str):

#     resultado = {
#         "internos": {},
#         "externos": {},
#         "network": {},
#         "workers": {},
#         "blobs": {},
#         "eventos_inline": {}
#     }

#     seen_external = set()
#     blob_scripts = {}

#     scripts = page.evaluate("""
#         () => {
#             return Array.from(document.scripts).map((s) => ({
#                 src: s.src || null,
#                 text: s.textContent || s.innerText || null,
#                 id: s.id || null,
#                 className: s.className || null,
#                 type: s.type || null
#             }));
#         }
#     """)

#     html = page.content()
#     soup = BeautifulSoup(html, "html.parser")

#     # --------------------------------------------------------
#     # EVENTOS INLINE
#     # --------------------------------------------------------
#     eventos = [
#         "onclick","onmouseover","onmouseout","onchange",
#         "onfocus","onblur","onsubmit","onkeydown",
#         "onkeyup","onload","onerror","onmouseenter","onmouseleave"
#     ]

#     tag_counter = {}

#     for tag in soup.find_all(True):
#         for ev in eventos:
#             if tag.has_attr(ev):
#                 if tag.get("id"):
#                     clave = tag["id"].strip()
#                 else:
#                     tag_counter.setdefault(tag.name, 0)
#                     tag_counter[tag.name] += 1
#                     clave = f"{tag.name}_{tag_counter[tag.name]}"

#                 resultado["eventos_inline"][clave] = {
#                     "evento": ev,
#                     "codigo": tag.get(ev),
#                     "html": str(tag)
#                 }

#     # --------------------------------------------------------
#     # SCRIPTS INTERNOS
#     # --------------------------------------------------------
#     contador = 0
#     for s in scripts:
#         contenido = (s.get("text") or "").strip()
#         if not contenido:
#             continue

#         if s.get("id"):
#             nombre = s["id"].strip()
#         else:
#             contador += 1
#             nombre = f"script_{contador}"

#         resultado["internos"][nombre] = contenido

#     # --------------------------------------------------------
#     # SCRIPTS EXTERNOS
#     # --------------------------------------------------------
#     for s in scripts:
#         src = s.get("src")
#         if not src:
#             continue

#         if src.startswith("blob:"):
#             blob_scripts[src] = None
#             continue

#         if src.startswith(("data:", "javascript:")):
#             continue

#         src_abs = urljoin(url, src)
#         if src_abs in seen_external:
#             continue

#         seen_external.add(src_abs)

#         try:
#             r = requests.get(src_abs, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
#             resultado["externos"][src_abs] = r.text if r.status_code == 200 else None
#         except:
#             resultado["externos"][src_abs] = None

#     resultado["blobs"] = blob_scripts
#     return resultado, soup

def extraer_scripts_con_playwright2(page, url: str):

    resultado = {
        "internos": {},
        "externos": {},
        "network": {},      # 👈 NUEVO
        "workers": {},      # 👈 NUEVO
        "blobs": {},
        "eventos_inline": {}
    }

    seen_external = set()
    blob_scripts = {}

    # --------------------------------------------------------
    # NETWORK LISTENER
    # --------------------------------------------------------
    def handle_response(response):
        try:
            ct = response.headers.get("content-type", "")
            if "javascript" in ct:
                js_url = response.url
                if js_url not in resultado["network"]:
                    resultado["network"][js_url] = response.text()
        except:
            pass

    page.on("response", handle_response)

    # --------------------------------------------------------
    # EXTRAER SCRIPTS DEL DOM
    # --------------------------------------------------------
    scripts = page.evaluate("""
        () => {
            return Array.from(document.scripts).map((s) => ({
                src: s.src || null,
                text: s.textContent || s.innerText || null,
                id: s.id || null,
                className: s.className || null,
                type: s.type || null
            }));
        }
    """)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # --------------------------------------------------------
    # EVENTOS INLINE
    # --------------------------------------------------------
    eventos = [
        "onclick","onmouseover","onmouseout","onchange",
        "onfocus","onblur","onsubmit","onkeydown",
        "onkeyup","onload","onerror","onmouseenter","onmouseleave"
    ]

    tag_counter = {}

    for tag in soup.find_all(True):
        for ev in eventos:
            if tag.has_attr(ev):
                if tag.get("id"):
                    clave = tag["id"].strip()
                else:
                    tag_counter.setdefault(tag.name, 0)
                    tag_counter[tag.name] += 1
                    clave = f"{tag.name}_{tag_counter[tag.name]}"

                resultado["eventos_inline"][clave] = {
                    "evento": ev,
                    "codigo": tag.get(ev),
                    "html": str(tag)
                }

    # --------------------------------------------------------
    # SCRIPTS INTERNOS
    # --------------------------------------------------------
    contador = 0
    for s in scripts:
        contenido = (s.get("text") or "").strip()
        if not contenido:
            continue

        if s.get("id"):
            nombre = s["id"].strip()
        else:
            contador += 1
            nombre = f"script_{contador}"

        resultado["internos"][nombre] = contenido

    # --------------------------------------------------------
    # SCRIPTS EXTERNOS
    # --------------------------------------------------------
    for s in scripts:
        src = s.get("src")
        if not src:
            continue

        if src.startswith("blob:"):
            blob_scripts[src] = None
            continue

        if src.startswith(("data:", "javascript:")):
            continue

        src_abs = urljoin(url, src)
        if src_abs in seen_external:
            continue

        seen_external.add(src_abs)

        try:
            r = requests.get(src_abs, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            resultado["externos"][src_abs] = r.text if r.status_code == 200 else None
        except:
            resultado["externos"][src_abs] = None

    # --------------------------------------------------------
    # DETECTAR WORKERS (por red)
    # --------------------------------------------------------
    for js_url, code in resultado["network"].items():
        if not code:
            continue

        if (
            "new Worker(" in code or
            "new SharedWorker(" in code or
            "serviceWorker.register" in code
        ):
            resultado["workers"][js_url] = code

    resultado["blobs"] = blob_scripts
    return resultado, soup




def analizar_urls_con_playwright(
    urls: list,
    headless: bool = True,
    timeout: int = 30000
):
    """
    Dada una lista de URLs, ejecuta extracción profunda de JS,
    eventos inline, blobs, etc.
    """

    resultados = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        for url in urls:
            print(f"[+] Análisis profundo: {url}")
            page = context.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                datos, soup = extraer_scripts_con_playwright2(page, url)
                resultados[url] = datos
            except Exception as e:
                print(f"[!] Error en {url}: {e}")
            finally:
                page.close()

        browser.close()

    return resultados



#Hasata aca lo nuevo de tools






# def formatear_js_basico(codigo: str) -> str:
#     """
#     Formatea código JS de manera básica:
#     - Agrega saltos de línea tras { } ;
#     - Indenta bloques
#     """
#     # Agregar saltos de línea básicos
#     codigo = codigo.replace("{", "{\n")
#     codigo = codigo.replace("}", "\n}\n")
#     codigo = codigo.replace(";", ";\n")

#     # Quitar múltiples líneas vacías
#     lineas = [line.rstrip() for line in codigo.split("\n")]
#     codigo = "\n".join([line for line in lineas if line.strip() != ""])

#     # Indentar según llaves
#     indentado = []
#     nivel = 0
#     for line in codigo.split("\n"):
#         line_strip = line.strip()

#         if line_strip.startswith("}"):
#             nivel = max(0, nivel - 1)

#         indentado.append("    " * nivel + line_strip)

#         if line_strip.endswith("{"):
#             nivel += 1

#     return "\n".join(indentado)


def url_a_nombre_carpeta(url: str) -> str:
    # Reemplaza cualquier carácter que no sea alfanumérico, punto, guion o guion bajo por "_"
    if not url:  # None o cadena vacía
        return "url_vacia"
    return re.sub(r'[^a-zA-Z0-9._-]', '_', str(url))


def nombre_archivo_seguro(nombre: str) -> str:
    # normalizar caracteres
    base = re.sub(r'[^a-zA-Z0-9._-]', '_', nombre)

    # limitar tamaño (Windows máx. 255 chars por nombre)
    if len(base) > 80:
        base = base[:80]

    # agregar hash para evitar colisiones
    h = hashlib.md5(nombre.encode("utf-8", errors="ignore")).hexdigest()

    return f"{base}__{h}"

# def guardar_scripts_internos2(nombre, codigo, carpeta_destino: str):
#     """
#     Guarda los scripts internos, exernos, etc; en archivos .js
#     Nombre del archivo = clave del diccionario
#     Contenido = valor del diccionario
#     Se aplica formateo básico antes de guardar
#     """
#     os.makedirs(carpeta_destino, exist_ok=True)

#     rutas = []

    
#     if not nombre:
#         nombre = "sin_nombre"

#     nombre_limpio = nombre_archivo_seguro(str(nombre))
#     ruta_archivo = os.path.join(carpeta_destino, f"{nombre_limpio}.js")
#     rutas.append(ruta_archivo)

#     if codigo is None:
#         codigo_formateado = "// Código no disponible\n"
#     else:
#         codigo_formateado = formatear_js_basico(str(codigo))

#     with open(ruta_archivo, "w", encoding="utf-8") as f:
#         f.write(codigo_formateado)

#     return rutas

def guardar_scripts_internos_sin_formato(nombre, codigo, carpeta_destino):
    os.makedirs(carpeta_destino, exist_ok=True)

    if not nombre:
        nombre = "sin_nombre"

    nombre_limpio = nombre_archivo_seguro(str(nombre))
    ruta_archivo = os.path.join(carpeta_destino, f"{nombre_limpio}.js")

    if codigo is None:
        codigo = "// Código no disponible\n"

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(codigo)

    return ruta_archivo



# def guardar_scripts_internos(scripts_dict: dict, carpeta_destino: str):
#     """
#     Guarda los scripts internos, exernos, etc; en archivos .js
#     Nombre del archivo = clave del diccionario
#     Contenido = valor del diccionario
#     Se aplica formateo básico antes de guardar
#     """
#     os.makedirs(carpeta_destino, exist_ok=True)

#     rutas = []

#     for nombre, codigo in scripts_dict.items():
#         if not nombre:
#             nombre = "sin_nombre"

#         nombre_limpio = nombre_archivo_seguro(str(nombre))
#         ruta_archivo = os.path.join(carpeta_destino, f"{nombre_limpio}.js")
#         rutas.append(ruta_archivo)

#         if codigo is None:
#             codigo_formateado = "// Código no disponible\n"
#         else:
#             codigo_formateado = formatear_js_basico(str(codigo))

#         with open(ruta_archivo, "w", encoding="utf-8") as f:
#             f.write(codigo_formateado)

#     return rutas

    

def separar_codigo(codigo, tamano=2000):
    return [codigo[i:i+tamano] for i in range(0, len(codigo), tamano)]


# def extraer_scripts_con_playwright(url: str, headless: bool = True, timeout: int = 30000):
#     """
#     Dada una url, devuelve los scripts internos, externos, de network, blob y los eventos inline
#     """

#     resultado = {
#         "internos": {},
#         "externos": {}
#     }

#     network_js = {}   # url -> codigo
#     worker_js = {}    # url -> codigo
#     blob_scripts = {} # blob_url -> placeholder
#     seen_external = set()
#     eventos_inline = {}  # NUEVO

#     with sync_playwright() as p: #- sync_playwright() inicializa Playwright en modo sincrónico.
#         browser = p.chromium.launch(headless=headless)
#         context = browser.new_context()
#         page = context.new_page()

#         # ---- Capturar respuestas de red ----
#         def on_response(response):
#             try:
#                 req = response.request
#                 rurl = response.url
#                 ctype = response.headers.get("content-type", "") if hasattr(response, "headers") else ""
#                 is_js_ct = "javascript" in ctype or rurl.lower().endswith(".js")
#                 rtype = req.resource_type if hasattr(req, "resource_type") else response.request.resource_type

#                 if is_js_ct or rtype in ("script", "xhr", "fetch", "serviceworker"):
#                     try:
#                         body_bytes = response.body()
#                         if body_bytes:
#                             text = body_bytes.decode("utf-8", errors="replace")
#                             network_js[rurl] = text
#                     except Exception:
#                         network_js.setdefault(rurl, None)
#             except Exception:
#                 pass

#         page.on("response", on_response)

#         # ---- Navegar ----
#         page.goto(url, wait_until="networkidle", timeout=timeout)

#         # ---- Extraer scripts del DOM ----
#         scripts = page.evaluate("""
#             () => {
#                 return Array.from(document.scripts).map((s) => {
#                     return {
#                         src: s.src || null,
#                         text: s.textContent || s.innerText || null,
#                         id: s.id || null,
#                         className: s.className || null,
#                         type: s.type || null
#                     };
#                 });
#             }
#         """)

#         # ---- Extraer HTML para eventos inline ----
#         html = page.content()
#         soup = BeautifulSoup(html, "html.parser")
#         eventos = ["onclick", "onmouseover", "onmouseout", "onchange",
#                    "onfocus", "onblur", "onsubmit", "onkeydown", "onkeyup",
#                    "onload", "onerror", "onmouseenter", "onmouseleave"]

#         tag_counter = {}  # para tags sin id

#         for tag in soup.find_all(True):
#             for ev in eventos:
#                 if tag.has_attr(ev):
#                     codigo = tag.get(ev)
#                     html_elem = str(tag)

#                     # elegir nombre clave: id > tag_index
#                     if tag.get("id"):
#                         clave = tag.get("id").strip()
#                     else:
#                         tname = tag.name
#                         tag_counter.setdefault(tname, 0)
#                         tag_counter[tname] += 1
#                         clave = f"{tname}_{tag_counter[tname]}"

#                     eventos_inline[clave] = {
#                         "evento": ev,
#                         "codigo": codigo,
#                         "html": html_elem
#                     }

#         # ---- Cerrar navegador ----
#         try:
#             context.close()
#             browser.close()
#         except Exception:
#             pass

#     # ---- Procesar scripts internos ----
#     contador = 0
#     for s in scripts:
#         contenido = (s.get("text") or "")
#         if not contenido or not contenido.strip():
#             continue

#         if s.get("id"):
#             nombre = s["id"].strip()
#         elif s.get("className"):
#             classes = [c.strip() for c in s["className"].split() if c.strip()]
#             if classes:
#                 nombre = "class_" + "_".join(classes)
#             else:
#                 contador += 1
#                 nombre = f"script_{contador}"
#         elif s.get("type") and s.get("type").strip().lower() != "text/javascript":
#             nombre = "type_" + s.get("type").strip().replace("/", "_")
#         else:
#             contador += 1
#             nombre = f"script_{contador}"

#         original = nombre
#         suffix = 2
#         while nombre in resultado["internos"]:
#             nombre = f"{original}_{suffix}"
#             suffix += 1

#         resultado["internos"][nombre] = contenido

#     # ---- Procesar scripts externos ----
#     for s in scripts:
#         src = s.get("src")
#         if not src:
#             continue

#         if src.startswith(("data:", "javascript:")):
#             if src.startswith("blob:"):
#                 blob_scripts[src] = None
#             continue

#         src_abs = urljoin(url, src)
#         if src_abs in seen_external:
#             continue
#         seen_external.add(src_abs)

#         if src_abs in network_js:
#             resultado["externos"][src_abs] = network_js.get(src_abs)
#         else:
#             try:
#                 headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
#                 r = requests.get(src_abs, timeout=15, headers=headers)
#                 if r.status_code == 200:
#                     resultado["externos"][src_abs] = r.text
#                 else:
#                     resultado["externos"][src_abs] = None
#             except Exception:
#                 resultado["externos"][src_abs] = None

#     # ---- Agregar network ----
#     for net_url, code in network_js.items():
#         if net_url in resultado["externos"]:
#             continue
#         if code is not None:
#             resultado.setdefault("network", {})[net_url] = code
#         else:
#             resultado.setdefault("network", {})[net_url] = None

#     # ---- Agregar workers ----
#     for net_url in list(network_js.keys()):
#         low = net_url.lower()
#         if "serviceworker" in net_url.lower() or low.endswith("/sw.js") or "worker" in net_url.lower():
#             worker_js[net_url] = network_js.get(net_url)
#     if worker_js:
#         resultado["workers"] = worker_js

#     # ---- Agregar blobs ----
#     if blob_scripts:
#         resultado["blobs"] = blob_scripts

#     # ---- Agregar eventos inline ----
#     if eventos_inline:
#         resultado["eventos_inline"] = eventos_inline

#     return resultado




# '''res = extraer_scripts_con_selenium("https://www.iana.org/help/example-domains", True)


# #guardar_scripts_internos(res["externos"], "GuardarDescargas/scripts_extraidos")

# for url, codigo in res["externos"].items():
#     lista = separar_codigo(codigo)
#     for item in lista:
#         print(f"\n\n\nEl codigo, de url {url}, y de largo: {len(item)} es: \n\n\n{item}")


# '''


# """"




# url = "https://www.google.com/"   # Cambia por la URL que quieras analizar

# resultado = extraer_scripts_con_playwright_2(url)

# print("\n=== RESUMEN DE RESULTADOS ===")
# print(f"Scripts internos: {len(resultado.get('internos', {}))}")
# print(f"Scripts externos: {len(resultado.get('externos', {}))}")
# print(f"Network JS (dinámicos): {len(resultado.get('network', {}))}")
# print(f"Service workers: {len(resultado.get('workers', {}))}")
# print(f"Blob scripts: {len(resultado.get('blobs', {}))}")
# print(f"Eventos inline detectados: {len(resultado.get('eventos_inline', []))}")

# """


# """
# Scripts internos: 42
# Scripts externos: 18
# Network JS (dinámicos): 104
# Service workers: 0
# Blob scripts: 0
# Eventos inline detectados: 0

# para la url = "https://www.youtube.com/watch?v=WBZlcr4SE78"

# """




# # json = """
# # content='```json\n[\n  {\n    "id": 2,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "Prototype Pollution",\n    "descripcion": "La función de mezcla profunda \'ce.extend\' itera sobre propiedades de objetos de entrada. Aunque hay una comprobación explícita para `__proto__`, un atacante podría manipular las propiedades del objeto de entrada para inyectar o modificar propiedades en `Object.prototype` o `Array.prototype` (Prototype Pollution), lo que podría afectar el comportamiento de la aplicación en otras partes y llevar a otras vulnerabilidades.",\n    "nivel": "Low",\n    "ubicacion": "función: ce.extend, fragmento: `for ( t in e ) r = e [ t ], \\"_ _proto __\\"!= = t && a!= = r && ( l && r && ( ce. is Plain Object ( r ) || ( i = Array. is Array ( r ) ) )? ( n = a [ t ], o = i &&! Array. is Array ( n )? [ ] : i || ce. is Plain Object ( n )? n : { }, i =! 1, a [ t ] = ce. extend ( l, o, r ) ) : void 0!= = r && ( a [ t ] = r ) ) ;`"\n  },\n  {\n    "id": 5,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "Falso Positivo",\n    "descripcion": "La función \'ce.escapeSelector\' es una medida de seguridad diseñada para escapar selectores CSS, no una vulnerabilidad en sí misma. Su propósito es prevenir la inyección de CSS malicioso cuando se utiliza entrada de usuario en selectores.",\n    "nivel": "None",\n    "ubicacion": "función: ce.escapeSelector, fragmento: `ce. escape Selector = function ( e ) { return ( e + \\"\\" ). replace ( f, p ) } ;`"\n  },\n  {\n    "id": 22,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "Falso Positivo",\n    "descripcion": "Este fragmento de código parece ser parte de un motor de análisis de selectores o una utilidad de procesamiento de cadenas. No hay evidencia directa de una vulnerabilidad de seguridad, ya que solo muestra la lógica de análisis y tokenización de cadenas, no la renderización insegura de HTML o la ejecución de código.",\n    "nivel": "None",\n    "ubicacion": "fragmento: `if (! n ) break } return t? a. length : a? I. error ( e ) : c ( e, s ). slice ( 0 ) } function Q ( e ) { for ( var t = 0, n = e. length, r = \\"\\" ; t < n ; t ++ ) r += e [ t ]. value ; return r }`"\n  },\n  {\n    "id": 43,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "XSS (Cross-Site Scripting)",\n    "descripcion": "La lógica de procesamiento de atributos `data-` incluye una llamada a `JSON.parse(i)` donde `i` es el valor recuperado directamente de un atributo `data-` del DOM (`e.getAttribute(r)`). Si un atacante puede inyectar HTML y controlar el contenido de estos atributos, y los datos resultantes de `JSON.parse` se utilizan posteriormente de forma insegura (ej., insertados en `innerHTML` sin sanitización), podría conducir a una vulnerabilidad de Cross-Site Scripting (XSS).",\n    "nivel": "Medium",\n    "ubicacion": "contexto: procesamiento de data-attributes, fragmento: `try { n = \\"true\\" == = ( i = n ) || \\"false\\"!= = i && ( \\"null\\" == = i? null : i == = + i + \\"\\"? + i : X. test ( i )? JSON. parse ( i ) : i ) } catch ( e ) { }`"\n  },\n  {\n    "id": 72,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "Inyección CSS",\n    "descripcion": "La función `ce.style` permite la asignación directa de valores (`n`) a propiedades CSS de un elemento (`e.style`). Si un atacante puede controlar el valor de `n` (por ejemplo, a través de entrada de usuario no sanitizada), podría inyectar CSS malicioso. Esto puede llevar a la desfiguración de la interfaz, el robo de datos (mediante exfiltración CSS) o, en ciertos navegadores o configuraciones, la ejecución de JavaScript (ej., `url(\'javascript:...\')`).",\n    "nivel": "Medium",\n    "ubicacion": "función: ce.style, fragmento: `style : function ( e, t, n, r ) { if ( e && 3!= = e. node Type && 8!= = e. node Type && e. style ) { var i, o, a, s = F ( t ), u = ze. test ( t ), l = e. style ;`"\n  },\n  {\n    "id": 75,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "Inyección CSS",\n    "descripcion": "Este fragmento de código refuerza la vulnerabilidad de inyección CSS. Contiene la asignación directa `e.style[u] = t` y la llamada a `ce.style(e, t, n)`. Si la entrada `t` o `n` es controlada por un atacante y no está debidamente sanitizada, se pueden inyectar estilos CSS arbitrarios, lo que conlleva los mismos riesgos de inyección CSS mencionados en el fragmento ID 72.",\n    "nivel": "Medium",\n    "ubicacion": "función: ce.fn.extend.css, fragmento: `s && ( r = Y. exec ( t ) ) && \\"p x\\"!= = ( r [ 3 ] || \\"p x\\" ) && ( e. style [ u ] = t, t = ce. css ( e, u ) ), rt ( 0, t, s ) } } } ), ... return void 0!= = n? ce. style ( e, t, n ) : ce. css ( e, t )`"\n  },\n  {\n    "id": 101,\n    "idArchivo": 1,\n    "tipo_vulnerabilidad": "Redirección Abierta",\n    "descripcion": "La asignación de `v.url` (`v.url = ((e || v.url || E t.href) + \\"\\").replace($t, E t.protocol + \\"//\\")`) utiliza la variable `e` como una posible fuente de la URL. Si esta variable `e` puede ser controlada por el usuario (por ejemplo, a través de un parámetro de URL) y no se valida adecuadamente contra una lista blanca de dominios permitidos, un atacante podría manipular la URL para redirigir a los usuarios a sitios maliciosos (phishing o malware).",\n    "nivel": "Medium",\n    "ubicacion": "contexto: configuración de petición AJAX, fragmento: `v. url = ( ( e || v. url || E t. href ) + \\"\\" ). replace ( $ t, E t. protocol + \\"/ /\\" ), v. type = t. method || t. type || v. method || v. type, v. data Types = ( v. dataType || \\"*\\" ). toLower Case ( ). match ( D ) || [ \\"\\" ], null == v. cross Domain )`"\n  }\n]\n```' additional_kwargs={} response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': [], 'grounding_metadata': {}, 'model_provider': 'google_genai'} id='lc_run--c61b9593-8481-4afb-8cde-17e929f5d073-0' usage_metadata={'input_tokens': 4009, 'output_tokens': 11175, 'total_tokens': 15184, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 9453}}
# # """

# # res = formatear_js_basico(json)

# # print(res)