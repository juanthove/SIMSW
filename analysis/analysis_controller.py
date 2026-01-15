#Controlador, llama a ejecutar analisis y guarda en la base de datos

from .analysis_service import ejecutar_analisis_estatico, ejecutar_analisis_dinamico, ejecutar_analisis_sonar_qube

def analizar_estatico(url):
    resultado = ejecutar_analisis_estatico(url)

    return {
        "url": url,
        "resultado": resultado
    }

def analizar_dinamico(url):
    print("Entre en el de control")
    resultado = ejecutar_analisis_dinamico(url)

    return {
        "url": url,
        "resultado": resultado
    }

def analizar_sonar_qube(url):
    pass