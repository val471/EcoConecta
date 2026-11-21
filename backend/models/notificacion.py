from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from ..database import Base, ahora


class Notificacion(Base):
    """Mensajes enviados (o simulados) por WhatsApp."""
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), index=True)
    canal = Column(String(20), default="whatsapp")
    mensaje = Column(String(500), nullable=False)
    estado = Column(String(20), default="simulada")   # simulada | enviada | error
    fecha = Column(DateTime(timezone=True), default=ahora)
