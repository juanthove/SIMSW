import os
import subprocess

from dotenv import load_dotenv
import time 
from scripts.Herramienta import Herramienta
from zapv2 import ZAPv2


load_dotenv()

class OwaspZap(Herramienta):
    def __init__(self, nombre, version):
        super().__init__( nombre, version)

        self.ZAP_PORT = "8090"
        self.ZAP_HOST = "127.0.0.1"
        self.ZAP_PATH = os.path.join(os.getcwd(), "ZAP_2.17.0", "zap-2.17.0.jar")
        self.ZAP_URL = f"http://{self.ZAP_HOST}:{self.ZAP_PORT}"

    def start_zap(self):

        #Si ya está levantado, no hacer nada
        try:
            zap = ZAPv2(proxies=self._proxies())
            zap.core.version
            return
        except Exception:
            pass


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
        for _ in range(30):
            try:
                zap = ZAPv2(proxies=self._proxies())
                zap.core.version
                return
            except Exception:
                time.sleep(1)

        raise RuntimeError("ZAP no levantó")

    def _proxies(self):
        return {
            "http": f"http://{self.ZAP_HOST}:{self.ZAP_PORT}",
            "https": f"http://{self.ZAP_HOST}:{self.ZAP_PORT}"
        }

    def scan_activo(self, url):
        zap = ZAPv2(proxies=self._proxies())


        #Spider
        spider_id = zap.spider.scan(url)

        SPIDER_TIMEOUT = 120  #Segundos para que finalice automaticamente
        start_time = time.time()

        while int(zap.spider.status(spider_id)) < 100:
            if time.time() - start_time > SPIDER_TIMEOUT:
                break

            time.sleep(2)



        #Active Scan
        scan_id = zap.ascan.scan(url)

        ASCAN_TIMEOUT = 600  #Segundos para que finalice automaticamente
        start_time = time.time()

        while int(zap.ascan.status(scan_id)) < 100:
            if time.time() - start_time > ASCAN_TIMEOUT:
                break

            time.sleep(5)



        #Passive Scan
        while int(zap.pscan.records_to_scan) > 0:
            print("Passive Scan pendiente:", zap.pscan.records_to_scan)
            time.sleep(2)

        #Alertas
        alertas = zap.core.alerts(baseurl=url)

        resultado = []
        for alerta in alertas:
            if alerta.get("riskcode") == "0":
                continue

            resultado.append({
                "tipo": alerta.get("name"),
                "riesgo": alerta.get("risk"),
                "confianza": alerta.get("confidence"), #Nivel de confianaz del hallazgo
                "descripcion": alerta.get("description"),
                "solucion": alerta.get("solution"),
                "referencias": alerta.get("reference"),
                "impacto": alerta.get("riskdesc"),
                "url": alerta.get("url"),
                "cwe": alerta.get("cweid"), #Id estandar de la vulnerabilidad
                "evidencia" : {
                    "endpoint": alerta.get("url"),
                    "parametro": alerta.get("param"),
                    "payload": alerta.get("attack"),
                    "evidencia": alerta.get("evidence"),
                    "metodo": alerta.get("method")
                }
            })


        return resultado
    
    def obtener_urls_zap(self, baseurl):
        zap = ZAPv2(proxies=self._proxies())


        #Spider
        spider_id = zap.spider.scan(baseurl)

        SPIDER_TIMEOUT = 120
        start_time = time.time()

        while int(zap.spider.status(spider_id)) < 100:
            if time.time() - start_time > SPIDER_TIMEOUT:
                print("[!] Timeout en Spider")
                break

            time.sleep(2)


        #Esperar passive
        while int(zap.pscan.records_to_scan) > 0:
            time.sleep(1)

        todas = zap.core.urls()

        filtradas = [u for u in todas if u.startswith(baseurl)]


        return filtradas