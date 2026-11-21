from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.config import settings
from backend.constantes import (AVISO_PUNTOS, COLECTIVO_POR_ROL_COORD, ROL_RECOLECTOR, ROL_SOLICITANTE, ROLES_COORDINADOR)
from backend.database import get_db
from backend.models import Notificacion, Puntos, ReglaPuntos, Solicitud, Usuario
from backend.schemas.admin import (NotificacionOut, ReglaIn, ReglaOut, ReglaUpdate, UsuarioAdminOut, UsuarioCrear,
                                   UsuarioUpdate)
from backend.schemas.solicitud import SolicitudOut
from backend.security import passwords
from backend.security.permisos import requiere_admin
from backend.services import whatsapp_service
from backend.services.serializadores import serializar

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(requiere_admin)])


def _regla_out(r: ReglaPuntos) -> ReglaOut:
    return ReglaOut(id=r.id, tipo_residuo=r.tipo_residuo, unidad=r.unidad, puntos_por_unidad=r.puntos_por_unidad,
                    descripcion=r.descripcion, activa=r.activa, aviso=AVISO_PUNTOS)


@router.get("/resumen")
def resumen(db: Session = Depends(get_db)):
    por_estado = {e: n for e, n in db.execute(select(Solicitud.estado, func.count()).group_by(Solicitud.estado)).all()}
    por_colectivo = {c: n for c, n in db.execute(select(Solicitud.colectivo, func.count()).group_by(Solicitud.colectivo)).all()}
    por_rol = {r: n for r, n in db.execute(select(Usuario.rol, func.count()).group_by(Usuario.rol)).all()}
    total_puntos = int(db.scalar(select(func.coalesce(func.sum(Puntos.puntos), 0))) or 0)
    return {"solicitudes_por_estado": por_estado, "solicitudes_por_colectivo": por_colectivo,
            "usuarios_por_rol": por_rol, "puntos_otorgados": total_puntos, "aviso_puntos": AVISO_PUNTOS}


@router.get("/configuracion")
def configuracion():
    return {
        "solo_usuarios_piloto": settings.SOLO_USUARIOS_PILOTO,
        "whatsapp": "real" if whatsapp_service.modo_real() else "simulado",
        "ia": "claude" if settings.ANTHROPIC_API_KEY else "local",
        "aviso_puntos": AVISO_PUNTOS,
    }


@router.get("/solicitudes", response_model=list[SolicitudOut])
def solicitudes(estado: str | None = None, db: Session = Depends(get_db)):
    """Vista del administrador: sin teléfono ni dirección de contacto (RN-07)."""
    consulta = select(Solicitud).order_by(Solicitud.id.desc())
    if estado:
        consulta = consulta.where(Solicitud.estado == estado)
    return [serializar(s, "admin") for s in db.scalars(consulta).all()]


# ---------- reglas de puntos (RN-06) ----------
@router.get("/reglas", response_model=list[ReglaOut])
def listar_reglas(db: Session = Depends(get_db)):
    return [_regla_out(r) for r in db.scalars(select(ReglaPuntos).order_by(ReglaPuntos.id)).all()]


@router.post("/reglas", response_model=ReglaOut, status_code=201)
def crear_regla(datos: ReglaIn, db: Session = Depends(get_db)):
    r = ReglaPuntos(tipo_residuo=datos.tipo_residuo, unidad=datos.unidad.strip().lower(),
                    puntos_por_unidad=datos.puntos_por_unidad, descripcion=datos.descripcion, activa=datos.activa)
    db.add(r)
    db.commit()
    db.refresh(r)
    return _regla_out(r)


@router.put("/reglas/{regla_id}", response_model=ReglaOut)
def actualizar_regla(regla_id: int, datos: ReglaUpdate, db: Session = Depends(get_db)):
    r = db.get(ReglaPuntos, regla_id)
    if r is None:
        raise HTTPException(404, "Regla no encontrada.")
    cambios = datos.model_dump(exclude_unset=True)
    if "unidad" in cambios and cambios["unidad"]:
        cambios["unidad"] = cambios["unidad"].strip().lower()
    for campo, valor in cambios.items():
        setattr(r, campo, valor)
    db.commit()
    db.refresh(r)
    return _regla_out(r)


# ---------- usuarios (RN-08: usuarios piloto) ----------
@router.get("/usuarios", response_model=list[UsuarioAdminOut])
def listar_usuarios(rol: str | None = None, db: Session = Depends(get_db)):
    consulta = select(Usuario).order_by(Usuario.id)
    if rol:
        consulta = consulta.where(Usuario.rol == rol)
    return db.scalars(consulta).all()


@router.post("/usuarios", response_model=UsuarioAdminOut, status_code=201)
def crear_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    email = datos.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(409, "Ya existe una cuenta con ese correo.")
    colectivo = datos.colectivo
    if datos.rol in ROLES_COORDINADOR:
        colectivo = COLECTIVO_POR_ROL_COORD[datos.rol]
    if datos.rol == ROL_RECOLECTOR and colectivo is None:
        raise HTTPException(422, "El recolector necesita un colectivo (huerteros o recicladores).")
    tipo = datos.tipo_solicitante if datos.rol == ROL_SOLICITANTE else None
    u = Usuario(nombre=datos.nombre.strip(), email=email, telefono=datos.telefono, direccion=datos.direccion,
                password_hash=passwords.hashear(datos.password), rol=datos.rol, colectivo=colectivo,
                tipo_solicitante=tipo, es_piloto=datos.es_piloto)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioAdminOut)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    u = db.get(Usuario, usuario_id)
    if u is None:
        raise HTTPException(404, "Usuario no encontrado.")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(u, campo, valor)
    db.commit()
    db.refresh(u)
    return u


# ---------- mensajes de WhatsApp (incluye los simulados) ----------
@router.get("/notificaciones", response_model=list[NotificacionOut])
def notificaciones(solicitud_id: int | None = None, limite: int = 50, db: Session = Depends(get_db)):
    consulta = select(Notificacion).order_by(Notificacion.id.desc()).limit(min(max(limite, 1), 200))
    if solicitud_id:
        consulta = consulta.where(Notificacion.solicitud_id == solicitud_id)
    return [NotificacionOut(id=n.id, solicitud_id=n.solicitud_id, direccion=n.direccion, mensaje=n.mensaje,
                            estado=n.estado, detalle=n.detalle, creado_en=n.creado_en)
            for n in db.scalars(consulta).all()]
