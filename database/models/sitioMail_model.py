from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database.connection import Base

class SitioMail(Base):
    __tablename__ = "sitio_mail"

    id = Column(Integer, primary_key=True, index=True)
    sitio_web_id = Column(Integer, ForeignKey("sitio_web.id"), nullable=False)
    mail_id = Column(Integer, ForeignKey("mail.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("sitio_web_id", "mail_id", name="uq_sitio_mail"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sitio_web_id": self.sitio_web_id,
            "mail_id": self.mail_id
        }
