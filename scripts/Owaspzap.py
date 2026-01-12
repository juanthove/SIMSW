import os
import subprocess
import requests

from dotenv import load_dotenv
import time 
from scripts.Herramienta import Herramienta
#from Herramienta import *


load_dotenv()

class OwaspZap(Herramienta):
    def __init__(self, nombre, version):
        super().__init__( nombre, version)

        self.ZAP_PORT = "8090"
        self.ZAP_PATH = os.path.join(os.getcwd(), "ZAP_2.17.0", "zap-2.17.0.jar")
        self.ZAP_URL = f"http://127.0.0.1:{self.ZAP_PORT}"
        print(f"El path es: {self.ZAP_PATH}")

        
    def start_zap(self):
        print("[+] Iniciando OWASP ZAP en background...")

        subprocess.Popen(
            [
                "java",
                "-jar",
                self.ZAP_PATH,
                "-daemon",
                "-port", self.ZAP_PORT,
                "-config", "api.disablekey=true"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.wait_for_zap()

    def wait_for_zap(self):
        print("[*] Esperando a que ZAP levante...")
        for _ in range(30):
            try:
                requests.get(self.ZAP_URL)
                print("[+] ZAP listo")
                return
            except:
                time.sleep(1)
        raise RuntimeError("ZAP no respondió")

    def spider(self, url):
        print(f"[+] Spider a {url}")
        requests.get(
            f"{self.ZAP_URL}/JSON/spider/action/scan/",
            params={"url": url}
        )

    def active_scan(self, url):
        print(f"[+] Active Scan a {url}")
        requests.get(
            f"{self.ZAP_URL}/JSON/ascan/action/scan/",
            params={"url": url}
        )

    # def get_alerts(self):
    #     r = requests.get(f"{self.ZAP_URL}/JSON/core/view/alerts/")
    #     return r.json()

    def get_alerts(self):
        r = requests.get(f"{self.ZAP_URL}/JSON/core/view/alerts/")
        data = r.json()

        alerts = data.get("alerts", [])
        resultado = []

        for alerta in alerts:
            resultado.append({
                "tipo": alerta.get("name"),
                "riesgo": alerta.get("risk"),
                "confianza": alerta.get("confidence"),
                "descripcion": alerta.get("description"),
                "solucion": alerta.get("solution"),
                "referencias": alerta.get("reference"),
                "url": alerta.get("url"),
                "cwe": alerta.get("cweid")
            })

        return resultado



    # def scan_activo(self,url):
    #     print(f"La url es: {url}")
    #     resultado = []

    #     proxies = {
    #         'http': f'http://{self.__ZAP_HOST}:{self.__ZAP_PORT}',
    #         'https': f'http://{self.__ZAP_HOST}:{self.__ZAP_PORT}'
    #     }

    #     zap = ZAPv2(apikey=self.__API_KEY, proxies=proxies)

    #     print("Conectado a ZAP, versión:", zap.core.version)

    #     print(f"Iniciando spider contra: {url}")

    #     # 1. Spider primero
    #     spider_id = zap.spider.scan(url)
    #     while int(zap.spider.status(spider_id)) < 100:
    #         print("Spider en progreso...", zap.spider.status(spider_id), "%")
    #         time.sleep(3)

    #     print("Spider finalizado")

    #     # 2. Ahora lanzar Active Scan
    #     print("Iniciando escaneo activo contra:", url)
    #     scan_id = zap.ascan.scan(url)

    #     while int(zap.ascan.status(scan_id)) < 100:
    #         print("Escaneo activo en progreso...", zap.ascan.status(scan_id), "%")
    #         time.sleep(5)

    #     print("Escaneo activo finalizado")

    #     # 3. Obtener alertas
    #     alertas = zap.core.alerts(baseurl=url)
    #     if not alertas:
    #         resultado = None
    #     else:
    #         for alerta in alertas:
    #             resultado.append({
    #                 "tipo": alerta["name"],
    #                 "riesgo": alerta["risk"],
    #                 "descripcion": alerta["description"],
    #                 "solucion": alerta["solution"],
    #                 "referencias": alerta["reference"]
    #             })
    #     return resultado
            

    # def scan_pasivo(self,url):
    #     print(url)
    #     return 0
    

    
