import pdfkit
import os
from io import BytesIO
import sys
import os

def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def limpiar_html(html):
    if not html:
        return ""
    return (str(html)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def generar_html_reporte(data):

    severidad_texto = {
        1: "Baja",
        2: "Media",
        3: "Alta"
    }

    def generar_caratula():
        return f"""
        <div class="contenedor page-break">
            <header class="encabezado">
                <h1>{data['sitio']['nombre']}</h1>
                <span class="badge">{data['analisis']['tipo']}</span>
            </header>

            <section class="bloque">
                <h2>Información General</h2>

                <div><strong>URL:</strong> {data['sitio']['url'] or "-"}</div>
                <div><strong>Fecha:</strong> {data['analisis']['fecha']}</div>
                <div><strong>Tipo de análisis:</strong> {data['analisis']['tipo']}</div>
                <div><strong>Estado:</strong> {data['analisis']['estado']}</div>
                <div><strong>Resultado global:</strong> {data['analisis']['resultado_global']}</div>
            </section>
        </div>
        """

    def generar_detalle(inf, es_ultimo):
        severidad = severidad_texto.get(inf.get("severidad"), "Desconocida")
        page_break = "" if es_ultimo else "page-break"

        detalle_oz = inf.get("detalleOZ") or {}

        return f"""
        <div class="contenedor {page_break}">
            <header class="encabezado">
                <h1>{inf.get("titulo")}</h1>
                <span class="badge {severidad}">{severidad}</span>
            </header>

            <section class="bloque">
                <h2>Descripción</h2>
                <p>{limpiar_html(inf.get("descripcion")) or "-"}</p>
            </section>

            <section class="bloque">
                <h2>Impacto</h2>
                <p>{limpiar_html(inf.get("impacto")) or "-"}</p>
            </section>

            <section class="bloque">
                <h2>Recomendación</h2>
                <p>{limpiar_html(inf.get("recomendacion")) or "-"}</p>
            </section>

            <section class="bloque">
                <h2>Evidencia</h2>
                <p>{limpiar_html(inf.get("evidencia"))}</p>
            </section>

            {"<section class='bloque'><h2>Código Analizado</h2><pre><code>" + limpiar_html(inf.get("codigo")) + "</code></pre></section>" if inf.get("codigo") else ""}

            {f"""
            <section class="bloque">
                <h2>Detalle Técnico</h2>

                {f'''
                <div class="oz-item">
                    <strong>Endpoint:</strong>
                    <span>{detalle_oz.get("endpoint")}</span>
                </div>
                ''' if detalle_oz.get("endpoint") else ""}

                {f'''
                <div class="oz-item">
                    <strong>Método:</strong>
                    <span>{detalle_oz.get("metodo")}</span>
                </div>
                ''' if detalle_oz.get("metodo") else ""}

                {f'''
                <div class="oz-item">
                    <strong>Parámetro:</strong>
                    <span>{detalle_oz.get("parametro")}</span>
                </div>
                ''' if detalle_oz.get("parametro") else ""}

                {f'''
                <div class="oz-item">
                    <strong>Payload:</strong>
                    <pre><code>{limpiar_html(detalle_oz.get("payload"))}</code></pre>
                </div>
                ''' if detalle_oz.get("payload") else ""}

            </section>
            """ if detalle_oz else ""}
        </div>
        """

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
            }}

            p {{
                word-break: break-word;
            }}

            .contenedor {{
                max-width: 900px;
                margin: 0 auto;
                background: #fff;
                padding: 24px;
                border-radius: 6px;
            }}

            .encabezado {{
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 12px;
            }}

            .badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 14px;
                font-weight: bold;
                font-size: 13px;
            }}

            .badge.Alta {{ background: #fce4e4; color: #c0392b; }}
            .badge.Media {{ background: #fff3cd; color: #d68910; }}
            .badge.Baja {{ background: #e8f8f5; color: #27ae60; }}

            .bloque {{
                margin-top: 20px;
            }}

            .bloque h2 {{
                font-size: 16px;
                margin-bottom: 18px;
                border-left: 4px solid #bbb;
                padding-left: 8px;
            }}

            pre {{
                background: #f4f4f4;
                padding: 12px;
                border-radius: 4px;
                font-size: 13px;
                white-space: pre-wrap;
                word-break: break-word;
                page-break-inside: avoid;
            }}

            .oz-item {{
                display: flex;
                gap: 8px;
                margin-bottom: 14px;
                align-items: flex-start;
                padding: 6px 0;
                border-bottom: 1px dashed #e5e5e5;
                page-break-inside: avoid;
            }}

            .oz-item strong {{
                min-width: 100px;
                color: #555;
            }}

            .oz-item span {{
                font-family: Consolas, Monaco, monospace;
                font-size: 13px;
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 4px;
            }}

            .oz-item pre {{
                margin-top: 8px;
                margin-left: 100px;
            }}

            .page-break {{
                page-break-after: always;
            }}
        </style>
    </head>
    <body>

        {generar_caratula()}

        {"".join([
            generar_detalle(inf, i == len(data["informes"]) - 1)
            for i, inf in enumerate(data["informes"])
        ])}

    </body>
    </html>
    """

    return html


def generar_pdf_reporte(data):
    html = generar_html_reporte(data)

    path_wkhtmltopdf = get_resource_path("wkhtmltox/bin/wkhtmltopdf.exe")

    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    options = {
        "encoding": "UTF-8",
        "enable-local-file-access": None,
        "quiet": ""
    }

    #Generar PDF en memoria
    pdf_bytes = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    return BytesIO(pdf_bytes)