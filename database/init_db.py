#Codigo para crear la base de datos

from database.connection import engine, Base

# IMPORTAR TODOS LOS MODELOS
from models.sitioWeb_model import SitioWeb
# from models.usuarioModel import Usuario
# from models.analisisModel import Analisis

def create_tables():
    Base.metadata.create_all(bind=engine)