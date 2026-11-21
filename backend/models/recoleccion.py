from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.tiempo import ahora


class Recoleccion(Base):
    __tablename__ = "recolecciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), unique=True)
    recolector_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    tipo_residuo: Mapped[str] = mapped_column(String(20))
    cantidad: Mapped[float] = mapped_column(Float)
    unidad: Mapped[str] = mapped_column(String(20))
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    solicitud = relationship("Solicitud", back_populates="recoleccion")
    recolector = relationship("Usuario", foreign_keys=[recolector_id])
