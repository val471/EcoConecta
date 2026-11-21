from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..constantes import TIPOS_RESIDUO
from ..database import get_db
from ..models import Asignacion, MovimientoPuntos, Recoleccion, ReglaPuntos, Solicitud, Usuario
from ..schemas import RecoleccionIn
from ..security.permisos import requiere_roles
from ..services.flujo_estados import cambiar_estado
from ..services.puntos import calcular_puntos
from ..services.serializacion import solicitud_dict
from ..services.whatsapp_service import notificar

router = APIRouter(prefix="/recolector", tags=["recolector"])
solo_recolector = requiere_roles("recolector")


def _asignada_a(db: Session, codigo: str, u: Usuario):
    return (db.query(Solicitud).join(Asignacion, Asignacion.solicitud_id == Solicitud.id)
            .filter(Solicitud.codigo == codigo, Asignacion.recolector_id == u.id).first())


@router.get("/asignaciones")
def asignaciones(db: Session = Depends(get_db), u: Usuario = Depends(solo_recolector)):
    """RN-07: el recolector solo ve (con contacto y dirección) lo que le asignaron."""
    filas = (db.query(Solicitud).join(Asignacion, Asignacion.solicitud_id == Solicitud.id)
             .filter(Asignacion.recolector_id == u.id, Solicitud.estado != "cancelada")
             .order_by(Solicitud.id.desc()).all())
    return [solicitud_dict(s, operativo=True) for s in filas]


@router.post("/solicitudes/{codigo}/recoleccion")
def registrar(codigo: str, datos: RecoleccionIn, db: Session = Depends(get_db), u: Usuario = Depends(solo_recolector)):
    s = _asignada_a(db, codigo, u)
    if not s:
        raise HTTPException(404, "Solicitud no asignada a ti")
    tipo = (datos.tipo_residuo or "").strip()
    if tipo not in TIPOS_RESIDUO or TIPOS_RESIDUO[tipo]["flujo"] != s.flujo:
        raise HTTPException(400, "Ese material no corresponde a este tipo de solicitud")
    if datos.unidad != "kg":
        raise HTTPException(400, "La unidad debe ser kg")
    cantidad = Decimal(str(datos.cantidad)).quantize(Decimal("0.01"))
    if not (Decimal("0") < cantidad <= Decimal("1000")):
        raise HTTPException(400, "Indica una cantidad mayor a 0")

    cambiar_estado(db, s, "recolectada", u.nombre, "Recolección registrada")           # RN-05: primero el cierre...
    db.add(Recoleccion(solicitud_id=s.id, tipo_residuo=tipo, cantidad=cantidad, unidad="kg"))
    regla = db.query(ReglaPuntos).filter(ReglaPuntos.tipo_residuo == tipo, ReglaPuntos.unidad == "kg").first()
    total, explicacion = calcular_puntos(regla.puntos_por_unidad if regla else None, tipo, cantidad, "kg")
    db.add(MovimientoPuntos(usuario_id=s.usuario_id, solicitud_id=s.id, puntos=total, explicacion=explicacion))  # ...luego los puntos
    db.commit()
    db.refresh(s)
    notificar(db, s, f"Registramos la entrega de tu solicitud {s.codigo}. Ganaste {total} puntos. ¡Gracias por participar!")
    db.refresh(s)
    return solicitud_dict(s, operativo=True)
