import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..constantes import FLUJOS, TIPOS_GENERADOR
from ..database import get_db
from ..models import HistorialEstado, MovimientoPuntos, Solicitud, Usuario
from ..schemas import SolicitudIn
from ..security.permisos import requiere_roles
from ..services.serializacion import iso, solicitud_dict
from ..services.whatsapp_service import notificar

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])
solo_solicitante = requiere_roles("solicitante")


@router.post("")
def crear(datos: SolicitudIn, db: Session = Depends(get_db), u: Usuario = Depends(solo_solicitante)):
    # RN-08: solo usuarios piloto habilitados
    if not u.es_piloto:
        raise HTTPException(403, "Tu cuenta todavía no está habilitada para solicitar recolecciones. Habla con el administrador.")
    if datos.flujo not in FLUJOS:
        raise HTTPException(400, "Elige si tus residuos son orgánicos o reciclables")
    if datos.tipo_generador not in TIPOS_GENERADOR:
        raise HTTPException(400, "Elige el tipo de lugar")
    direccion = datos.direccion.strip()
    if len(direccion) < 5:
        raise HTTPException(400, "Escribe tu dirección completa")
    contacto = datos.contacto.strip()
    if not re.fullmatch(r"3\d{9}", contacto):
        raise HTTPException(400, "Escribe un celular de 10 números, empezando por 3")

    s = Solicitud(
        usuario_id=u.id, flujo=datos.flujo,                 # RN-01: el flujo define el coordinador
        tipo_generador=datos.tipo_generador, direccion=direccion[:200], contacto=contacto,
        observaciones=(datos.observaciones or "").strip()[:300],
        preferencia_horaria=(datos.preferencia_horaria or "").strip()[:60], estado="recibida",
    )
    db.add(s)
    db.flush()
    s.codigo = f"SOL-{s.id:04d}"
    db.add(HistorialEstado(solicitud_id=s.id, estado="recibida", por=u.nombre, nota="Solicitud registrada"))  # RN-04
    db.commit()
    db.refresh(s)
    notificar(db, s, f"Recibimos tu solicitud {s.codigo}. Un coordinador la revisará y te dirá el día, la hora y la persona que irá.")
    db.refresh(s)
    return solicitud_dict(s)


# OJO: /mias y /puntos van ANTES de /{codigo}, o FastAPI los confunde con un código
@router.get("/mias")
def mias(db: Session = Depends(get_db), u: Usuario = Depends(solo_solicitante)):
    filas = db.query(Solicitud).filter(Solicitud.usuario_id == u.id).order_by(Solicitud.id.desc()).all()
    return [solicitud_dict(s) for s in filas]


@router.get("/puntos")
def puntos(db: Session = Depends(get_db), u: Usuario = Depends(solo_solicitante)):
    movs = db.query(MovimientoPuntos).filter(MovimientoPuntos.usuario_id == u.id).order_by(MovimientoPuntos.id.desc()).all()
    return {
        "total": sum(m.puntos for m in movs),
        "movimientos": [{"solicitud_id": m.solicitud_id, "puntos": m.puntos, "explicacion": m.explicacion,
                         "fecha": iso(m.fecha)} for m in movs],
    }


@router.get("/{codigo}")
def detalle(codigo: str, db: Session = Depends(get_db), u: Usuario = Depends(solo_solicitante)):
    s = db.query(Solicitud).filter(Solicitud.codigo == codigo, Solicitud.usuario_id == u.id).first()
    if not s:
        raise HTTPException(404, "Solicitud no encontrada")      # RN-07: no se revela que existe
    return solicitud_dict(s)
