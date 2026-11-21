from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.tiempo import ahora


class Asignacion(Base):
    """RN-03: la atención queda asociada a un coordinador y a un recolector."""

    __tablename__ = "asignaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), unique=True)
    coordinador_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    recolector_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    nota: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    solicitud = relationship("Solicitud", back_populates="asignacion")
    coordinador = relationship("Usuario", foreign_keys=[coordinador_id])
    recolector = relationship("Usuario", foreign_keys=[recolector_id])
