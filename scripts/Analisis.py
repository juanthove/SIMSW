import json
import time
from scripts.vulberta_api import Vulberta as vt
from scripts.Owaspzap import OwaspZap as ow
from scripts.EnviarAlerta import EnviarAlerta
import os
import dotenv

class Analisis():
    def __init__(self, id, fecha, estado, tipo, sitio):
        self.__idAnalisis = id
        self.__fecha = fecha
        self.__estado = estado
        self.__tipo = tipo
        self.__sitio = sitio
    
    def get_id(self):
        return self.__idAnalisis
    def get_fecha(self):
        return self.__fecha 
    
    def getE_estado(self):
        return self.__estado
    
    def get_tipo(self):
        return self.__tipo

    def get_sitio(self):
        return self.__sitio
    
    def ejectutar_dinamico(self):
        sitio = self.get_sitio()
        

        herramienta = ow(
            nombre="VulBERTa",
            version="1.0",
        )

        herramienta.start_zap()
        herramienta.spider(sitio)
        time.sleep(10)

        herramienta.active_scan(sitio)
        time.sleep(20)

        alerts = herramienta.get_alerts()
        print(json.dumps(alerts, indent=2))

        #Mando mensaje en caso de encontrar vulnerabilidad high

        
        for item in alerts:
            if(item["riesgo"] == "High"):
                alerta = EnviarAlerta()
                
                #En caso de hacerlo desde .env
                destinatario = os.getenv("GMAIL_DESTINATARIO")

                #En el caso de hacerlo con gmail, lo saco de SitioWeb.propietario

                #destinatario = self.get_sitio().get_propietario()

                asunto = "Alerta de nivel alto encontrada"
                contenido = "Nombre de la alerta: " + item["name"]


                alerta.enviar_alerta(destinatario, asunto, contenido)


        return alerts
        
    
    def ejectutar_estatico(self):
        sitio = self.get_sitio()

        herramienta = vt(
            nombre="VulBERTa",
            version="1.0",
        )

        resultadoVulbERTa = herramienta.analizar_sitio(sitio)
    
        return resultadoVulbERTa


    def ejectutar_virus_total(sitio):
        pass