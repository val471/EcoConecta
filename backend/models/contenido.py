from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Contenido(Base):
    """Contenido educativo sobre gestión de residuos."""

    __tablename__ = "contenidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(160))
    categoria: Mapped[str] = mapped_column(String(20), index=True)  # organico | reciclable | general
    resumen: Mapped[str] = mapped_column(String(300))
    cuerpo: Mapped[str] = mapped_column(Text)
    publicado: Mapped[bool] = mapped_column(Boolean, default=True)
