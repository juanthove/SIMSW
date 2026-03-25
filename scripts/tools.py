from bs4 import BeautifulSoup, Comment
import hashlib
import difflib
from pathlib import Path


#Para lo de guardado
import os
import re


from urllib.parse import urlparse
import subprocess
import json
from typing import List, Dict, Tuple
from playwright.sync_api import sync_playwright


def nombre_archivo_seguro(nombre: str) -> str:
    #Normalizar caracteres
    base = re.sub(r'[^a-zA-Z0-9._-]', '_', nombre)

    #Limitar tamaño
    if len(base) > 80:
        base = base[:80]

    #Agregar hash para evitar colisiones
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


def extract_code_from_file(path: str, start: int, end: int) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return "".join(lines[start - 1:end]).strip()
    except Exception:
        return ""


def run_semgrep_analysis(target_dir: str, config: str = "p/owasp-top-ten") -> Tuple[List[Dict], List[Dict]]:
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


    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONUTF8": "1"}
    )

    if result.returncode not in (0, 1):
        raise RuntimeError("Semgrep failed")


    output = json.loads(result.stdout)
    findings = output.get("results", [])

    vulberta_inputs = []

    for f in findings:
        path = f.get("path")
        start = f.get("start", {}).get("line")
        end = f.get("end", {}).get("line")

        extra = f.get("extra", {})

        metadata = extra.get("metadata", {})
        
        code = extract_code_from_file(path, start, end)

        context = extract_code_with_context(
            path,
            start,
            end,
            context_before=5,
            context_after=5
        )

        #JSON completo
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


def extract_code_with_context(path: str, start: int, end: int, context_before: int = 5, context_after: int = 5) -> Dict:
    """
    Extrae código con contexto seguro alrededor de un finding.
    """

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        total_lines = len(lines)

        #Ajustes seguros
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
            "type": tag,  # replace, delete, insert
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

    #Scripts
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

    #Eventos inline (on*)
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

    #Forms
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

    #Iframes
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

    #Comentarios HTML
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

    #Fallback: diff textual real
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
        autojunk=False 
    )

    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            continue

        changes.append({
            "type": tag,  #replace, delete, insert
            "old_start_line": i1 + 1,
            "old_end_line": i2,
            "new_start_line": j1 + 1,
            "new_end_line": j2,
            "old_content": "\n".join(old_lines[i1:i2]).strip(),
            "new_content": "\n".join(new_lines[j1:j2]).strip()
        })

    return changes


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
    domain = parsed.netloc.lower()
    path = parsed.path.strip("/")

    #Caso especial: GitHub Pages
    if domain.endswith("github.io") and path:
        #Ignorar el primer segmento (nombre del repo)
        first_segment = path.split("/")[0]
        return Path(first_segment)

    #Caso normal
    if not path:
        return Path()

    return Path(path)




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
        page.wait_for_timeout(5000) 
        browser.close()

    return resources


def es_pagina_html(url):
    path = url.split("?")[0]

    #Sin extensión es probablemente MVC view
    if "." not in path.split("/")[-1]:
        return True

    return path.endswith(".html")


def relative_path_from_url(resource_url: str, site_base: Path) -> Path:
    parsed = urlparse(resource_url)
    raw_path = parsed.path

    #Si termina en "/" es carpeta se le llama index.html
    if raw_path.endswith("/"):
        path = Path(raw_path.lstrip("/")) / "index.html"

    else:
        path = Path(raw_path.lstrip("/"))

        #Si no tiene extensión es ruta tipo MVC
        if "." not in path.name:
            path = path.with_suffix(".html")

    #Hacer relativo al sitio base
    try:
        path = path.relative_to(site_base)
    except ValueError:
        pass

    #Sanitizar nombre
    parts = [
        re.sub(r"[^a-zA-Z0-9._-]", "", p)
        for p in path.parts
    ]

    return Path(*parts)




#Aca arranca la mierda

def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()



def detectar_parecidos(old_map, new_map):
    matches = []
    usados = set()

    for old_rel, old_info in old_map.items():

        old_name = Path(old_rel).name

        for new_rel, new_info in new_map.items():

            if new_rel in usados:
                continue

            new_name = Path(new_rel).name

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
            "hash": hash_file(file)
        }

    return index

