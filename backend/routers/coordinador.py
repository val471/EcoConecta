from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..constantes import ETIQUETA_ESTADO
from ..database import ahora, get_db
from ..models import Asignacion, Programacion, Solicitud, Usuario
from ..schemas import AsignarIn, CancelarIn, ProgramarIn
from ..security.permisos import requiere_roles
from ..services.enrutamiento import flujo_de_coordinador
from ..services.flujo_estados import cambiar_estado
from ..services.serializacion import solicitud_dict, usuario_dict
from ..services.whatsapp_service import notificar

router = APIRouter(prefix="/coordinador", tags=["coordinador"])
solo_coordinador = requiere_roles("coord_huerteros", "coord_recicladores")


def _solicitud(db: Session, codigo: str, u: Usuario) -> Solicitud:
    """Un coordinador solo accede a solicitudes de su flujo (RN-01, RN-07)."""
    s = db.query(Solicitud).filter(Solicitud.codigo == codigo, Solicitud.flujo == flujo_de_coordinador(u)).first()
    if not s:
        raise HTTPException(404, "Solicitud no encontrada")
    return s


@router.get("/bandeja")
def bandeja(estado: Optional[str] = None, db: Session = Depends(get_db), u: Usuario = Depends(solo_coordinador)):
    q = db.query(Solicitud).filter(Solicitud.flujo == flujo_de_coordinador(u))
    if estado == "pendientes":
        q = q.filter(Solicitud.estado.in_(["recibida", "en_revision"]))
    elif estado:
        q = q.filter(Solicitud.estado == estado)
    return [solicitud_dict(s, operativo=True) for s in q.order_by(Solicitud.id.desc()).all()]


@router.get("/resumen")
def resumen(db: Session = Depends(get_db), u: Usuario = Depends(solo_coordinador)):
    flujo = flujo_de_coordinador(u)
    filas = db.query(Solicitud).filter(Solicitud.flujo == flujo).all()
    por_estado = {e: 0 for e in ETIQUETA_ESTADO}
    for s in filas:
        por_estado[s.estado] += 1
    return {"flujo": flujo, "total": len(filas), "por_estado": por_estado}


@router.get("/recolectores")
def recolectores(db: Session = Depends(get_db), u: Usuario = Depends(solo_coordinador)):
    filas = db.query(Usuario).filter(Usuario.rol == "recolector", Usuario.flujo == flujo_de_coordinador(u)).order_by(Usuario.nombre).all()
    return [usuario_dict(r) for r in filas]


@router.post("/solicitudes/{codigo}/asignar")
def asignar(codigo: str, datos: AsignarIn, db: Session = Depends(get_db), u: Usuario = Depends(solo_coordinador)):
    s = _solicitud(db, codigo, u)
    rec = db.query(Usuario).filter(Usuario.id == datos.recolector_id, Usuario.rol == "recolector", Usuario.flujo == s.flujo).first()
    if not rec:
        raise HTTPException(400, "Esa persona no pertenece a tu colectivo")
    if s.estado == "recibida":
        cambiar_estado(db, s, "en_revision", u.nombre, "Revisada por el coordinador")
    cambiar_estado(db, s, "asignada", u.nombre, f"Asignada a {rec.nombre}")        # RN-03
    if s.asignacion:
        s.asignacion.recolector_id, s.asignacion.coordinador_id, s.asignacion.fecha = rec.id, u.id, ahora()
    else:
        db.add(Asignacion(solicitud_id=s.id, coordinador_id=u.id, recolector_id=rec.id))
    db.commit()
    db.refresh(s)
    return solicitud_dict(s, operativo=True)


@router.post("/solicitudes/{codigo}/programar")
def programar(codigo: str, datos: ProgramarIn, db: Session = Depends(get_db), u: Usuario = Depends(solo_coordinador)):
    s = _solicitud(db, codigo, u)
    fecha_txt, hora, persona = (datos.fecha or "").strip(), (datos.hora or "").strip(), (datos.persona or "").strip()
    if not (fecha_txt and hora and persona):                                          # RN-02
        raise HTTPException(400, "Falta día, hora o persona encargada")
    try:
        fecha = date.fromisoformat(fecha_txt)
    except ValueError:
        raise HTTPException(400, "El día no es válido")
    if fecha < date.today() - timedelta(days=1):
        raise HTTPException(400, "Elige un día de hoy en adelante")
    cambiar_estado(db, s, "programada", u.nombre, f"Programada: {fecha.strftime('%d/%m/%Y')}, {hora}, a cargo de {persona}")
    db.add(Programacion(solicitud_id=s.id, fecha=fecha, hora=hora[:20], persona=persona[:120]))
    db.commit()
    db.refresh(s)
    notificar(db, s, f"Tu recolección {s.codigo} quedó programada para el {fecha.strftime('%d/%m/%Y')} a las {hora}. Irá {persona}.")
    db.refresh(s)
    return solicitud_dict(s, operativo=True)


@router.post("/solicitudes/{codigo}/cancelar")
def cancelar(codigo: str, datos: CancelarIn, db: Session = Depends(get_db), u: Usuario = Depends(solo_coordinador)):
    s = _solicitud(db, codigo, u)
    cambiar_estado(db, s, "cancelada", u.nombre, (datos.motivo or "Cancelada").strip() or "Cancelada")
    db.commit()
    db.refresh(s)
    return solicitud_dict(s, operativo=True)
