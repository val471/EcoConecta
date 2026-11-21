from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.tiempo import ahora


class Programacion(Base):
    """RN-02: una solicitud solo está 'programada' si tiene día, hora y persona encargada."""

    __tablename__ = "programaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), unique=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    encargado_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    registrado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nota: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    solicitud = relationship("Solicitud", back_populates="programacion")
    encargado = relationship("Usuario", foreign_keys=[encargado_id])
    registrado_por = relationship("Usuario", foreign_keys=[registrado_por_id])
