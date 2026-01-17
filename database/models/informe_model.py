from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.connection import Base

class Informe(Base):
    __tablename__ = "informe"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String(200), nullable=False)

    descripcion = Column(Text, nullable=True)
    descripcion_humana = Column(Text, nullable=True)
    impacto = Column(Text, nullable=True)
    recomendacion = Column(Text, nullable=True)
    evidencia = Column(Text, nullable=True)

    severidad = Column(Integer, nullable=False)
    codigo = Column(Text, nullable=True)

    analisis_id = Column(Integer, ForeignKey("analisis.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "descripcion_humana": self.descripcion_humana,
            "impacto": self.impacto,
            "recomendacion": self.recomendacion,
            "evidencia": self.evidencia,
            "severidad": self.severidad,
            "codigo": self.codigo,
            "analisis_id": self.analisis_id
        }
