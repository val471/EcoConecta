"""RN-05 y RN-06: puntos solo tras registrar la recolección; regla parametrizable y explicable."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.constantes import AVISO_PUNTOS
from backend.models import Puntos, ReglaPuntos, Solicitud
from backend.services.flujo_estados import FlujoError


def calcular(db: Session, tipo: str, unidad: str, cantidad: float) -> tuple[int, ReglaPuntos | None, str]:
    unidad = unidad.strip().lower()
    regla = db.scalars(
        select(ReglaPuntos)
        .where(ReglaPuntos.tipo_residuo == tipo, ReglaPuntos.unidad == unidad, ReglaPuntos.activa.is_(True))
        .order_by(ReglaPuntos.id.desc())
    ).first()
    if regla is None:
        return 0, None, f"No hay una regla activa para {tipo} en {unidad}; se asignan 0 puntos. {AVISO_PUNTOS}"
    puntos = int(round(cantidad * regla.puntos_por_unidad))
    explicacion = (
        f"{cantidad:g} {unidad} de {tipo} × {regla.puntos_por_unidad:g} pts/{unidad} = {puntos} pts "
        f"(regla #{regla.id}). {AVISO_PUNTOS}"
    )
    return puntos, regla, explicacion


def otorgar(db: Session, solicitud: Solicitud) -> Puntos:
    # RN-05: solo después de registrar la recolección
    if solicitud.estado != "recolectada" or solicitud.recoleccion is None:
        raise FlujoError("RN-05: los puntos solo se asignan después de registrar la recolección.")
    if solicitud.puntos is not None:
        return solicitud.puntos
    r = solicitud.recoleccion
    puntos, regla, explicacion = calcular(db, r.tipo_residuo, r.unidad, r.cantidad)
    registro = Puntos(
        usuario_id=solicitud.solicitante_id,
        regla_id=regla.id if regla else None,
        tipo_residuo=r.tipo_residuo,
        cantidad=r.cantidad,
        unidad=r.unidad,
        puntos=puntos,
        explicacion=explicacion,
    )
    solicitud.puntos = registro
    db.add(registro)
    db.flush()
    return registro


def total_usuario(db: Session, usuario_id: int) -> int:
    return int(db.scalar(select(func.coalesce(func.sum(Puntos.puntos), 0)).where(Puntos.usuario_id == usuario_id)) or 0)
