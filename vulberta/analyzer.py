# vulberta/analyzer.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_PATH = "vulberta/models"
CLASES = ["No vulnerable", "Vulnerable"] #Etiquetas para cada clase del modelo

# Cargar modelo y tokenizer una sola vez
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, trust_remote_code=True)
model.eval()

def analizar_texto(texto, chunk_size=512):
    """
    Analiza un texto de código fuente y devuelve una lista de diccionarios con:
    - fragment: número del fragmento analizado
    - label: etiqueta predicha ("No vulnerable" / "Vulnerable")
    - confidence: probabilidad asociada a la predicción
    - code_fragment (opcional): el texto del fragmento vulnerable destokenizado
    """

    resultados = []

    # Tokenizamos el código fuente completo → tensor de IDs numéricos
    tokens = tokenizer(
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
            outputs = model(chunk)
            probs = torch.softmax(outputs.logits, dim=-1).tolist()[0]
            pred_idx = probs.index(max(probs))
            label = CLASES[pred_idx]
            confidence = round(max(probs), 3)

            # Diccionario base con la información del fragmento
            resultado = {
                "fragment": i // chunk_size + 1,
                "label": label,
                "confidence": confidence
            }

            # mostrar su es vulnerable
            if label == "Vulnerable":
                code_fragment = tokenizer.decode(
                    chunk[0],
                    skip_special_tokens=True
                )
                resultado["code_fragment"] = code_fragment
                print("\n Fragmento vulnerable detectado:")
                print(code_fragment)

            resultados.append(resultado)
    
    return resultados