from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.tiempo import ahora


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # RN-04: identificador legible (SOL-00001), se genera al crear
    codigo: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    tipo_residuo: Mapped[str] = mapped_column(String(20))  # organico | reciclable
    colectivo: Mapped[str] = mapped_column(String(20), index=True)  # RN-01
    descripcion: Mapped[str] = mapped_column(Text)
    cantidad_estimada: Mapped[float | None] = mapped_column(Float, nullable=True)
    unidad_estimada: Mapped[str | None] = mapped_column(String(20), nullable=True)
    direccion: Mapped[str] = mapped_column(String(200))
    estado: Mapped[str] = mapped_column(String(20), default="recibida", index=True)  # RN-04
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora, onupdate=ahora)

    solicitante = relationship("Usuario", foreign_keys=[solicitante_id])
    historial = relationship(
        "HistorialEstado", back_populates="solicitud", order_by="HistorialEstado.id", cascade="all, delete-orphan"
    )
    asignacion = relationship("Asignacion", back_populates="solicitud", uselist=False, cascade="all, delete-orphan")
    programacion = relationship("Programacion", back_populates="solicitud", uselist=False, cascade="all, delete-orphan")
    recoleccion = relationship("Recoleccion", back_populates="solicitud", uselist=False, cascade="all, delete-orphan")
    puntos = relationship("Puntos", back_populates="solicitud", uselist=False, cascade="all, delete-orphan")
