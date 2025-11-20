class Archivo:
    def __init__(self, id, nombre, url, checksum, tipo, largo, codigo):
        self.__idArchivo = id
        self.__nombre = nombre
        self.__url = url
        self.__checksum = checksum
        self.__tipo = tipo
        self.__largo = largo
        self.__codigo = codigo

    def to_dict(self):
        return {
            "id": self.__idArchivo,
            "nombre": self.__nombre,
            "url": self.__url,
            "checksum": self.__checksum,
            "tipo": self.__tipo,
            "largo": self.__largo,
            "codigo": self.__codigo,
        }
    
    def get_id(self):
        return self.__idArchivo

    def get_nombre(self):
        return self.__nombre

    def get_url(self):
        return self.__url

    def get_checksum(self):
        return self.__checksum

    def get_tipo(self):
        return self.__tipo

    def get_largo(self):
        return self.__largo
    
    def get_codigo(self):
        return self.__codigo
    
