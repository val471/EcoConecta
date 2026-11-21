from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.tiempo import ahora


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    rol: Mapped[str] = mapped_column(String(30), index=True)
    # huerteros | recicladores (coordinadores y recolectores)
    colectivo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # hogar | unidad_productiva (solicitantes)
    tipo_solicitante: Mapped[str | None] = mapped_column(String(30), nullable=True)
    es_piloto: Mapped[bool] = mapped_column(Boolean, default=False)  # RN-08
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
