import sys
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.Herramienta import Herramienta

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
#from vulberta.analyzer import analizar_texto


class Vulberta(Herramienta):
    def __init__(self, id, nombre, version, tipo, analisis):
        super().__init__(id, nombre, version, tipo, analisis)

        self.__eventos_inline = [
            "onclick", "onmouseover", "onmouseout", "onchange",
            "onfocus", "onblur", "onsubmit", "onkeydown", "onkeyup"
        ]
        self.__max_scripts = 20
        self.__max_events = 50
        self.__max_chars_script = 2000
        self.__max_chars = 50_000

        self.__MODEL_PATH = "vulberta/models"
        self.__CLASES = ["No vulnerable", "Vulnerable"] #Etiquetas para cada clase del modelo

        try:
            # Cargar modelo y tokenizer una sola vez
            self.__tokenizer = AutoTokenizer.from_pretrained(self.__MODEL_PATH, trust_remote_code=True)
            self.__model = AutoModelForSequenceClassification.from_pretrained(self.__MODEL_PATH, trust_remote_code=True)
            self.__model.eval()
        except Exception as e:
            raise RuntimeError(f"Error al cargar el modelo/tokenizer: {e}")


    def extraer_codigo(self,url):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
        except Exception as e:
            return None, str(e)

        soup = BeautifulSoup(r.text, 'html.parser')

        # 1️⃣ Scripts internos
        scripts = [s.get_text()[:self.__max_chars_script] for s in soup.find_all('script') if s.get_text()]
        scripts = scripts[:self.__max_scripts]

        # 2️⃣ Eventos inline
        eventos = []
        for ev in self.__eventos_inline:
            eventos += [tag[ev] for tag in soup.find_all(attrs={ev: True})]
        eventos = eventos[:self.__max_events]

        # 3️⃣ Combinar scripts y eventos y truncar
        codigo = "\n".join(scripts + eventos)
        if len(codigo) > self.__max_chars:
            codigo = codigo[:self.__max_chars]

        return codigo, None

    def analizar_texto(self, texto, chunk_size=512):
        resultados = []

        # Tokenizamos el código fuente completo → tensor de IDs numéricos
        tokens = self.__tokenizer(
            texto,
            truncation=False,
            add_special_tokens=True,
            return_tensors="pt"
        )["input_ids"][0]

        num_tokens = tokens.shape[0]

        # Analizamos en bloques de 512 tokens
        for i in range(0, num_tokens, chunk_size):
            # Selecciona el fragmento actual y le agrega dimensión batch
            chunk = tokens[i:i + chunk_size].unsqueeze(0)

            # Inferencia sin gradientes (más rápido, menos memoria)
            with torch.no_grad():
                outputs = self.__model(chunk)
                probs = torch.softmax(outputs.logits, dim=-1).tolist()[0]
                pred_idx = probs.index(max(probs))
                label = self.__CLASES[pred_idx]
                confidence = round(max(probs), 3)

                # Diccionario base con la información del fragmento
                resultado = {
                    "fragment": i // chunk_size + 1,
                    "label": label,
                    "confidence": confidence
                }

                # mostrar su es vulnerable
                if label == "Vulnerable":
                    code_fragment = self.__tokenizer.decode(
                        chunk[0],
                        skip_special_tokens=True
                    )
                    resultado["code_fragment"] = code_fragment
                    print("\n Fragmento vulnerable detectado:")
                    print(code_fragment)

                resultados.append(resultado)
        
        return resultados
    
    def analizar_url(self,url):
        codigo, error = self.extraer_codigo(url)
        if error:
            return jsonify({"error": f"No se pudo obtener la página: {error}"}), 500

        resultado = self.analizar_texto(codigo)

        # 🔹 Devolvemos JSON legible, listo para Gemini o para mostrar directamente
        return jsonify({"url": url, "resultado": resultado})


