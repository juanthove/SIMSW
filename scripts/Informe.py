from dotenv import load_dotenv
import os
import traceback
from groq import Groq #pip install groq
from langchain_google_genai import ChatGoogleGenerativeAI
import ollama #pip install ollama
from pathlib import Path
from llama_cpp import Llama #pip install llama-cpp-python


class Informe():
    def __init__(self):
        load_dotenv()
        self.__llm = None
        self.__model = os.getenv("MODEL")
        if not self.__model:
            raise ValueError("No se encontró el modelo de LLM en el entorno.")

        if(self.__model == "gemini-2.5-flash"):
            self.__password = os.getenv("GOOGLE_API_KEY")

            if not self.__password:
                    raise ValueError("No se encontró la clave el modelo gemini-2.5-flash en el entorno.")

        elif(self.__model == "llama-3.3-70b-versatile"):
            self.__password = os.getenv("GROQ_API_KEY")

            if not self.__password:
                    raise ValueError("No se encontró la clave para el modelo llama-3.3-70b-versatile en el entorno.")
        
        elif(self.__model == "tinyllamaQ4-local"):
            print("Voy a buscarlo")
            model_path = (
                Path(__file__).resolve().parent.parent
                / "models"
                / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            )

            if not model_path.exists():
                raise ValueError(
                    f"No existe el modelo GGUF: {model_path}"
                )

            try:
                self.__llm = Llama(
                    model_path=str(model_path),
                    n_ctx=2048,
                    verbose=False
                )

            except Exception as e:
                raise ValueError(
                    f"Error cargando modelo GGUF: {str(e)}"
                )

            self.__password = ""

        elif (self.__model == "tinyllama:latest"):
            self.__password = ""

        else:
            raise ValueError("No se pudo obtener modelo")

    def preguntar(self,promptCausa):
        try:
            if(self.__model == "gemini-2.5-flash"):
                

                llm_geminiAI = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key= self.__password
                )
                
                response = llm_geminiAI.invoke(promptCausa)
                return response
            
            elif(self.__model == "llama-3.3-70b-versatile"):

                clientGroq = Groq(api_key=self.__password)
                response = clientGroq.chat.completions.create(
                    model=self.__model,
                    messages=[
                        {
                            "role": "user",
                            "content": promptCausa
                        }
                    ],
                    temperature=0
                )
                return response.choices[0].message.content or ""
            
            elif(self.__model == "tinyllamaQ4-local"):
                print("Entrando en preguntar")
                response = self.__llm.create_chat_completion(
                    messages=[
                        {
                            "role": "user",
                            "content": promptCausa
                        }
                    ],
                    temperature=0
                )
                print("Voy a retornar")
                return (
                    response["choices"][0]
                    ["message"]["content"]
                )

            elif(self.__model == "tinyllama:latest"):
                try:
                    modelos = ollama.list()


                    modelos_instalados = [
                        m["model"] for m in modelos["models"]
                    ]

                    print(f"los modelos instalados son: {modelos_instalados}")

                    if "tinyllama:latest" not in modelos_instalados:
                        raise ValueError(
                            "El modelo tinyllama no está descargado. "
                            "Ejecuta: ollama pull tinyllama"
                        )
                    
                    response = ollama.chat(
                        model=self.__model,
                        messages=[
                            {
                                "role": "user",
                                "content": promptCausa
                            }
                        ]
                    )

                    return response["message"]["content"]

                except Exception as e:
                    raise ValueError("Error al llamar a ollama: Verifique que ollama esta levantado")

            else:
                raise ValueError("No se encontró el modelo LLM en el entorno.")

        except Exception as e:
            print("Error en armarInforme():", str(e))
            traceback.print_exc()
            raise e

        
