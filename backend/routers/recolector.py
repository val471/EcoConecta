from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Asignacion, Recoleccion, Solicitud, Usuario
from backend.schemas.solicitud import RecoleccionIn, SolicitudOut
from backend.security.permisos import modo_para, requiere_recolector
from backend.services import puntos as svc_puntos
from backend.services import whatsapp_service
from backend.services.flujo_estados import FlujoError, cambiar_estado
from backend.services.serializadores import obtener_solicitud, serializar

router = APIRouter(prefix="/api/recolector", tags=["recolector"])


def _mia(db: Session, usuario: Usuario, solicitud_id: int) -> Solicitud:
    s = obtener_solicitud(db, solicitud_id)
    if modo_para(usuario, s) != "operativo":  # RN-07: solo lo que tiene asignado
        raise HTTPException(404, "Solicitud no encontrada.")
    return s


@router.get("/solicitudes", response_model=list[SolicitudOut])
def asignadas(estado: str | None = None, usuario: Usuario = Depends(requiere_recolector), db: Session = Depends(get_db)):
    consulta = (select(Solicitud).join(Asignacion, Asignacion.solicitud_id == Solicitud.id)
                .where(Asignacion.recolector_id == usuario.id).order_by(Solicitud.id.desc()))
    if estado:
        consulta = consulta.where(Solicitud.estado == estado)
    return [serializar(s, "operativo") for s in db.scalars(consulta).all()]


@router.get("/solicitudes/{solicitud_id}", response_model=SolicitudOut)
def detalle(solicitud_id: int, usuario: Usuario = Depends(requiere_recolector), db: Session = Depends(get_db)):
    return serializar(_mia(db, usuario, solicitud_id), "operativo")


@router.post("/solicitudes/{solicitud_id}/recoleccion", response_model=SolicitudOut)
def registrar_recoleccion(solicitud_id: int, datos: RecoleccionIn, usuario: Usuario = Depends(requiere_recolector),
                          db: Session = Depends(get_db)):
    """Registra la recolección, cierra la solicitud (recolectada) y entonces asigna puntos (RN-05)."""
    s = _mia(db, usuario, solicitud_id)
    if s.estado != "programada":
        raise HTTPException(409, f"Solo se registra la recolección de una solicitud programada (estado actual: '{s.estado}').")
    try:
        s.recoleccion = Recoleccion(recolector_id=usuario.id, tipo_residuo=s.tipo_residuo, cantidad=datos.cantidad,
                                    unidad=datos.unidad.strip().lower(), observaciones=datos.observaciones)
        db.flush()
        cambiar_estado(db, s, "recolectada", usuario, "Recolección registrada")
        svc_puntos.otorgar(db, s)
    except FlujoError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    whatsapp_service.notificar_recolectada(db, s)
    db.commit()
    db.refresh(s)
    return serializar(s, "operativo")
