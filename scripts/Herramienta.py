class Herramienta():
    def __init__(self, nombre, version):
        self.__nombre = nombre
        self.__version = version

    def get_nombre(self):
        return self.__nombre

    def get_version(self):
        return self.__version
