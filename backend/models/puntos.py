from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from ..database import Base, ahora


class MovimientoPuntos(Base):
    """Puntos otorgados tras registrar la recolección (RN-05), con la explicación del cálculo."""
    __tablename__ = "puntos"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), unique=True, nullable=False)
    puntos = Column(Integer, nullable=False)
    explicacion = Column(String(300), nullable=False)
    fecha = Column(DateTime(timezone=True), default=ahora)
