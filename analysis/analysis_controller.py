#Controlador, llama a ejecutar analisis y guarda en la base de datos

from .analysis_service import ejecutar_analisis_estatico

def analizar_estatico(url):
    resultado = ejecutar_analisis_estatico(url)

    return {
        "url": url,
        "resultado": resultado
    }