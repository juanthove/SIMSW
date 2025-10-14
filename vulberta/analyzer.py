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
    Devuelve lista de diccionarios con:
    - fragment
    - label
    - confidence
    """
    resultados = []
    tokens = tokenizer(texto, truncation=False, add_special_tokens=True, return_tensors="pt")["input_ids"][0]
    num_tokens = tokens.shape[0]

    for i in range(0, num_tokens, chunk_size):
        chunk = tokens[i:i+chunk_size].unsqueeze(0)
        with torch.no_grad():
            outputs = model(chunk)
            probs = torch.softmax(outputs.logits, dim=-1).tolist()[0]
            pred_idx = probs.index(max(probs))
            resultados.append({
                "fragment": i // chunk_size + 1,
                "label": CLASES[pred_idx],
                "confidence": round(max(probs), 3)
            })
    return resultados