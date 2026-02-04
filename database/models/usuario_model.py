from sqlalchemy import Column, Integer, String
from database.connection import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    nombre = Column(String(50), nullable=False)


    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre
        }
