from sqlalchemy import Column, Integer, Numeric, String, UniqueConstraint

from ..database import Base


class ReglaPuntos(Base):
    """Regla parametrizable por el administrador (RN-06). Valores de ejemplo, no oficiales de FSD."""
    __tablename__ = "reglas_puntos"
    __table_args__ = (UniqueConstraint("tipo_residuo", "unidad", name="uq_regla_tipo_unidad"),)

    id = Column(Integer, primary_key=True)
    tipo_residuo = Column(String(30), nullable=False)
    unidad = Column(String(10), nullable=False, default="kg")
    puntos_por_unidad = Column(Numeric(10, 2), nullable=False)
