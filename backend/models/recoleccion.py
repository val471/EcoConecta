from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from ..database import Base, ahora


class Recoleccion(Base):
    """Cierre de la solicitud: qué y cuánto se entregó."""
    __tablename__ = "recolecciones"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), unique=True, nullable=False)
    tipo_residuo = Column(String(30), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    unidad = Column(String(10), nullable=False, default="kg")
    fecha = Column(DateTime(timezone=True), default=ahora)
