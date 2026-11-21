from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String

from ..database import Base, ahora


class Programacion(Base):
    """Día, hora y persona encargada (RN-02)."""
    __tablename__ = "programaciones"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), unique=True, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(String(20), nullable=False)
    persona = Column(String(120), nullable=False)
    creada = Column(DateTime(timezone=True), default=ahora)
