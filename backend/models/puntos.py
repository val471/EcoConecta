from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.tiempo import ahora


class Puntos(Base):
    """RN-05: solo se crea después de registrar la recolección. Una fila por solicitud."""

    __tablename__ = "puntos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), unique=True)
    regla_id: Mapped[int | None] = mapped_column(ForeignKey("reglas_puntos.id"), nullable=True)
    tipo_residuo: Mapped[str] = mapped_column(String(20))
    cantidad: Mapped[float] = mapped_column(Float)
    unidad: Mapped[str] = mapped_column(String(20))
    puntos: Mapped[int] = mapped_column(Integer)
    explicacion: Mapped[str] = mapped_column(Text)  # RN-06: puntos explicables
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    solicitud = relationship("Solicitud", back_populates="puntos")
