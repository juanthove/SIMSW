class SitioWeb():
    def __init__(self, id, nombre, url, propietario, fecha_registro, ultima_fecha_monitoreo, archivos):
        self.__idSitio = id
        self.__nombre = nombre
        self.__url = url
        self.__propietario = propietario
        self.__fecha_registro = fecha_registro
        self.__ultima_fecha_monitoreo = ultima_fecha_monitoreo
        self.__archivos = archivos
    
    def getId(self):
        return self.__idSitio
    
    def getNombre(self):
        return self.__nombre
    
    def getUrl(self):
        return self.__url
    
    def getPropietario(self):
        return self.__propietario
    
    def getFechaRegistro(self):
        return self.__fecha_registro
    
    def getUltimaFechaMonitoreo(self):
        return self.__ultima_fecha_monitoreo
    
    def getArchivos(self):
        return self.__archivos
    
    def actualizarMonitoreo():
        pass