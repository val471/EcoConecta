from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.constantes import ROL_RECOLECTOR
from backend.database import get_db
from backend.models import Asignacion, Programacion, Solicitud, Usuario
from backend.schemas.solicitud import (AsignarIn, CancelarIn, ProgramarIn, RecolectorPublico, RevisarIn, SolicitudOut)
from backend.security.permisos import colectivo_de, requiere_coordinador
from backend.services import whatsapp_service
from backend.services.flujo_estados import FlujoError, cambiar_estado
from backend.services.serializadores import obtener_solicitud, serializar

router = APIRouter(prefix="/api/coordinador", tags=["coordinador"])


def _solicitud_del_colectivo(db: Session, usuario: Usuario, solicitud_id: int) -> Solicitud:
    s = obtener_solicitud(db, solicitud_id)
    if s.colectivo != colectivo_de(usuario):  # RN-07: un coordinador solo atiende su colectivo
        raise HTTPException(404, "Solicitud no encontrada.")
    return s


def _recolector_valido(db: Session, s: Solicitud, recolector_id: int) -> Usuario:
    r = db.get(Usuario, recolector_id)
    if r is None or r.rol != ROL_RECOLECTOR or not r.activo or r.colectivo != s.colectivo:
        raise HTTPException(422, f"El recolector debe ser una persona activa del colectivo de {s.colectivo}.")
    return r


@router.get("/solicitudes", response_model=list[SolicitudOut])
def bandeja(estado: str | None = None, usuario: Usuario = Depends(requiere_coordinador), db: Session = Depends(get_db)):
    consulta = select(Solicitud).where(Solicitud.colectivo == colectivo_de(usuario)).order_by(Solicitud.id.desc())
    if estado:
        consulta = consulta.where(Solicitud.estado == estado)
    return [serializar(s, "operativo") for s in db.scalars(consulta).all()]


@router.get("/solicitudes/{solicitud_id}", response_model=SolicitudOut)
def detalle(solicitud_id: int, usuario: Usuario = Depends(requiere_coordinador), db: Session = Depends(get_db)):
    return serializar(_solicitud_del_colectivo(db, usuario, solicitud_id), "operativo")


@router.get("/recolectores", response_model=list[RecolectorPublico])
def recolectores(usuario: Usuario = Depends(requiere_coordinador), db: Session = Depends(get_db)):
    filas = db.scalars(
        select(Usuario).where(Usuario.rol == ROL_RECOLECTOR, Usuario.activo.is_(True),
                              Usuario.colectivo == colectivo_de(usuario)).order_by(Usuario.nombre)
    ).all()
    return [RecolectorPublico(id=r.id, nombre=r.nombre, colectivo=r.colectivo) for r in filas]


@router.post("/solicitudes/{solicitud_id}/revisar", response_model=SolicitudOut)
def revisar(solicitud_id: int, datos: RevisarIn, usuario: Usuario = Depends(requiere_coordinador),
            db: Session = Depends(get_db)):
    s = _solicitud_del_colectivo(db, usuario, solicitud_id)
    try:
        cambiar_estado(db, s, "en_revision", usuario, datos.nota or "Solicitud en revisión")
    except FlujoError as exc:
        raise HTTPException(409, str(exc)) from exc
    db.commit()
    db.refresh(s)
    return serializar(s, "operativo")


@router.post("/solicitudes/{solicitud_id}/asignar", response_model=SolicitudOut)
def asignar(solicitud_id: int, datos: AsignarIn, usuario: Usuario = Depends(requiere_coordinador),
            db: Session = Depends(get_db)):
    s = _solicitud_del_colectivo(db, usuario, solicitud_id)
    if s.estado != "en_revision":
        raise HTTPException(409, f"Solo se asigna una solicitud en revisión (estado actual: '{s.estado}').")
    recolector = _recolector_valido(db, s, datos.recolector_id)
    try:
        # RN-03: la atención queda asociada a coordinador y recolector
        s.asignacion = Asignacion(coordinador_id=usuario.id, recolector_id=recolector.id, nota=datos.nota)
        db.flush()
        cambiar_estado(db, s, "asignada", usuario, datos.nota or f"Asignada a {recolector.nombre}")
    except FlujoError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    whatsapp_service.notificar_asignada(db, s)
    db.commit()
    db.refresh(s)
    return serializar(s, "operativo")


@router.post("/solicitudes/{solicitud_id}/programar", response_model=SolicitudOut)
def programar(solicitud_id: int, datos: ProgramarIn, usuario: Usuario = Depends(requiere_coordinador),
              db: Session = Depends(get_db)):
    """RN-02: registra día, hora y persona encargada; solo entonces la solicitud pasa a 'programada'."""
    s = _solicitud_del_colectivo(db, usuario, solicitud_id)
    if s.estado != "asignada" or s.asignacion is None:
        raise HTTPException(409, f"Solo se programa una solicitud asignada (estado actual: '{s.estado}').")
    encargado_id = datos.encargado_id or s.asignacion.recolector_id
    if encargado_id != s.asignacion.recolector_id:
        raise HTTPException(422, "La persona encargada debe ser el recolector asignado; reasigna la solicitud para cambiarla.")
    try:
        s.programacion = Programacion(fecha_hora=datos.fecha_hora, encargado_id=encargado_id,
                                      registrado_por_id=usuario.id, nota=datos.nota)
        db.flush()
        cambiar_estado(db, s, "programada", usuario, datos.nota or f"Programada para {datos.fecha_hora:%d/%m/%Y %H:%M}")
    except FlujoError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc
    whatsapp_service.notificar_programada(db, s)
    db.commit()
    db.refresh(s)
    return serializar(s, "operativo")


@router.post("/solicitudes/{solicitud_id}/cancelar", response_model=SolicitudOut)
def cancelar(solicitud_id: int, datos: CancelarIn, usuario: Usuario = Depends(requiere_coordinador),
             db: Session = Depends(get_db)):
    s = _solicitud_del_colectivo(db, usuario, solicitud_id)
    try:
        cambiar_estado(db, s, "cancelada", usuario, datos.motivo or "Cancelada por el coordinador")
    except FlujoError as exc:
        raise HTTPException(409, str(exc)) from exc
    whatsapp_service.notificar_cancelada(db, s, datos.motivo)
    db.commit()
    db.refresh(s)
    return serializar(s, "operativo")
