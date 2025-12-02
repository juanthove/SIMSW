from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import smtplib
import os

load_dotenv()

class EnviarAlerta():
    def __init__(self):
        self.__remitente= os.getenv("GMAIL_REMITENTE") 
        self.__contrasena= os.getenv("PASS_APLICACION")

    def enviar_alerta(self, destinatario, asunto, contenido):
        #Creo el mensaje
        mensaje = MIMEMultipart()
        mensaje["From"] = self.__remitente
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        #Agrego el contenido

        mensaje.attach(MIMEText(contenido, 'plain'))

        try:
            #Conectamos con el servidor en el puerto 587
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.__remitente, self.__contrasena)
            server.sendmail(self.__remitente, destinatario, mensaje.as_string())
            server.quit()
            print("Correo enviado")
        except Exception as e:
            print(f"Error al enviar correo {e}")
