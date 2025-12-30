import os
from pathlib import Path
from scripts.tools import extraer_scripts_con_playwright, guardar_scripts_internos, url_a_nombre_carpeta, guardar_scripts_internos_sin_formato
from scripts.Archivo import Archivo
from scripts.SitioWeb import SitioWeb
from scripts.Analisis import Analisis
from scripts.Informe import Informe
import re


def analisis_estatico(url):
    
    #Tendria que checkear que la url no existe
    #En caso de que no exista, hago lo siguiente, en caso de que si, voy a buscar los datos a la base. 
    
    id = 0
    archivos = []
    direccion = url_a_nombre_carpeta(url)
    
    
    #Verifico que no exista direccion de url
    
    ruta = Path("./urlsAnalizadas") / direccion 

    if ruta.exists():
        print("La ruta existe en el sistema")
    else:
        
        scripts = extraer_scripts_con_playwright(url)
        
        
        """
        items = scripts.items()
        for  categoria, grupo in items:
            for nombre, codigo in grupo.items(): 
                print(f"Categoria: {categoria}, Nombre: {nombre}, Codigo: {codigo[:30]}...")

        """



        items = scripts.items()
        for categoria, grupo in items:
            try:
                direccion_final = Path("./urlsAnalizadas") / direccion / categoria

                # Crear carpeta si no existe
                direccion_final.mkdir(parents=True, exist_ok=True)
                rutas = guardar_scripts_internos(grupo, str(direccion_final))
                print(f"Guardado en: {direccion_final}")
                print("Las rutas son: ")
                for a in rutas:
                    print(f"{a}, ")

            except Exception as e:
                print(f"Error en {categoria}: {e}")



def analisis_estatico2(url):
    
    #Tendria que checkear que la url no existe
    #En caso de que no exista, hago lo siguiente, en caso de que si, voy a buscar los datos a la base. 
    
    id = 0
    archivos = []
    direccion = url_a_nombre_carpeta(url)
    
    
    #Verifico que no exista direccion de url
    
    ruta = Path("./urlsAnalizadas") / direccion 

    print("Verifico")
    if ruta.exists():
        print("La ruta existe en el sistema")
        
        # Solo subcarpetas de primer nivel
        subcarpetas = [p for p in ruta.iterdir() if p.is_dir()]

        for carpeta in subcarpetas: 
            # Solo archivos dentro de esa subcarpeta
            for fila in carpeta.iterdir():
                if fila.is_file():
                    with fila.open("r", encoding="utf-8") as f:
                        contenido = f.read()
                        # fila ya es la ruta completa al archivo
                        rutaFinal = fila  
                        
                        # Ejemplo de objeto Archivo
                        a = Archivo(id, fila.name, rutaFinal, None, None, len(contenido), contenido)
                        archivos.append(a)
                id += 1


        s = SitioWeb(1, "YouTube", url, "Google", "29/11/25", "Today", archivos)
        print(f"La url del sitio es: {s.get_url()}")
        #Seguir llamada a Analisis.py

    else:
        print("No existia")
        scripts = extraer_scripts_con_playwright(url)
        
        
        """
        items = scripts.items()
        for  categoria, grupo in items:
            for nombre, codigo in grupo.items(): 
                print(f"Categoria: {categoria}, Nombre: {nombre}, Codigo: {codigo[:30]}...")

        """



        items = scripts.items()
        for categoria, grupo in items:
            try:
                direccion_final = Path("./urlsAnalizadas") / direccion / categoria

                # Crear carpeta si no existe
                direccion_final.mkdir(parents=True, exist_ok=True)

                for nombre, codigo in grupo.items():
                    ruta = guardar_scripts_internos_sin_formato(nombre, codigo, str(direccion_final))
                    if not codigo:
                        print(f"Script vacío o None: {nombre}")
                        codigo = ""
                    a = Archivo(id, nombre, ruta, None, None, len(codigo), codigo)
                    print(f"Guardado en: {direccion_final}")
                    archivos.append(a)#
                    print(f"Categoria: {categoria}, Nombre: {nombre}, Codigo: {codigo[:30]}...")#
                    id = id + 1
            except Exception as e:
                print(f"Error en {categoria}: {e}")

    s = SitioWeb(1, "YouTube", url, "Google", "29/11/25", "Today", archivos)
    a = Analisis(0, "Today", "X", "Estatico", s)
    print("Ento a hacer el analisis")
    res = a.ejectutar_estatico()
    print("Salgo de hacer el analisis")

    
    son = 0
    noson = 0
    lista_mayores = []
    for item in res:
        if(item.get_label() == "Vulnerable"):
            if(item.get_confidence() > 0.9):
                print(f"Es mayor a 0.7, el condidebnce es: {item.get_confidence()}\n")
                
                lista_mayores.append({
                    "id": item.get_id(),
                    "idArchivo": item.get_id_archivo(),
                    "code_fragment": item.get_code_fragment()
                })
                son = son + 1
            else:
                print(f"confidence es menor o igual a 0.7, es: {item.get_confidence()}\n")
                noson = noson + 1

    print(f"La cantidad que son mayores son:{son}, y menores: {noson}")

    # Supongamos que ya armaste lista_mayores con los dicts de cada fragmento
    prompt = """
    Analiza la siguiente lista de fragmentos de código vulnerables, teniendo en cuenta que pueden ser falsos positivos.
    Devuélveme la respuesta en formato JSON válido, con un array de objetos. Solo el json, nada más. 
    Cada objeto debe tener los siguientes campos:
    - id: el id del fragmento
    - idArchivo: el id del archivo
    - tipo_vulnerabilidad: el tipo de vulnerabilidad detectada (ejemplo: inyeccionSQL, XSS, CSRF, etc.)
    - descripcion: una muy breve explicación de qué es esa vulnerabilidad, solo en caso de no ser falso positivo
    - nivel: puedes basarte en el low, medium o high de Owasp Zap
    - ubicacion: en qué parte del código se da (ejemplo: función, línea, fragmento), resaltame esa parte

    Aquí está la lista de fragmentos:
    """ 

    for frag in lista_mayores:  
        prompt += f"\nID: {frag['id']}, Archivo: {frag['idArchivo']}, Código:\n{frag['code_fragment']}\n"

    informe = Informe()
    resultadoFinal = informe.preguntar(prompt)

    return resultadoFinal
    #Seguir llamada a Analisis.py




#url = "https://app.y.gy/captcha?&id=295481"
url = "https://www.iana.org/help/example-domains"

res = analisis_estatico2(url)


print(res)
