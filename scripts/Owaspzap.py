import os
import subprocess
import requests

from dotenv import load_dotenv
import time 
from scripts.Herramienta import Herramienta
#from Herramienta import *
from zapv2 import ZAPv2


load_dotenv()

class OwaspZap(Herramienta):
    def __init__(self, nombre, version):
        super().__init__( nombre, version)

        self.ZAP_PORT = "8090"
        self.ZAP_HOST = "127.0.0.1"
        self.ZAP_PATH = os.path.join(os.getcwd(), "ZAP_2.17.0", "zap-2.17.0.jar")
        self.ZAP_URL = f"http://{self.ZAP_HOST}:{self.ZAP_PORT}"
        print(f"El path es: {self.ZAP_PATH}")

    def start_zap(self):
        print("[+] Verificando estado de OWASP ZAP...")

        # ✅ Si ya está levantado, no hacer nada
        try:
            zap = ZAPv2(proxies=self._proxies())
            zap.core.version
            print("[+] ZAP ya estaba levantado")
            return
        except Exception:
            pass  # No está levantado, se inicia abajo

        print("[+] Iniciando OWASP ZAP (local)...")

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
        print("[*] Esperando a ZAP...")
        for _ in range(30):
            try:
                zap = ZAPv2(proxies=self._proxies())
                zap.core.version
                print("[+] ZAP listo")
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

        print("Conectado a ZAP, versión:", zap.core.version)

        # 🔎 Spider
        print(f"[+] Spider a {url}")
        spider_id = zap.spider.scan(url)

        SPIDER_TIMEOUT = 120  #Segundos para que finalice automaticamente
        start_time = time.time()

        while int(zap.spider.status(spider_id)) < 100:
            if time.time() - start_time > SPIDER_TIMEOUT:
                print("[!] Timeout en Spider")
                break

            print("Spider:", zap.spider.status(spider_id), "%")
            time.sleep(2)

        print("[✓] Spider finalizado (o timeout)")


        # ⚔️ Active Scan
        print("[+] Active Scan")
        scan_id = zap.ascan.scan(url)

        ASCAN_TIMEOUT = 600  #Segundos para que finalice automaticamente
        start_time = time.time()

        while int(zap.ascan.status(scan_id)) < 100:
            if time.time() - start_time > ASCAN_TIMEOUT:
                print("[!] Timeout en Active Scan")
                break

            print("Active Scan:", zap.ascan.status(scan_id), "%")
            time.sleep(5)

        print("[✓] Active Scan finalizado (o timeout)")


        # ⏳ Passive Scan
        while int(zap.pscan.records_to_scan) > 0:
            print("Passive Scan pendiente:", zap.pscan.records_to_scan)
            time.sleep(2)

        # 🚨 Alertas
        print("[+] Obteniendo alertas")
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

        print("Conectado a ZAP, versión:", zap.core.version)

        # 🔎 Spider primero (OBLIGATORIO o urls() queda vacío)
        print(f"[+] Spider a {baseurl}")
        spider_id = zap.spider.scan(baseurl)

        SPIDER_TIMEOUT = 120
        start_time = time.time()

        while int(zap.spider.status(spider_id)) < 100:
            if time.time() - start_time > SPIDER_TIMEOUT:
                print("[!] Timeout en Spider")
                break

            print("Spider:", zap.spider.status(spider_id), "%")
            time.sleep(2)

        print("[✓] Spider finalizado")

        # ⏳ Esperar passive
        while int(zap.pscan.records_to_scan) > 0:
            time.sleep(1)

        # ✅ ahora sí obtener urls
        print("[+] Obteniendo URLs descubiertas")

        todas = zap.core.urls()

        filtradas = [u for u in todas if u.startswith(baseurl)]

        print(f"[+] URLs encontradas: {len(filtradas)}")

        return filtradas

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
    

    
