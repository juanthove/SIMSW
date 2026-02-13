import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROMPT_TEMPLATE = """
Actuas como un analista de seguridad de aplicaciones senior.

Recibiras el siguiente CONJUNTO DE INFORMACION:

1) Fragmentos de codigo que un modelo ML (VulBERTa) clasifico como VULNERABLES.
-> En caso de tratarse de un falso positivo, ignoralo, no lo devuelves en el json.

Tu tarea:
- Analizar TODOS los fragmentos.
- Verificar si existe sanitizacion o mitigacion real.
- Detectar falsos positivos.
- Devolver SOLO vulnerabilidades reales.
- Si un fragmento NO es vulnerable, IGNORARLO.

Devuelve EXCLUSIVAMENTE un JSON valido.
NO agregues texto adicional.
NO uses ```json.

Estructura exacta del JSON:

[
  {
    "titulo": nombre tecnico corto de la vulnerabilidad,
    "descripcion": explicacion tecnica del problema,
    "descripcion_humana": explicacion breve en lenguaje simple y entendible,
    "impacto": consecuencias reales si se explota,
    "recomendacion": como corregir o mitigar la vulnerabilidad,
    "evidencia": descripcion observable del problema (request, endpoint, comportamiento) y nombre del archivo donde se encuentra la vulnerabilidad sin su ruta,
    "severidad": nivel de severidad del 1 al 3 (1=baja, 2=media, 3=alta),
    "codigo": fragmento exacto de codigo vulnerable
  }
]

Si no hay vulnerabilidades reales, devuelve [].
""".strip()



def crear_prompts_lote_vulberta(
    resultados_vulberta: Iterable[dict] | dict,
    llm_char_limit: int = 12_000,
) -> list[str]:
    """
    Crea prompts por lotes desde resultados de VulBERTa y respeta el limite de caracteres por llamada.
    Si un fragmento excede el limite, recorta su codigo para que entre.
    """
    if llm_char_limit < 200:
        raise ValueError("llm_char_limit must be >= 200")

    payload = _armar_payload_vulberta(resultados_vulberta)
    chunks: list[list[dict]] = []
    current: list[dict] = []

    for item in payload:
        fitted = _ajustar_item_a_limite(item, llm_char_limit)
        if fitted is None:
            continue

        trial = current + [fitted]
        trial_prompt = crear_prompt_vulberta(trial)
        if verificar_maximo_caracteres(trial_prompt, llm_char_limit):
            current = trial
            continue

        if current:
            chunks.append(current)
        current = [fitted]

    if current:
        chunks.append(current)

    return [crear_prompt_vulberta(chunk) for chunk in chunks]


def _formatear_fragmentos_prompt(payload: list[dict]) -> str:
    """Formatea cada entrada del payload para incluirla en el prompt final."""
    rows: list[str] = []
    for frag in payload:
        rows.append(
            "\n".join(
                [
                    f"Ruta: {frag.get('Ruta', '')}",
                    f"Archivo: {frag.get('Archivo', '')}",
                    f"Keyword: {frag.get('Keyword', '')}",
                    f"Label: {frag.get('label', '')}",
                    f"Class ID: {frag.get('class_id', '')}",
                    f"Confidence: {frag.get('confidence', '')}",
                    "Codigo:",
                    str(frag.get("Codigo", "") or ""),
                ]
            )
        )

    return "\n\n".join(rows)


def crear_prompt_vulberta(payload: list[dict]) -> str:
    """Construye el prompt completo usando el template base y payload de VulBERTa."""
    prompt = f"{PROMPT_TEMPLATE}\n\n"
    prompt += "=== FRAGMENTOS A ANALIZAR ===\n"
    if payload:
        prompt += _formatear_fragmentos_prompt(payload) + "\n"
    else:
        prompt += "(sin fragmentos)\n"
    return prompt


def _ajustar_item_a_limite(item: dict, llm_char_limit: int) -> dict | None:
    """
    Ajusta un item para que pueda entrar solo en un prompt, truncando `Codigo` si es necesario.
    Devuelve None si ni truncando se puede incluir.
    """
    candidate = dict(item)
    code_fragment = str(candidate.get("Codigo", "") or "")
    single_prompt = crear_prompt_vulberta([candidate])

    if verificar_maximo_caracteres(single_prompt, llm_char_limit):
        return candidate

    marker = "\n...[truncated_for_llm]..."
    low = 0
    high = len(code_fragment)
    best: str | None = None

    while low <= high:
        mid = (low + high) // 2
        candidate["Codigo"] = code_fragment[:mid] + marker
        test_prompt = crear_prompt_vulberta([candidate])
        if verificar_maximo_caracteres(test_prompt, llm_char_limit):
            best = candidate["Codigo"]
            low = mid + 1
        else:
            high = mid - 1

    if best is None:
        return None

    candidate["Codigo"] = best
    return candidate



def verificar_maximo_caracteres(texto: str, limite: int) -> bool:
    """Valida si un texto respeta el limite de caracteres configurado."""
    return len(texto) <= limite


def _normalizar_resultados_vulberta(resultados: Iterable[dict] | dict) -> list[dict]:
    """Normaliza resultados de VulBERTa a una lista de diccionarios."""
    if isinstance(resultados, dict):
        return [resultados]
    return [item for item in resultados if isinstance(item, dict)]


def _serializar_payload(payload: list[dict]) -> str:
    """Serializa un payload en JSON legible para estimar tamano de entrada."""
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _armar_payload_vulberta(resultados_vulberta: Iterable[dict] | dict) -> list[dict]:
    """
    Convierte la salida de `CorrerPrograma.ejecutar()` al formato que alimenta el prompt.
    Toma campos devueltos por VulBERTa: label, class_id, confidence, is_vulnerable, code_fragment.
    """
    items = _normalizar_resultados_vulberta(resultados_vulberta)
    payload: list[dict] = []

    for item in items:
        vulberta_data = item.get("vulberta", {}) if isinstance(item.get("vulberta"), dict) else {}
        file_path = str(item.get("file_name", "") or "")
        file_name = Path(file_path).name if file_path else ""

        payload.append(
            {
                "Ruta": file_path,
                "Archivo": file_name,
                "Keyword": str(item.get("keyword", "") or ""),
                "label": vulberta_data.get("label", ""),
                "class_id": vulberta_data.get("class_id", -1),
                "confidence": vulberta_data.get("confidence", 0.0),
                "is_vulnerable": vulberta_data.get("is_vulnerable", False),
                "Codigo": str(vulberta_data.get("code_fragment", "") or ""),
            }
        )

    return payload