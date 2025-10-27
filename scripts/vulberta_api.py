import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
from vulberta.analyzer import analizar_texto




# Eventos inline que queremos capturar
EVENTOS_INLINE = [
    "onclick", "onmouseover", "onmouseout", "onchange",
    "onfocus", "onblur", "onsubmit", "onkeydown", "onkeyup"
]

# Límites para optimización
MAX_SCRIPTS = 20      # máximo de scripts a analizar
MAX_EVENTS = 50       # máximo de eventos inline a analizar
MAX_CHARS_SCRIPT = 2000  # máximo de caracteres por script
MAX_CHARS = 50_000    # máximo total de texto a pasar al modelo

def extraer_codigo(url):
    """
    Descarga la página desde la URL y extrae scripts internos
    y eventos inline relevantes, optimizando la cantidad de datos
    que se pasan al modelo VulBERTa.
    
    Retorna:
        codigo (str): texto combinado para analizar
        error (str|None): mensaje de error si falla la descarga
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return None, str(e)

    soup = BeautifulSoup(r.text, 'html.parser')

    # 1️⃣ Scripts internos
    scripts = [s.get_text()[:MAX_CHARS_SCRIPT] for s in soup.find_all('script') if s.get_text()]
    scripts = scripts[:MAX_SCRIPTS]

    # 2️⃣ Eventos inline
    eventos = []
    for ev in EVENTOS_INLINE:
        eventos += [tag[ev] for tag in soup.find_all(attrs={ev: True})]
    eventos = eventos[:MAX_EVENTS]

    # 3️⃣ Combinar scripts y eventos y truncar
    codigo = "\n".join(scripts + eventos)
    if len(codigo) > MAX_CHARS:
        codigo = codigo[:MAX_CHARS]

    return codigo, None

def analizar_url(url):
    codigo, error = extraer_codigo(url)
    if error:
        return jsonify({"error": f"No se pudo obtener la página: {error}"}), 500

    resultado = analizar_texto(codigo)

    # 🔹 Devolvemos JSON legible, listo para Gemini o para mostrar directamente
    return jsonify({"url": url, "resultado": resultado})
