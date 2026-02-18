from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import traceback


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
            
            response = llm_geminiAI.invoke(promptCausa)

            return response

        except Exception as e:
            print("Error en armarInforme():", str(e))
            traceback.print_exc()
            raise e

        
