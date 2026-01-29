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

        # Seguridad general
        "--config", "p/security-audit",
        "--config", "p/secrets",

        # Lenguajes
        "--config", "p/python",
        "--config", "p/javascript",
        "--config", "p/java",
        "--config", "p/csharp",

        # Frameworks
        "--config", "p/django",
        "--config", "p/flask",
        # "--config", "p/express",
        "--config", "p/react",
        # "--config", "p/spring",
        # "--config", "p/rails",

        # Infra / DevOps
        "--config", "p/docker",
        "--config", "p/kubernetes",
        "--config", "p/terraform",
        "--config", "p/github-actions",

        # Target
        target_dir,

        # Output
        "--json",
        "--metrics=off",
    ]


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