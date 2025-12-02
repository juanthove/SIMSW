import os
import tempfile


from zapv2 import ZAPv2

from dotenv import load_dotenv
import time 
from scripts.Herramienta import Herramienta

load_dotenv()

class OwaspZap(Herramienta):
    def __init__(self, nombre, version):
        super().__init__( nombre, version)
        self.__ZAP_HOST= os.getenv("ZAP_HOST") 
        self.__ZAP_PORT= os.getenv("ZAP_PORT")
        self.__API_KEY= os.getenv("API_KEY")

    def scan_activo(self,url):
        print(f"La url es: {url}")
        resultado = []

        proxies = {
            'http': f'http://{self.__ZAP_HOST}:{self.__ZAP_PORT}',
            'https': f'http://{self.__ZAP_HOST}:{self.__ZAP_PORT}'
        }

        zap = ZAPv2(apikey=self.__API_KEY, proxies=proxies)

        print("Conectado a ZAP, versión:", zap.core.version)

        print(f"Iniciando spider contra: {url}")

        # 1. Spider primero
        spider_id = zap.spider.scan(url)
        while int(zap.spider.status(spider_id)) < 100:
            print("Spider en progreso...", zap.spider.status(spider_id), "%")
            time.sleep(3)

        print("Spider finalizado")

        # 2. Ahora lanzar Active Scan
        print("Iniciando escaneo activo contra:", url)
        scan_id = zap.ascan.scan(url)

        while int(zap.ascan.status(scan_id)) < 100:
            print("Escaneo activo en progreso...", zap.ascan.status(scan_id), "%")
            time.sleep(5)

        print("Escaneo activo finalizado")

        # 3. Obtener alertas
        alertas = zap.core.alerts(baseurl=url)
        if not alertas:
            resultado = None
        else:
            for alerta in alertas:
                resultado.append({
                    "tipo": alerta["name"],
                    "riesgo": alerta["risk"],
                    "descripcion": alerta["description"],
                    "solucion": alerta["solution"],
                    "referencias": alerta["reference"]
                })
        return resultado
            

    def scan_pasivo(self,url):
        print(url)
        return 0
    

    
