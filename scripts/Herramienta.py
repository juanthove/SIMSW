class Herramienta():
    def __init__(self, id, nombre, version, tipo, analisis):
        self.__idHerramienta = id
        self.__nombre = nombre
        self.__version = version
        self.__tipo = tipo
        self.__analisis  = analisis
    
    def get_idHerramienta(self):
        return self.__idHerramienta

    def get_nombre(self):
        return self.__nombre

    def get_version(self):
        return self.__version

    def get_tipo(self):
        return self.__tipo

    def get_analisis(self):
        return self.__analisis

    