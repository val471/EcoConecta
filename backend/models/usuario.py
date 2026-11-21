from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    password_hash = Column(String(300), nullable=False)
    rol = Column(String(30), nullable=False)
    flujo = Column(String(20))          # solo recolectores: organico | reciclable
    tipo = Column(String(30))           # solo solicitantes: hogar | unidad_productiva
    telefono = Column(String(20))
    es_piloto = Column(Boolean, nullable=False, default=False)   # RN-08
