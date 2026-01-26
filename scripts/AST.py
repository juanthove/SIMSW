from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid
import re

# 🔹 Patrones peligrosos con variantes y case-insensitive
DANGEROUS_CALLS = [
    "eval(", "function(", "innerhtml", "outerhtml", "document.write", "settimeout(", "setinterval("
]

NETWORK_CALLS = [
    "fetch(", "xmlhttprequest", "axios"
]

SOURCES = [
    "location", "document.cookie", "localstorage", "sessionstorage", "window.name"
]


class ASTNode:
    def __init__(self, node_type: str, name: str = None, code: str = None, url: str = None, metadata: dict = None):
        self.id = str(uuid.uuid4())
        self.node_type = node_type
        self.name = name
        self.code = code
        self.url = url
        self.metadata = metadata or {}
        self.children = []


def normalize_snippet(code: str) -> str:
    code = code.replace("\n", " ")
    code = " ".join(code.split())
    return code


def extract_snippet(code: str, pattern: str, window: int = 300) -> Optional[str]:
    idx = code.lower().find(pattern.lower())
    if idx == -1:
        return None
    start = max(0, idx - window)
    end = min(len(code), idx + len(pattern) + window)
    return code[start:end]


def build_js_semantic_ast(code: str, script_name: str, page_url: str) -> ASTNode:
    script_node = ASTNode(
        node_type="Script",
        name=script_name,
        code=code,
        url=page_url,
        metadata={"size": len(code), "script_name": script_name}
    )
    print(f"[DEBUG] Analizando script {script_name}, largo {len(code)}")

    # Dangerous calls
    pattern_variants = [
        re.compile(r"\beval\s*\("),
        re.compile(r"\bFunction\s*\("),
        re.compile(r"\binnerHTML\b"),
        re.compile(r"\bouterHTML\b"),
        re.compile(r"document\.write\s*\("),
        re.compile(r"setTimeout\s*\("),
        re.compile(r"setInterval\s*\(")
    ]

    for pat in pattern_variants:
        for match in pat.finditer(code):
            snippet = extract_snippet(code, match.group())
            if snippet:
                script_node.children.append(
                    ASTNode(
                        node_type="DangerousCall",
                        name=match.group(),
                        code=snippet,
                        url=page_url,
                        metadata={
                            "kind": "sink",
                            "pattern": match.group(),
                            "script": script_name
                        }
                    )
                )

    # Network calls
    for net in NETWORK_CALLS:
        if net.lower() in code.lower():
            snippet = extract_snippet(code, net)
            if snippet:
                print(f"[DEBUG] NetworkCall detectado: {net} en {script_name}, largo snippet: {len(snippet)}")
                script_node.children.append(
                    ASTNode(
                        node_type="NetworkCall",
                        name=net,
                        code=snippet,
                        url=page_url,
                        metadata={"pattern": net}
                    )
                )

    # Sources
    for src in SOURCES:
        if src.lower() in code.lower():
            print(f"[DEBUG] Source detectado: {src} en {script_name}")
            script_node.children.append(
                ASTNode(
                    node_type="Source",
                    name=src,
                    code=extract_snippet(code, src) or code,
                    url=page_url,
                    metadata={"pattern": src}
                )
            )

    return script_node


def build_inline_event_node(event_key, event_data, page_url):
    print(f"[DEBUG] InlineEvent detectado: {event_key}")
    return ASTNode(
        node_type="InlineEvent",
        name=event_key,
        code=event_data.get("codigo"),
        url=page_url,
        metadata={"event": event_data.get("evento")}
    )


def build_worker_node(name, code, url):
    print(f"[DEBUG] WorkerScript detectado: {name}, largo {len(code) if code else 0}")
    return ASTNode(
        node_type="WorkerScript",
        name=name,
        code=code,
        url=url,
        metadata={"size": len(code) if code else 0, "is_worker": True}
    )


def build_network_node(info, url):
    return ASTNode(node_type="NetworkBehavior", url=url, metadata=info)


def recorrer_ast_para_vulberta(node, results):
    if node.node_type in {"InlineEvent", "DangerousCall", "NetworkCall", "Source"}:
        if node.code:
            print(f"[DEBUG] Agregando fragmento a VulBERTa: {node.node_type} - {node.name} - largo {len(node.code)}")
            results.append({
                "id": node.id,
                "code": node.code,
                "origin": node.name,
                "url": node.url,
                "metadata": node.metadata
            })
    for child in node.children:
        recorrer_ast_para_vulberta(child, results)


def preparar_inputs_vulberta(ast_pages, max_len=2000):
    samples = []
    seen = set()

    for page_ast in ast_pages:
        collected = []
        recorrer_ast_para_vulberta(page_ast, collected)
        for item in collected:
            code = item["code"].strip()
            if not code:
                print(f"[DEBUG] Fragmento vacío descartado: {item['id']}")
                continue
            if len(code) > max_len:
                code = code[:max_len]
            code_hash = hash(code)
            if code_hash in seen:
                print(f"[DEBUG] Fragmento duplicado descartado: {item['id']}")
                continue
            seen.add(code_hash)
            print(f"[DEBUG] Fragmento agregado a VulBERTa inputs: {item['id']} - largo {len(code)}")
            samples.append(code)
    print(f"[*] Cantidad total de fragmentos VulBERTa: {len(samples)}")
    return samples


def build_page_ast(url: str, extracted_data: dict) -> ASTNode:
    page_node = ASTNode(node_type="Page", name=url, url=url)
    print(f"[DEBUG] Construyendo AST de página: {url}")

    # Scripts internos
    for name, code in extracted_data.get("internos", {}).items():
        page_node.children.append(build_js_semantic_ast(code, name, url))

    # Scripts externos
    for src, code in extracted_data.get("externos", {}).items():
        if code:
            page_node.children.append(build_js_semantic_ast(code, src, url))

    # Workers
    for name, code in extracted_data.get("workers", {}).items():
        if code:
            page_node.children.append(build_worker_node(name, code, url))

    # Blobs
    for blob in extracted_data.get("blobs", {}):
        print(f"[DEBUG] Blob detectado: {blob}")
        page_node.children.append(ASTNode(node_type="BlobReference", name=blob, url=url))

    # Network
    if extracted_data.get("network"):
        page_node.children.append(build_network_node(extracted_data.get("network"), url))

    # Eventos inline
    for key, event in extracted_data.get("eventos_inline", {}).items():
        page_node.children.append(build_inline_event_node(key, event, url))

    return page_node


def print_ast(node, indent=0):
    print("  " * indent + f"- {node.node_type}: {node.name}")
    for child in node.children:
        print_ast(child, indent + 1)
