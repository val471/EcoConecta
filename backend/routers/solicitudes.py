from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import settings
from backend.constantes import AVISO_PUNTOS
from backend.database import get_db
from backend.models import HistorialEstado, Puntos, Solicitud, Usuario
from backend.schemas.solicitud import CancelarIn, SolicitudCrear, SolicitudOut
from backend.security.permisos import modo_para, requiere_solicitante, usuario_actual
from backend.services import puntos as svc_puntos
from backend.services import whatsapp_service
from backend.services.enrutamiento import EnrutamientoError, colectivo_para
from backend.services.flujo_estados import FlujoError, cambiar_estado
from backend.services.serializadores import obtener_solicitud, serializar

router = APIRouter(prefix="/api/solicitudes", tags=["solicitudes"])


@router.post("", response_model=SolicitudOut, status_code=201)
def crear(datos: SolicitudCrear, usuario: Usuario = Depends(requiere_solicitante), db: Session = Depends(get_db)):
    if settings.SOLO_USUARIOS_PILOTO and not usuario.es_piloto:
        raise HTTPException(403, "Tu cuenta aún no está habilitada para el piloto.")  # RN-08
    direccion = (datos.direccion or usuario.direccion or "").strip()
    if not direccion:
        raise HTTPException(422, "Indica la dirección de recolección.")
    try:
        colectivo = colectivo_para(datos.tipo_residuo)  # RN-01
    except EnrutamientoError as exc:
        raise HTTPException(422, str(exc)) from exc
    s = Solicitud(
        solicitante_id=usuario.id, tipo_residuo=datos.tipo_residuo, colectivo=colectivo,
        descripcion=datos.descripcion.strip(), cantidad_estimada=datos.cantidad_estimada,
        unidad_estimada=datos.unidad_estimada, direccion=direccion, estado="recibida",
    )
    db.add(s)
    db.flush()
    s.codigo = f"SOL-{s.id:05d}"  # RN-04
    db.add(HistorialEstado(solicitud_id=s.id, estado_anterior=None, estado_nuevo="recibida",
                           usuario_id=usuario.id, nota="Solicitud creada"))
    db.flush()
    whatsapp_service.notificar_recibida(db, s)
    db.commit()
    db.refresh(s)
    return serializar(s, "propio")


@router.get("", response_model=list[SolicitudOut])
def mis_solicitudes(usuario: Usuario = Depends(requiere_solicitante), db: Session = Depends(get_db)):
    filas = db.scalars(select(Solicitud).where(Solicitud.solicitante_id == usuario.id).order_by(Solicitud.id.desc())).all()
    return [serializar(s, "propio") for s in filas]


@router.get("/puntos")
def mis_puntos(usuario: Usuario = Depends(requiere_solicitante), db: Session = Depends(get_db)):
    movimientos = db.scalars(select(Puntos).where(Puntos.usuario_id == usuario.id).order_by(Puntos.id.desc())).all()
    return {
        "total": svc_puntos.total_usuario(db, usuario.id),
        "movimientos": [
            {"solicitud_id": m.solicitud_id, "codigo": f"SOL-{m.solicitud_id:05d}", "puntos": m.puntos,
             "explicacion": m.explicacion, "fecha": m.creado_en}
            for m in movimientos
        ],
        "aviso": AVISO_PUNTOS,
    }


@router.get("/{solicitud_id}", response_model=SolicitudOut)
def detalle(solicitud_id: int, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    s = obtener_solicitud(db, solicitud_id)
    modo = modo_para(usuario, s)
    if modo is None:  # RN-07: no revelar ni que existe
        raise HTTPException(404, "Solicitud no encontrada.")
    return serializar(s, modo)


@router.post("/{solicitud_id}/cancelar", response_model=SolicitudOut)
def cancelar(solicitud_id: int, datos: CancelarIn, usuario: Usuario = Depends(requiere_solicitante),
             db: Session = Depends(get_db)):
    s = obtener_solicitud(db, solicitud_id)
    if s.solicitante_id != usuario.id:
        raise HTTPException(404, "Solicitud no encontrada.")
    if s.estado not in ("recibida", "en_revision"):
        raise HTTPException(409, "La solicitud ya está en gestión; comunícate con el coordinador para cancelarla.")
    try:
        cambiar_estado(db, s, "cancelada", usuario, datos.motivo or "Cancelada por el solicitante")
    except FlujoError as exc:
        raise HTTPException(409, str(exc)) from exc
    whatsapp_service.notificar_cancelada(db, s, datos.motivo)
    db.commit()
    db.refresh(s)
    return serializar(s, "propio")
