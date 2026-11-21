from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from ..database import Base, ahora


class HistorialEstado(Base):
    """Una fila por cada cambio de estado (RN-04)."""
    __tablename__ = "historial_estado"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False, index=True)
    estado = Column(String(20), nullable=False)
    por = Column(String(120))
    nota = Column(String(300), default="")
    fecha = Column(DateTime(timezone=True), default=ahora)
