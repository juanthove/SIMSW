#from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin
import hashlib
from pathlib import Path
import difflib



#from pprint import pprint
import requests

#Para lo de guardado
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
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(2000)   

                datos, soup = extraer_scripts_con_playwright2(page, url)
                print(f"[DEBUG] Scripts internos: {list(datos['internos'].keys())}")
                print(f"[DEBUG] Scripts externos: {list(datos['externos'].keys())}")
                print(f"[DEBUG] Eventos inline: {list(datos['eventos_inline'].keys())}")
                print(f"[DEBUG] Workers: {list(datos['workers'].keys())}")
                print(f"[DEBUG] Blobs: {list(datos['blobs'].keys())}")


                # 🔹 Éxito real → dict con datos
                if datos and isinstance(datos, dict):
                    resultados[url] = datos
                else:
                    print(f"[!] Datos vacíos para {url}")
                    resultados[url] = None

            except Exception as e:
                print(f"[!] Error en {url}: {e}")
                resultados[url] = None  # 🔥 CLAVE

            finally:
                page.close()

        browser.close()

    return resultados



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



    

def separar_codigo(codigo, tamano=2000):
    return [codigo[i:i+tamano] for i in range(0, len(codigo), tamano)]


import os
import subprocess
import json
from typing import List, Dict, Tuple


def extract_code_from_file(path: str, start: int, end: int) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return "".join(lines[start - 1:end]).strip()
    except Exception:
        return ""


def run_semgrep_analysis(
    target_dir: str,
    config: str = "p/owasp-top-ten"
) -> Tuple[List[Dict], List[Dict]]:
    """
    Ejecuta Semgrep sobre un directorio y devuelve:
    1) JSON completo de findings
    2) Lista optimizada para VulBERTa (codigo + path + metadata)
    """


    cmd = [
        "semgrep",

        "--config", "p/r2c-security-audit",
        "--config", "p/secrets",
        "--config", "p/supply-chain",

        "--no-git-ignore",

        "--timeout", "0",
        "--json",
        "--metrics=off",

        target_dir
    ]


#     cmd = [
#     "semgrep",

#     "--config", "p/javascript",
#     "--config", "p/xss",

#     "--include", "*.js",

#     "--no-git-ignore",
#     "--json",

#     target_dir
# ]


    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONUTF8": "1"}
    )

    if result.returncode not in (0, 1):
        print("=== SEMGREP ERROR ===")
        print("Return code:", result.returncode)
        print("STDOUT:")
        print(result.stdout[:2000])
        print("STDERR:")
        print(result.stderr[:2000])
        raise RuntimeError("Semgrep failed")


    output = json.loads(result.stdout)
    findings = output.get("results", [])

    vulberta_inputs = []

    for f in findings:
        path = f.get("path")
        start = f.get("start", {}).get("line")
        end = f.get("end", {}).get("line")

        extra = f.get("extra", {})
        snippet = extra.get("lines", "").strip()

        metadata = extra.get("metadata", {})
        
        code = extract_code_from_file(path, start, end)

        context = extract_code_with_context(
            path,
            start,
            end,
            context_before=5,
            context_after=5
        )

        # JSON completo
        vulberta_inputs.append({
            "path": path,
            "start_line": start,
            "end_line": end,
            "context_start": context["context_start"],
            "context_end": context["context_end"],
            "check_id": f.get("check_id"),
            "owasp": metadata.get("owasp"),
            "cwe": metadata.get("cwe"),
            "code_context": context["code"],
            "code": code
        })

    return vulberta_inputs


def extract_code_with_context(
    path: str,
    start: int,
    end: int,
    context_before: int = 5,
    context_after: int = 5
) -> Dict:
    """
    Extrae código con contexto seguro alrededor de un finding.
    """

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        total_lines = len(lines)

        # Ajustes seguros
        safe_start = max(1, start - context_before)
        safe_end = min(total_lines, end + context_after)

        code = "".join(lines[safe_start - 1:safe_end]).rstrip()

        return {
            "context_start": safe_start,
            "context_end": safe_end,
            "original_start": start,
            "original_end": end,
            "code": code
        }

    except Exception:
        return {
            "context_start": None,
            "context_end": None,
            "original_start": start,
            "original_end": end,
            "code": ""
        }
    





#Comienzo lo de requerimiento 1

#Compara archivos js
def compare_js_files(file_old: str, file_new: str):
    """
    Compara dos archivos JS y retorna:
      - diff_text (formato git)
      - cambios estructurados (JSON friendly)
    """

    old_lines = Path(file_old).read_text(encoding="utf-8").splitlines()
    new_lines = Path(file_new).read_text(encoding="utf-8").splitlines()

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            continue

        changes.append({
            "type": tag,  # replace | delete | insert
            "old_start_line": i1 + 1,
            "old_end_line": i2,
            "new_start_line": j1 + 1,
            "new_end_line": j2,
            "old_content": "\n".join(old_lines[i1:i2]),
            "new_content": "\n".join(new_lines[j1:j2])
        })

    return changes



#Compara archivos html
def find_line_range(text: str, fragment: str):
    """
    Devuelve (start_line, end_line) aproximado de un fragmento dentro de text.
    """
    if not fragment:
        return None, None

    idx = text.find(fragment)
    if idx == -1:
        return None, None

    start_line = text[:idx].count("\n") + 1
    end_line = start_line + fragment.count("\n")
    return start_line, end_line


def compare_html_files(file_old: str, file_new: str):
    """
    Compara HTML enfocado en seguridad.
    Devuelve cambios usando el MISMO schema que compare_text_files.
    """

    old_html = Path(file_old).read_text(encoding="utf-8", errors="ignore")
    new_html = Path(file_new).read_text(encoding="utf-8", errors="ignore")

    soup_old = BeautifulSoup(old_html, "html.parser")
    soup_new = BeautifulSoup(new_html, "html.parser")

    cambios = []

    # ===============================
    # 1️⃣ Scripts
    # ===============================
    old_scripts = {str(s).strip() for s in soup_old.find_all("script")}
    new_scripts = {str(s).strip() for s in soup_new.find_all("script")}

    for s in new_scripts - old_scripts:
        start, end = find_line_range(new_html, s)
        cambios.append({
            "type": "insert",
            "category": "html_script",
            "old_start_line": None,
            "old_end_line": None,
            "new_start_line": start,
            "new_end_line": end,
            "old_content": "",
            "new_content": s
        })

    for s in old_scripts - new_scripts:
        start, end = find_line_range(old_html, s)
        cambios.append({
            "type": "delete",
            "category": "html_script",
            "old_start_line": start,
            "old_end_line": end,
            "new_start_line": None,
            "new_end_line": None,
            "old_content": s,
            "new_content": ""
        })

    # ===============================
    # 2️⃣ Eventos inline (on*)
    # ===============================
    def extract_events(soup):
        eventos = set()
        for tag in soup.find_all(True):
            for attr, value in tag.attrs.items():
                if attr.lower().startswith("on"):
                    eventos.add(f"<{tag.name} {attr}=\"{value}\">")
        return eventos

    old_events = extract_events(soup_old)
    new_events = extract_events(soup_new)

    for e in new_events - old_events:
        start, end = find_line_range(new_html, e)
        cambios.append({
            "type": "insert",
            "category": "html_inline_event",
            "old_start_line": None,
            "old_end_line": None,
            "new_start_line": start,
            "new_end_line": end,
            "old_content": "",
            "new_content": e
        })

    # ===============================
    # 3️⃣ Forms
    # ===============================
    old_forms = {str(f).strip() for f in soup_old.find_all("form")}
    new_forms = {str(f).strip() for f in soup_new.find_all("form")}

    for f in new_forms - old_forms:
        start, end = find_line_range(new_html, f)
        cambios.append({
            "type": "insert",
            "category": "html_form",
            "old_start_line": None,
            "old_end_line": None,
            "new_start_line": start,
            "new_end_line": end,
            "old_content": "",
            "new_content": f
        })

    # ===============================
    # 4️⃣ Iframes
    # ===============================
    old_iframes = {str(i).strip() for i in soup_old.find_all("iframe")}
    new_iframes = {str(i).strip() for i in soup_new.find_all("iframe")}

    for i in new_iframes - old_iframes:
        start, end = find_line_range(new_html, i)
        cambios.append({
            "type": "insert",
            "category": "html_iframe",
            "old_start_line": None,
            "old_end_line": None,
            "new_start_line": start,
            "new_end_line": end,
            "old_content": "",
            "new_content": i
        })

    # ===============================
    # 5️⃣ Comentarios HTML
    # ===============================
    def extract_comments(soup):
        return {
            str(c).strip()
            for c in soup.find_all(string=lambda t: isinstance(t, Comment))
        }

    old_comments = extract_comments(soup_old)
    new_comments = extract_comments(soup_new)

    for c in new_comments - old_comments:
        start, end = find_line_range(new_html, c)
        cambios.append({
            "type": "insert",
            "category": "html_comment",
            "old_start_line": None,
            "old_end_line": None,
            "new_start_line": start,
            "new_end_line": end,
            "old_content": "",
            "new_content": c
        })

    # ===============================
    # 6️⃣ Fallback: diff textual real
    # ===============================
    if not cambios:
        matcher = difflib.SequenceMatcher(
            None,
            old_html.splitlines(),
            new_html.splitlines(),
            autojunk=False
        )

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            cambios.append({
                "type": tag,
                "category": "text",
                "old_start_line": i1 + 1,
                "old_end_line": i2,
                "new_start_line": j1 + 1,
                "new_end_line": j2,
                "old_content": "\n".join(old_html.splitlines()[i1:i2]).strip(),
                "new_content": "\n".join(new_html.splitlines()[j1:j2]).strip()
            })

    return cambios


#Comparar archivos de texto
def compare_text_files(file_old: str, file_new: str):
    """
    Compara dos archivos de texto (JS, HTML, etc.)
    y devuelve diferencias estructuradas.

    Retorna:
    [
        {
            type: replace | delete | insert,
            old_start_line,
            old_end_line,
            new_start_line,
            new_end_line,
            old_content,
            new_content
        }
    ]
    """

    old_lines = Path(file_old).read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()

    new_lines = Path(file_new).read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()

    matcher = difflib.SequenceMatcher(
        None,
        old_lines,
        new_lines,
        autojunk=False  # importante para archivos grandes
    )

    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            continue

        changes.append({
            "type": tag,  # replace | delete | insert
            "old_start_line": i1 + 1,
            "old_end_line": i2,
            "new_start_line": j1 + 1,
            "new_end_line": j2,
            "old_content": "\n".join(old_lines[i1:i2]).strip(),
            "new_content": "\n".join(new_lines[j1:j2]).strip()
        })

    return changes


#Aca para traer archivs desde url

# def fetch_site_resources(url: str, timeout: int = 15000) -> dict:
#     """
#     Abre la URL con un navegador headless y captura
#     todos los recursos reales cargados (html, js, css).

#     Retorna:
#         {
#             url_recurso: contenido_texto
#         }
#     """
#     resources = {}

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()

#         def handle_response(response):
#             try:
#                 rtype = response.request.resource_type

#                 # solo lo que te interesa para integridad
#                 if rtype in ["document", "script", "stylesheet"]:
#                     body = response.text()
#                     if body:
#                         resources[response.url] = body

#             except Exception:
#                 pass

#         page.on("response", handle_response)

#         page.goto(url, wait_until="networkidle", timeout=timeout)

#         browser.close()

#     return resources

#Estas dos para guardarlas en la carpeta, que si no esta creada, se crea

# def relative_path_from_url(resource_url: str, site_base: Path) -> Path:
#     parsed = urlparse(resource_url)
#     path = Path(parsed.path.lstrip("/"))

#     # 🚫 si no tiene extensión, NO se guarda
#     if "." not in Path(path).name:
#         return

#     # quitar prefijo del sitio (ej: proyecto_DW_grupo3)
#     try:
#         path = path.relative_to(site_base)
#     except ValueError:
#         pass  # el recurso no estaba bajo el prefijo

#     if not path.name:
#         path = path / "index.html"

#     # sanitizar
#     parts = [
#         re.sub(r"[^a-zA-Z0-9._-]", "", p)
#         for p in path.parts
#     ]

#     return Path(*parts)



def save_resources_to_folder(resources: dict, base_folder: Path, site_url: str):
    """
    Guarda los recursos en:
    ./folder_name/

    Crea la carpeta si no existe.
    """
    site_base = get_site_base_path(site_url)

    for url, content in resources.items():
        rel_path = relative_path_from_url(url, site_base)

        #Si no tiene path se ignora
        if not rel_path:
            continue


        file_path = base_folder / rel_path

        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)


def get_site_base_path(url: str) -> Path:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        return Path()  # raíz

    return Path(path)


#Aca para traer archivs desde url
# def fetch_site_resources(url: str, timeout: int = 15000) -> dict:
#     resources = {}

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()

#         def handle_response(response):
#             try:
#                 rtype = response.request.resource_type

#                 if rtype in ["script", "stylesheet"]:
#                     body = response.text()
#                     if body:
#                         resources[response.url] = body

#             except Exception:
#                 pass

#         page.on("response", handle_response)

#         page.goto(url, wait_until="networkidle", timeout=timeout)

#         # ✅ guardar con la URL REAL
#         resources[url] = page.content()

#         browser.close()

#     return resources



def fetch_site_resources(url: str, timeout: int = 15000):
    resources = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_response(response):
            try:
                headers = response.headers
                ct = headers.get("content-type", "")

                if not any(x in ct for x in [
                    "text/html",
                    "javascript",
                    "text/css"
                ]):
                    return

                body = response.text()
                if body:
                    resources[response.url] = body

            except:
                pass

        page.on("response", handle_response)

        page.goto(url, wait_until="networkidle", timeout=timeout)
        browser.close()

    return resources

def es_pagina_html(url):
    path = url.split("?")[0]

    # sin extensión = probablemente MVC view
    if "." not in path.split("/")[-1]:
        return True

    return path.endswith(".html")

#ESte es el que venia usando
# def fetch_site_resources(url: str, timeout: int = 15000) -> dict:
#     """
#     Abre la URL con un navegador headless y captura
#     todos los recursos reales cargados (html, js, css).

#     Retorna:
#         {
#             url_recurso: contenido_texto
#         }
#     """
#     resources = {}

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()

#         def handle_response(response):
#             try:
#                 rtype = response.request.resource_type

#                 # solo lo que te interesa para integridad
#                 if rtype in ["document", "script", "stylesheet"]:
#                     body = response.text()
#                     if body:
#                         resources[response.url] = body

#             except Exception:
#                 pass

#         page.on("response", handle_response)

#         page.goto(url, wait_until="networkidle", timeout=timeout)

#         browser.close()

#     return resources

#Estas dos para guardarlas en la carpeta, que si no esta creada, se crea

# def relative_path_from_url(resource_url: str, site_base: Path) -> Path:
#     parsed = urlparse(resource_url)

#     path = Path(parsed.path.lstrip("/"))

#     # 🌱 raíz
#     if not path or path == Path(""):
#         path = Path("index.html")

#     # 🌐 vista MVC/SPA
#     elif "." not in path.name:
#         path = path / "index.html"   # 👈 MUCHO MEJOR QUE .with_suffix

#     try:
#         path = path.relative_to(site_base)
#     except ValueError:
#         pass

#     parts = [
#         re.sub(r"[^a-zA-Z0-9._-]", "", p).lower()
#         for p in path.parts
#     ]

#     return Path(*parts)

#probar esta sino
def relative_path_from_url(resource_url: str, site_base: Path) -> Path:
    parsed = urlparse(resource_url)
    path = Path(parsed.path.lstrip("/"))

    # raíz del sitio
    if not path or path == Path(""):
        path = Path("Index.html")

    # 👉 si NO tiene extensión => es vista MVC/SPA
    elif "." not in path.name:
        path = path.with_suffix(".html")

    try:
        path = path.relative_to(site_base)
    except ValueError:
        pass

    parts = [
        re.sub(r"[^a-zA-Z0-9._-]", "", p)
        for p in path.parts
    ]

    return Path(*parts)


#Viejo


# def relative_path_from_url(resource_url: str, site_base: Path) -> Path:
#     parsed = urlparse(resource_url)
#     path = Path(parsed.path.lstrip("/"))

#     # 🚫 si no tiene extensión, NO se guarda
#     if "." not in Path(path).name:
#         return

#     # quitar prefijo del sitio (ej: proyecto_DW_grupo3)
#     try:
#         path = path.relative_to(site_base)
#     except ValueError:
#         pass  # el recurso no estaba bajo el prefijo

#     if not path.name:
#         path = path / "index.html"

#     # sanitizar
#     parts = [
#         re.sub(r"[^a-zA-Z0-9._-]", "", p)
#         for p in path.parts
#     ]

#     return Path(*parts)





#Aca arranca la mierda

import hashlib
from collections import defaultdict

import difflib

def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()



#Sugerencia para evitar que matcheen erroneamente

# def detectar_parecidos(old_map, new_map, threshold=0.7):
#     matches = []
#     usados = set()

#     for old_rel, old_info in old_map.items():

#         mejor_score = 0
#         mejor_match = None

#         for new_rel, new_info in new_map.items():

#             if new_rel in usados:
#                 continue

#             old_name = old_rel.split("/")[-1]
#             new_name = new_rel.split("/")[-1]

#             score_name = similar(old_name, new_name)
#             score_path = similar(old_rel, new_rel)

#             score = score_name * 0.7 + score_path * 0.3

#             if score > mejor_score:
#                 mejor_score = score
#                 mejor_match = new_rel

#         if mejor_score >= threshold:
#             usados.add(mejor_match)

#             matches.append({
#                 "old": old_rel,
#                 "new": mejor_match,
#                 "score": mejor_score,
#                 "hash_equal": old_map[old_rel]["hash"] == new_map[mejor_match]["hash"]
#             })

#     return matches


def detectar_parecidos(old_map, new_map):
    matches = []
    usados = set()

    for old_rel, old_info in old_map.items():

        old_name = Path(old_rel).name

        for new_rel, new_info in new_map.items():

            if new_rel in usados:
                continue

            new_name = Path(new_rel).name

            # 🔥 MATCH ESTRICTO
            if old_name != new_name:
                continue

            usados.add(new_rel)

            matches.append({
                "old": old_rel,
                "new": new_rel,
                "score": 1.0,
                "hash_equal": old_info["hash"] == new_info["hash"]
            })

            break

    return matches


def hash_file(path, chunk_size=8192):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)

    return h.hexdigest()

def indexar_carpeta(base_dir, extensiones):
    base_dir = Path(base_dir)

    index = {}

    for file in base_dir.rglob("*"):
        if not file.is_file():
            continue

        if file.suffix.lower() not in extensiones:
            continue

        rel = file.relative_to(base_dir).as_posix()

        index[rel] = {
            "path": file,
            "hash": hash_file(file)   # 🔥 clave
        }

    return index

