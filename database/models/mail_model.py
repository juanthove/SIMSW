from sqlalchemy import Column, Integer, String
from database.connection import Base

class Mail(Base):
    __tablename__ = "mail"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(255), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo
        }
