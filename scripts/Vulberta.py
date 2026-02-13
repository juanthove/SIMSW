from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scripts.Herramienta import *


@dataclass
class ResultadoChunk:
    fragment: int
    class_id: int
    label: str
    confidence: float
    is_vulnerable: bool
    code_fragment: str
    scores: Dict[str, float]


class Vulberta(Herramienta):
    
    def __init__(
        self,
        nombre: str = "Vulberta", 
        version: str = "1",
        model_path: str = "vulberta/models",
        chunk_size: int = 512,
        vulnerable_class_id: int = 1,
        trust_remote_code: bool = True,
        device: Optional[str] = None,
    ) -> None:
        super().__init__(nombre, version)
        self.model_path = model_path
        self.chunk_size = chunk_size
        self.vulnerable_class_id = vulnerable_class_id
        
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._configurar_libclang()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=trust_remote_code,
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_path,
            trust_remote_code=trust_remote_code,
        )
        self.model.to(self.device)
        self.model.eval()

        self.class_labels = self._resolver_labels()

    def _configurar_libclang(self) -> None:
        """
        Configura explicitamente la ruta de libclang.dll. Esto es necesario para correr en Windows.
        """
        try:
            import clang
            from clang.cindex import Config
        except Exception:
            return

        """
        Cambio minimo y seguro:
        Si libclang ya fue cargado en una peticion anterior, no volver a ejecutar
        Config.set_library_file(...), porque falla en la segunda ejecucion.
        """
        if Config.loaded:
            return

        dll_path = Path(clang.__file__).resolve().parent / "native" / "libclang.dll"
        if dll_path.exists():
            Config.set_library_file(str(dll_path))

    def _resolver_labels(self) -> Dict[int, str]:
        config = self.model.config
        id2label = getattr(config, "id2label", {}) or {}
        num_labels = int(getattr(config, "num_labels", max(2, len(id2label) or 2)))

        labels: Dict[int, str] = {}
        for idx in range(num_labels):
            raw_label = str(id2label.get(idx, f"LABEL_{idx}"))
            lower = raw_label.lower()

            if "vulner" in lower and "no vulnerable" not in lower and "non" not in lower:
                labels[idx] = "Vulnerable"
                continue

            if (
                "benign" in lower
                or "safe" in lower
                or "no vulnerable" in lower
                or "non-vulner" in lower
                or "non vulnerable" in lower
            ):
                labels[idx] = "No vulnerable"
                continue

            labels[idx] = "Vulnerable" if idx == self.vulnerable_class_id else "No vulnerable"

        return labels

    def _validar_texto(self, texto: str) -> None:
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("El texto a analizar debe ser un string no vacio.")

    def _tokenizar(self, texto: str) -> torch.Tensor:
        tokens = self.tokenizer(
            texto,
            truncation=False,
            add_special_tokens=True,
            return_tensors="pt",
        )["input_ids"][0]
        return tokens

    def _predecir_chunk(self, chunk: torch.Tensor, fragment_idx: int) -> ResultadoChunk:
        input_ids = chunk.unsqueeze(0).to(self.device)
        attention_mask = torch.ones_like(input_ids).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=-1)[0]

        pred_id = int(torch.argmax(probs).item())
        confidence = float(probs[pred_id].item())
        label = self.class_labels.get(pred_id, f"LABEL_{pred_id}")
        is_vulnerable = pred_id == self.vulnerable_class_id

        scores = {
            self.class_labels.get(i, f"LABEL_{i}"): float(prob.item())
            for i, prob in enumerate(probs)
        }

        decoded_chunk = self.tokenizer.decode(chunk, skip_special_tokens=True)

        return ResultadoChunk(
            fragment=fragment_idx,
            class_id=pred_id,
            label=label,
            confidence=round(confidence, 6),
            is_vulnerable=is_vulnerable,
            code_fragment=decoded_chunk,
            scores=scores,
        )

    def analizar_texto(
        self,
        texto: str,
        chunk_size: Optional[int] = None,
        solo_vulnerables: bool = False,
    ) -> List[dict]:
        self._validar_texto(texto)

        effective_chunk_size = chunk_size or self.chunk_size
        if effective_chunk_size <= 0:
            raise ValueError("chunk_size debe ser > 0")

        tokens = self._tokenizar(texto)
        resultados: List[dict] = []

        for i in range(0, tokens.shape[0], effective_chunk_size):
            fragment_idx = i // effective_chunk_size + 1
            chunk = tokens[i : i + effective_chunk_size]
            pred = self._predecir_chunk(chunk, fragment_idx)

            if solo_vulnerables and not pred.is_vulnerable:
                continue

            resultados.append(
                {
                    "fragment": pred.fragment,
                    "class_id": pred.class_id,
                    "label": pred.label,
                    "confidence": pred.confidence,
                    "is_vulnerable": pred.is_vulnerable,
                    "code_fragment": pred.code_fragment,
                    "scores": pred.scores,
                }
            )

        return resultados

    def analizar_code_fragment(self, code_fragment: str) -> dict:
        chunks = self.analizar_texto(code_fragment)

        vulnerables = [c for c in chunks if c["is_vulnerable"]]
        if vulnerables:
            mejor = max(vulnerables, key=lambda x: x["confidence"])
            resumen_label = "Vulnerable"
            resumen_conf = mejor["confidence"]
            resumen_class_id = mejor["class_id"]
            is_vuln = True
        else:
            mejor = max(chunks, key=lambda x: x["confidence"])
            resumen_label = "No vulnerable"
            resumen_conf = mejor["confidence"]
            resumen_class_id = mejor["class_id"]
            is_vuln = False

        return {
            "label": resumen_label,
            "class_id": resumen_class_id,
            "confidence": resumen_conf,
            "code_fragment": code_fragment

        }

    def analizar_fragmentos(self, code_fragments: Sequence[str]) -> List[dict]:
        resultados: List[dict] = []
        for idx, fragment in enumerate(code_fragments, start=1):
            try:
                analisis = self.analizar_code_fragment(fragment)
                analisis["id"] = idx
                resultados.append(analisis)
            except Exception as exc:
                resultados.append(
                    {
                        "id": idx,
                        "label": "Error",
                        "class_id": -1,
                        "confidence": 0.0,
                        "is_vulnerable": False,
                        "error": str(exc),
                        "chunks": [],
                    }
                )

        return resultados