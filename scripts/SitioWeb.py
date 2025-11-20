import requests
from bs4 import BeautifulSoup
import hashlib
import mimetypes
from urllib.parse import urljoin
#from scripts.Archivo import Archivo   # Ajusta el import según tu estructura
from scripts.Archivo import Archivo


class SitioWeb():
    def __init__(self, id, nombre, url, propietario, fecha_registro, ultima_fecha_monitoreo, archivos):
        self.__idSitio = id
        self.__nombre = nombre
        self.__url = url
        self.__propietario = propietario
        self.__fecha_registro = fecha_registro
        self.__ultima_fecha_monitoreo = ultima_fecha_monitoreo
        self.__archivos = archivos
    
    def to_dict(self):
        return {
            "id": self.__idSitio,
            "nombre": self.__nombre,
            "url": self.__url,
            "propietario": self.__propietario,
            "fecha_registro": self.__fecha_registro,
            "ultima_fecha_monitoreo": self.__ultima_fecha_monitoreo,
            "archivos": [a.to_dict() for a in self.__archivos] if self.__archivos else []
        }

    def get_id(self):
        return self.__idSitio
    
    def get_nombre(self):
        return self.__nombre
    
    def get_url(self):
        return self.__url
    
    def get_propietario(self):
        return self.__propietario
    
    def get_fecha_registro(self):
        return self.__fecha_registro
    
    def get_ultima_fecha_monitoreo(self):
        return self.__ultima_fecha_monitoreo
    
    def get_archivos(self):
        return self.__archivos
    
    def actualizar_monitoreo():
        pass


