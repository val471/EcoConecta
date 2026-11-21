from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.tiempo import ahora


class ReglaPuntos(Base):
    """RN-06: regla parametrizable por el administrador. Los valores son de ejemplo, no oficiales."""

    __tablename__ = "reglas_puntos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_residuo: Mapped[str] = mapped_column(String(20), index=True)
    unidad: Mapped[str] = mapped_column(String(20))
    puntos_por_unidad: Mapped[float] = mapped_column(Float)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
