import sys
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from scripts.Fragmento import Fragmento
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.Herramienta import Herramienta

from flask import  jsonify


from scripts.tools import separar_codigo



class Vulberta(Herramienta):
    def __init__(self,nombre, version):
        super().__init__(nombre, version)

        self.__MODEL_PATH = "vulberta/models"
        self.__CLASES = ["No vulnerable", "Vulnerable"] #Etiquetas para cada clase del modelo

        try:
            # Cargar modelo y tokenizer una sola vez
            self.__tokenizer = AutoTokenizer.from_pretrained(self.__MODEL_PATH, trust_remote_code=True)
            self.__model = AutoModelForSequenceClassification.from_pretrained(self.__MODEL_PATH, trust_remote_code=True)
            self.__model.eval()
        except Exception as e:
            raise RuntimeError(f"Error al cargar el modelo/tokenizer: {e}")


    
    #512
    def analizar_texto(self, texto, chunk_size=512):
        resultados = []

        # 🔹 Verificar tipo y contenido del texto
        if not isinstance(texto, str) or not texto.strip():
            return [{
                "error": "Texto vacío o tipo inválido",
                "label": "Error",
                "confidence": 0.0
            }]

        try:
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
                chunk = tokens[i:i + chunk_size].unsqueeze(0)

                with torch.no_grad():
                    outputs = self.__model(chunk)
                    probs = torch.softmax(outputs.logits, dim=-1).tolist()[0]
                    pred_idx = probs.index(max(probs))
                    label = self.__CLASES[pred_idx]
                    confidence = round(max(probs), 3)

                    resultado = {
                        "fragment": i // chunk_size + 1,
                        "label": label,
                        "confidence": confidence
                    }

                    
                    code_fragment = self.__tokenizer.decode(
                        chunk[0],
                        skip_special_tokens=True
                    )
                    resultado["code_fragment"] = code_fragment

                    resultados.append(resultado)

        except Exception as e:
            # 🔹 Captura cualquier error (tokenización, modelo, etc.)
            resultados.append({
                "error": str(e),
                "label": "Error",
                "confidence": 0.0
            })

        return resultados

    

    def analizar_url(self,url):
        codigo, error = self.extraer_codigo(url)
        if error:
            return jsonify({"error": f"No se pudo obtener la página: {error}"}), 500

        resultado = self.analizar_texto(codigo)

        # 🔹 Devolvemos JSON legible, listo para Gemini o para mostrar directamente
        return jsonify({"url": url, "resultado": resultado})
    
    def analizar_sitio(self, sitio):
        archivos = sitio.get_archivos()

        id = 0
        fragmentos = []
        for parte in archivos:
            resultadoAnalisisFragmento = self.analizar_texto(parte)
            for r in resultadoAnalisisFragmento:
                # Si hay error, no intentamos leer code_fragment
                if "error" in r:
                    print(f"[ERROR] Modelo devolvió error: {r['error']}")
                    continue
                label = r["label"]
                confidence = r["confidence"]

                # Recuperamos el fragmento del código de forma segura
                code_fragment = r.get("code_fragment")
                if not code_fragment:
                    print(f"[WARN] No se recibió code_fragment. Resultado: {r}")
                    continue
                #Cambiar este id, ya que se repita: 1.2.3, despues 1,2,3 y asi. Ver si se puede usar el id de la variable  id += 1
                #idFragment = r["fragment"]
                idFragment = id
                fr = Fragmento(idFragment, label, confidence, code_fragment)
                fragmentos.append(fr)

                print(f"Analisis: {idFragment}, con largo: {len(code_fragment)}")
                id += 1

        return fragmentos
    

    