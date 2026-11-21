from sqlalchemy import Boolean, Column, Integer, String, Text

from ..database import Base


class Contenido(Base):
    """Material de educación ambiental."""
    __tablename__ = "contenidos"

    id = Column(Integer, primary_key=True)
    categoria = Column(String(30), nullable=False)
    titulo = Column(String(160), nullable=False)
    resumen = Column(String(300), default="")
    cuerpo = Column(Text, default="")
    orden = Column(Integer, default=0)
    publicado = Column(Boolean, default=True)
