class Fragmento():
    def __init__(self, id, idArchivo, label, confidence, codeFragment):
        self.__id = id
        self.__idArchivo = idArchivo
        self.__label = label
        self.__confidence = confidence
        self.__codeFragment = codeFragment
    
    def to_dict(self):
        return {
            "id": self.__id,
            "idArchivo": self.__idArchivo,
            "label": self.__label,
            "confidence": self.__confidence,
            "code_fragment": self.__codeFragment
            
        }
    
    def get_id(self):
        return self.__id

    def get_id_archivo(self):
        return self.__idArchivo
    
    def get_label(self):
        return self.__label

    def get_confidence(self):
        return self.__confidence

    def get_code_fragment(self):
        return self.__codeFragment
    