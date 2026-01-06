from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid



DANGEROUS_CALLS = [
        "eval(",
        "Function(",
        "innerHTML",
        "outerHTML",
        "document.write",
        "setTimeout(",
        "setInterval("
    ]

NETWORK_CALLS = [
    "fetch(",
    "XMLHttpRequest",
    "axios",
]

SOURCES = [
    "location",
    "document.cookie",
    "localStorage",
    "sessionStorage",
    "window.name"
]


class ASTNode:
    def __init__(
        self,
        node_type: str,
        name: str = None,
        code: str = None,
        url: str = None,
        metadata: dict = None
    ):
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
    """
    Extrae un fragmento de código alrededor de un patrón peligroso
    """
    idx = code.find(pattern)
    if idx == -1:
        return None

    start = max(0, idx - window)
    end = min(len(code), idx + len(pattern) + window)

    return code[start:end]



def build_js_semantic_ast(
    code: str,
    script_name: str,
    page_url: str
) -> ASTNode:

    script_node = ASTNode(
        node_type="Script",
        name=script_name,
        url=page_url,
        metadata={
            "size": len(code),
            "script_name": script_name
        }
    )

    for danger in DANGEROUS_CALLS:
        if danger in code:
            snippet = extract_snippet(code, danger)

            if snippet:
                script_node.children.append(
                    ASTNode(
                        node_type="DangerousCall",
                        name=danger,
                        code=snippet,   # 👈 AHORA ES CÓDIGO REAL
                        url=page_url,
                        metadata={
                            "kind": "sink",
                            "pattern": danger,
                            "script": script_name
                        }
                    )
                )


    # Network
    for net in NETWORK_CALLS:
        if net in code:
            script_node.children.append(
                ASTNode(
                    node_type="NetworkCall",
                    name=net
                )
            )

    # Sources
    for src in SOURCES:
        if src in code:
            script_node.children.append(
                ASTNode(
                    node_type="Source",
                    name=src
                )
            )

    return script_node

def build_inline_event_node(event_key, event_data, page_url):
    return ASTNode(
        node_type="InlineEvent",
        name=event_key,
        code=event_data["codigo"], 
        url=page_url,
        metadata={
            "event": event_data["evento"]
        }
    )


def build_worker_node(name, code, url):
    return ASTNode(
        node_type="WorkerScript",
        name=name,
        url=url,
        metadata={
            "size": len(code) if code else 0,
            "is_worker": True
        }
    )


def build_network_node(info, url):
    return ASTNode(
        node_type="NetworkBehavior",
        url=url,
        metadata=info
    )

def recorrer_ast_para_vulberta(node, results):
    if node.node_type in {
        "InlineEvent",
        "DangerousCall",
        "NetworkCall",
        "Source"
    }:
        if node.code:
            results.append({
                "id": node.id,
                "code": node.code,
                "origin": node.name,
                "url": node.url,
                "metadata": node.metadata   # 👈 AHORA TODO VIAJA
            })

    for child in node.children:
        recorrer_ast_para_vulberta(child, results)



def preparar_inputs_vulberta(ast_pages, max_len=2000):
    samples = []
    seen = set()   # 👈 para deduplicar

    for page_ast in ast_pages:
        collected = []
        recorrer_ast_para_vulberta(page_ast, collected)

        for item in collected:
            code = item["code"].strip()
            #code = normalize_snippet(code) Verificar si es asi

            if not code:
                continue

            if len(code) > max_len:
                code = code[:max_len]

            code_hash = hash(code)
            if code_hash in seen:
                continue

            seen.add(code_hash)
            samples.append(code)

    return samples

def build_page_ast(url: str, extracted_data: dict) -> ASTNode:

    page_node = ASTNode(
        node_type="Page",
        name=url,
        url=url
    )

    # Scripts internos
    for name, code in extracted_data.get("internos", {}).items():
        page_node.children.append(
            build_js_semantic_ast(code, name, url)
        )

    # Scripts externos
    for src, code in extracted_data.get("externos", {}).items():
        if code:
            page_node.children.append(
                build_js_semantic_ast(code, src, url)
            )

    # Workers
    for name, code in extracted_data.get("workers", {}).items():
        if code:
            page_node.children.append(
                build_js_semantic_ast(code, name, url)
            )

    # Blobs
    for blob in extracted_data.get("blobs", {}):
        page_node.children.append(
            ASTNode(
                node_type="BlobReference",
                name=blob,
                url=url
            )
        )

    # Network
    if extracted_data.get("network"):
        page_node.children.append(
            ASTNode(
                node_type="NetworkBehavior",
                url=url
            )
        )

    # Eventos inline
    for key, event in extracted_data.get("eventos_inline", {}).items():
        page_node.children.append(
            build_inline_event_node(key, event, url)
        )

    return page_node

def print_ast(node, indent=0):
    print("  " * indent + f"- {node.node_type}: {node.name}")
    for child in node.children:
        print_ast(child, indent + 1)