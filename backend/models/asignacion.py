from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..database import Base, ahora


class Asignacion(Base):
    """Asocia la solicitud con su coordinador y su recolector (RN-03)."""
    __tablename__ = "asignaciones"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), unique=True, nullable=False)
    coordinador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    recolector_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), default=ahora)

    coordinador = relationship("Usuario", foreign_keys=[coordinador_id])
    recolector = relationship("Usuario", foreign_keys=[recolector_id])
