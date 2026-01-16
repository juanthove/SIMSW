from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base

class Analisis(Base):
    __tablename__ = "analisis"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)

    # Usa CURRENT_TIMESTAMP de la BD
    fecha = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    # ESTATICO o DINAMICO
    tipo = Column(String(20), nullable=False)

    estado = Column(String(50), nullable=False)

    resultado_global = Column(Integer, nullable=False, default=0)

    sitio_web_id = Column(Integer, ForeignKey("sitio_web.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "tipo": self.tipo,
            "estado": self.estado,
            "resultado_global": self.resultado_global,
            "sitio_web_id": self.sitio_web_id
        }
