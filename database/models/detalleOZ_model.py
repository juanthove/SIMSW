from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.connection import Base

class DetalleOZ(Base):
    __tablename__ = "detalle_oz"

    id = Column(Integer, primary_key=True, index=True)

    # Relación 1 a 1 con Informe
    informe_id = Column(
        Integer,
        ForeignKey("informe.id"),
        nullable=False,
        unique=True
    )

    # Datos técnicos del DAST / OWASP ZAP
    endpoint = Column(Text, nullable=True)          # URLs pueden ser largas
    metodo = Column(String(10), nullable=True)      # GET, POST, PUT, DELETE
    parametro = Column(String(255), nullable=True)  # nombre de header, param, etc
    payload = Column(Text, nullable=True)           # body / payload

    def to_dict(self):
        return {
            "id": self.id,
            "informe_id": self.informe_id,
            "endpoint": self.endpoint,
            "metodo": self.metodo,
            "parametro": self.parametro,
            "payload": self.payload
        }
