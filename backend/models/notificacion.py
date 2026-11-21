from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.tiempo import ahora


class Notificacion(Base):
    """Mensaje de WhatsApp enviado, simulado, recibido o con error."""

    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    solicitud_id: Mapped[int | None] = mapped_column(ForeignKey("solicitudes.id"), nullable=True, index=True)
    canal: Mapped[str] = mapped_column(String(20), default="whatsapp")
    direccion: Mapped[str] = mapped_column(String(10), default="saliente")  # saliente | entrante
    mensaje: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20))  # enviada | simulada | error | recibida
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
