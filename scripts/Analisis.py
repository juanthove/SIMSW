from scripts.SitioWeb import SitioWeb as s
from scripts.vulberta_api import Vulberta as vt

class Analisis():
    def __init__(self, id, fecha, estado, tipo, sitio):
        self.__idAnalisis = id
        self.__fecha = fecha
        self.__estado = estado
        self.__tipo = tipo
        self.__sitio = sitio
    
    def getId(self):
        return self.__idAnalisis
    def getFecha(self):
        return self.__fecha 
    
    def getEstado(self):
        return self.__estado
    
    def getTipo(self):
        return self.__tipo

    def getSitio(self):
        return self.__sitio
    
    def ejectutarDinamico(sitio):
        pass
    
    def ejectutarEstatico(self):
        sitio = self.getSitio()
        url = sitio.getUrl()
        
        id_herramienta = None #Se va a la base de datos, y se verifica el maximo y se le suma 1

        herramienta = vt(
            id=id_herramienta,
            nombre="VulBERTa",
            version="1.0",
            tipo="estatico",
            analisis=self

        )

        resultado = herramienta.analizar_url(url)
        return resultado


    def ejectutarVirusTotal(sitio):
        pass