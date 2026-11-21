from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base, ahora


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, index=True)       # SOL-0001
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    flujo = Column(String(20), nullable=False)                 # RN-01
    tipo_generador = Column(String(30), nullable=False)
    direccion = Column(String(200), nullable=False)
    contacto = Column(String(20), nullable=False)
    observaciones = Column(String(300), default="")
    preferencia_horaria = Column(String(60), default="")
    estado = Column(String(20), nullable=False, default="recibida")
    creada = Column(DateTime(timezone=True), default=ahora)

    usuario = relationship("Usuario")
    historial = relationship("HistorialEstado", order_by="HistorialEstado.id", cascade="all, delete-orphan")
    asignacion = relationship("Asignacion", uselist=False, cascade="all, delete-orphan")
    programacion = relationship("Programacion", uselist=False, cascade="all, delete-orphan")
    recoleccion = relationship("Recoleccion", uselist=False, cascade="all, delete-orphan")
    movimiento = relationship("MovimientoPuntos", uselist=False)
