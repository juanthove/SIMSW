from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin


from pprint import pprint
import requests


from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import requests

#PAra lo de guardado
import os
import re

def formatear_js_basico(codigo: str) -> str:
    """
    Formatea código JS de manera básica:
    - Agrega saltos de línea tras { } ;
    - Indenta bloques
    """
    # Agregar saltos de línea básicos
    codigo = codigo.replace("{", "{\n")
    codigo = codigo.replace("}", "\n}\n")
    codigo = codigo.replace(";", ";\n")

    # Quitar múltiples líneas vacías
    lineas = [line.rstrip() for line in codigo.split("\n")]
    codigo = "\n".join([line for line in lineas if line.strip() != ""])

    # Indentar según llaves
    indentado = []
    nivel = 0
    for line in codigo.split("\n"):
        line_strip = line.strip()

        if line_strip.startswith("}"):
            nivel = max(0, nivel - 1)

        indentado.append("    " * nivel + line_strip)

        if line_strip.endswith("{"):
            nivel += 1

    return "\n".join(indentado)


def guardar_scripts_internos(scripts_dict: dict, carpeta_destino: str):
    """
    Guarda los scripts internos en archivos .js
    Nombre del archivo = clave del diccionario
    Contenido = valor del diccionario
    Se aplica formateo básico antes de guardar
    """

    os.makedirs(carpeta_destino, exist_ok=True)

    for nombre, codigo in scripts_dict.items():
        # Limpiar nombre del archivo
        nombre_limpio = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', nombre)

        ruta_archivo = os.path.join(carpeta_destino, f"{nombre_limpio}.js")

        # Formatear el código antes de guardar
        codigo_formateado = formatear_js_basico(codigo)

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(codigo_formateado)

    return True

def separar_codigo(codigo, tamano=2000):
    return [codigo[i:i+tamano] for i in range(0, len(codigo), tamano)]


def extraer_scripts_con_playwright(url: str, headless: bool = True, timeout: int = 30000):
    """
    + Ahora también captura eventos inline: onclick, onmouseover, etc.
    El resultado agrega la key: 'eventos_inline'
    """

    resultado = {
        "internos": {},
        "externos": {}
    }

    network_js = {}   # url -> codigo
    worker_js = {}    # url -> codigo
    blob_scripts = {} # blob_url -> placeholder
    seen_external = set()
    eventos_inline = {}  # NUEVO

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # ---- Capturar respuestas de red ----
        def on_response(response):
            try:
                req = response.request
                rurl = response.url
                ctype = response.headers.get("content-type", "") if hasattr(response, "headers") else ""
                is_js_ct = "javascript" in ctype or rurl.lower().endswith(".js")
                rtype = req.resource_type if hasattr(req, "resource_type") else response.request.resource_type

                if is_js_ct or rtype in ("script", "xhr", "fetch", "serviceworker"):
                    try:
                        body_bytes = response.body()
                        if body_bytes:
                            text = body_bytes.decode("utf-8", errors="replace")
                            network_js[rurl] = text
                    except Exception:
                        network_js.setdefault(rurl, None)
            except Exception:
                pass

        page.on("response", on_response)

        # ---- Navegar ----
        page.goto(url, wait_until="networkidle", timeout=timeout)

        # ---- Extraer scripts del DOM ----
        scripts = page.evaluate("""
            () => {
                return Array.from(document.scripts).map((s) => {
                    return {
                        src: s.src || null,
                        text: s.textContent || s.innerText || null,
                        id: s.id || null,
                        className: s.className || null,
                        type: s.type || null
                    };
                });
            }
        """)

        # ---- Extraer HTML para eventos inline ----
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        eventos = ["onclick", "onmouseover", "onmouseout", "onchange",
                   "onfocus", "onblur", "onsubmit", "onkeydown", "onkeyup",
                   "onload", "onerror", "onmouseenter", "onmouseleave"]

        tag_counter = {}  # para tags sin id

        for tag in soup.find_all(True):
            for ev in eventos:
                if tag.has_attr(ev):
                    codigo = tag.get(ev)
                    html_elem = str(tag)

                    # elegir nombre clave: id > tag_index
                    if tag.get("id"):
                        clave = tag.get("id").strip()
                    else:
                        tname = tag.name
                        tag_counter.setdefault(tname, 0)
                        tag_counter[tname] += 1
                        clave = f"{tname}_{tag_counter[tname]}"

                    eventos_inline[clave] = {
                        "evento": ev,
                        "codigo": codigo,
                        "html": html_elem
                    }

        # ---- Cerrar navegador ----
        try:
            context.close()
            browser.close()
        except Exception:
            pass

    # ---- Procesar scripts internos ----
    contador = 0
    for s in scripts:
        contenido = (s.get("text") or "")
        if not contenido or not contenido.strip():
            continue

        if s.get("id"):
            nombre = s["id"].strip()
        elif s.get("className"):
            classes = [c.strip() for c in s["className"].split() if c.strip()]
            if classes:
                nombre = "class_" + "_".join(classes)
            else:
                contador += 1
                nombre = f"script_{contador}"
        elif s.get("type") and s.get("type").strip().lower() != "text/javascript":
            nombre = "type_" + s.get("type").strip().replace("/", "_")
        else:
            contador += 1
            nombre = f"script_{contador}"

        original = nombre
        suffix = 2
        while nombre in resultado["internos"]:
            nombre = f"{original}_{suffix}"
            suffix += 1

        resultado["internos"][nombre] = contenido

    # ---- Procesar scripts externos ----
    for s in scripts:
        src = s.get("src")
        if not src:
            continue

        if src.startswith(("data:", "javascript:")):
            if src.startswith("blob:"):
                blob_scripts[src] = None
            continue

        src_abs = urljoin(url, src)
        if src_abs in seen_external:
            continue
        seen_external.add(src_abs)

        if src_abs in network_js:
            resultado["externos"][src_abs] = network_js.get(src_abs)
        else:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
                r = requests.get(src_abs, timeout=15, headers=headers)
                if r.status_code == 200:
                    resultado["externos"][src_abs] = r.text
                else:
                    resultado["externos"][src_abs] = None
            except Exception:
                resultado["externos"][src_abs] = None

    # ---- Agregar network ----
    for net_url, code in network_js.items():
        if net_url in resultado["externos"]:
            continue
        if code is not None:
            resultado.setdefault("network", {})[net_url] = code
        else:
            resultado.setdefault("network", {})[net_url] = None

    # ---- Agregar workers ----
    for net_url in list(network_js.keys()):
        low = net_url.lower()
        if "serviceworker" in net_url.lower() or low.endswith("/sw.js") or "worker" in net_url.lower():
            worker_js[net_url] = network_js.get(net_url)
    if worker_js:
        resultado["workers"] = worker_js

    # ---- Agregar blobs ----
    if blob_scripts:
        resultado["blobs"] = blob_scripts

    # ---- Agregar eventos inline ----
    if eventos_inline:
        resultado["eventos_inline"] = eventos_inline

    return resultado

'''res = extraer_scripts_con_selenium("https://www.iana.org/help/example-domains", True)


#guardar_scripts_internos(res["externos"], "GuardarDescargas/scripts_extraidos")

for url, codigo in res["externos"].items():
    lista = separar_codigo(codigo)
    for item in lista:
        print(f"\n\n\nEl codigo, de url {url}, y de largo: {len(item)} es: \n\n\n{item}")


'''


""""




url = "https://www.google.com/"   # Cambia por la URL que quieras analizar

resultado = extraer_scripts_con_playwright_2(url)

print("\n=== RESUMEN DE RESULTADOS ===")
print(f"Scripts internos: {len(resultado.get('internos', {}))}")
print(f"Scripts externos: {len(resultado.get('externos', {}))}")
print(f"Network JS (dinámicos): {len(resultado.get('network', {}))}")
print(f"Service workers: {len(resultado.get('workers', {}))}")
print(f"Blob scripts: {len(resultado.get('blobs', {}))}")
print(f"Eventos inline detectados: {len(resultado.get('eventos_inline', []))}")

"""


"""
Scripts internos: 42
Scripts externos: 18
Network JS (dinámicos): 104
Service workers: 0
Blob scripts: 0
Eventos inline detectados: 0

para la url = "https://www.youtube.com/watch?v=WBZlcr4SE78"

"""