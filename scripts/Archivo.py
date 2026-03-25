class Archivo:
    def __init__(self, id, url, checksum, tipo, largo):
        self.__idArchivo = id
        self.__url = url
        self.__checksum = checksum
        self.__tipo = tipo
        self.__largo = largo

    def to_dict(self):
        return {
            "id": self.__idArchivo,
            "url": self.__url,
            "checksum": self.__checksum,
            "tipo": self.__tipo,
            "largo": self.__largo
        }
    
    def get_id(self):
        return self.__idArchivo

    def get_url(self):
        return self.__url

    def get_checksum(self):
        return self.__checksum

    def get_tipo(self):
        return self.__tipo

    def get_largo(self):
        return self.__largo
    
    
