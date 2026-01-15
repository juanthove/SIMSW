from sqlalchemy import Column, Integer, String, DateTime
from database.connection import Base
from datetime import datetime, timezone

class SitioWeb(Base):
    __tablename__ = "sitio_web"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    propietario = Column(String(100), nullable=False)

    fecha_registro = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    fecha_ultimo_monitoreo = Column(
        DateTime(timezone=True),
        nullable=True
    )
    frecuencia_monitoreo_minutos = Column(Integer, default=120)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "url": self.url,
            "propietario": self.propietario,
            "fecha_registro": self.fecha_registro,
            "fecha_ultimo_monitoreo": self.fecha_ultimo_monitoreo,
            "frecuencia_monitoreo_minutos": self.frecuencia_monitoreo_minutos
        }
