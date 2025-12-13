from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import traceback


# def armarInforme(fragmento, codigoVulnerable):
#     try:
#         load_dotenv()
#         password = os.getenv("GOOGLE_API_KEY")
#         if not password:
#             raise ValueError("No se encontró la clave GOOGLE_API_KEY en el entorno.")

#         llm_geminiAI = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=password
#         )

#         promptCausa = f"""
#             El siguiente código fue pasado por una herramienta para detección de vulnerabilidades y dio positivo.
#             Dime cuál podría ser la vulnerabilidad en cuestión, en caso de haberla.
#             Limítate a decir: Fragmento X: vulnerabilidad;
#             Luego, en otra línea, marca el fragmento de código con el error;
#             y, tambien en un salto de linea, explica brevemente por qué ocurre y cómo solucionarlo.
#             Si no hay vulnerabilidades, responde: Fragmento X: Vulnerabilidades no encontradas.
#             Fragmento: {fragmento}
#             Código vulnerable: {codigoVulnerable}
#         """

#         response = llm_geminiAI.invoke(promptCausa)

#         # Acceder al texto correctamente
#         # Dependiendo de la versión, puede ser .content o .content[0].text
#         texto = getattr(response, "content", None)
#         if isinstance(texto, list) and len(texto) > 0 and hasattr(texto[0], "text"):
#             texto = texto[0].text
#         elif isinstance(texto, str):
#             pass
#         else:
#             texto = str(response)

#         return {
#             "fragmento": fragmento,
#             "analisis": texto
#         }

#     except Exception as e:
#         print("Error en armarInforme():", str(e))
#         traceback.print_exc()
#         return {
#             "fragmento": fragmento,
#             "error": f"No se pudo procesar el informe: {str(e)}"
#         }


class Informe():
    def __init__(self):
        load_dotenv()
        self.__password = os.getenv("GOOGLE_API_KEY")
        if not self.__password:
                raise ValueError("No se encontró la clave GOOGLE_API_KEY en el entorno.")

    def preguntar(self,promptCausa):
        try:

            llm_geminiAI = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key= self.__password
            )
            
            print("Accediendo")
            
            response = llm_geminiAI.invoke(promptCausa)

            print("Salgo...")

            return response

        except Exception as e:
            print("Error en armarInforme():", str(e))
            traceback.print_exc()

        
