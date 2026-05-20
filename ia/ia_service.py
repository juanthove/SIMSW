import os
from dotenv import load_dotenv

load_dotenv()


MODELOS = {
    "gemini": "gemini-2.5-flash",
    "groq": "llama-3.3-70b-versatile",
    "ollama": "ollama-local"
}


#Obtener configuración actual
def obtener_configuracion_ia():
    return {
        "MODEL": os.getenv("MODEL", MODELOS["gemini"]),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", "")
    }


#Actualizar toda la configuración
def actualizar_configuracion_ia(data):

    model = data.get("MODEL", "")
    google_api_key = data.get("GOOGLE_API_KEY", "")
    groq_api_key = data.get("GROQ_API_KEY", "")

    actualizar_env("MODEL", model)
    actualizar_env("GOOGLE_API_KEY", google_api_key)
    actualizar_env("GROQ_API_KEY", groq_api_key)


#Actualizar valor en .env
def actualizar_env(clave, valor):

    ruta_env = ".env"

    if not os.path.exists(ruta_env):
        raise FileNotFoundError("No existe el archivo .env")

    with open(ruta_env, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    encontrada = False

    for i, linea in enumerate(lineas):

        if linea.startswith(f"{clave}="):
            lineas[i] = f"{clave}={valor}\n"
            encontrada = True
            break

    #Agregar si no existe
    if not encontrada:
        lineas.append(f"{clave}={valor}\n")

    with open(ruta_env, "w", encoding="utf-8") as f:
        f.writelines(lineas)

    #Actualizar runtime
    os.environ[clave] = valor