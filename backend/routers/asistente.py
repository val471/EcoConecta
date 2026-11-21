from fastapi import APIRouter, Depends

from backend.models import Usuario
from backend.schemas.asistente import ClasificacionOut, ClasificarIn, MensajeIn, RespuestaIA
from backend.security.permisos import usuario_actual
from backend.services import ia_service

router = APIRouter(prefix="/api/asistente", tags=["asistente"])


@router.post("/mensaje", response_model=RespuestaIA)
def mensaje(datos: MensajeIn, _: Usuario = Depends(usuario_actual)):
    """Guía conversacional (texto). La voz la produce el navegador con speechSynthesis; no se envía audio a terceros."""
    return ia_service.responder(datos.mensaje, [t.model_dump() for t in datos.historial])


@router.post("/clasificar", response_model=ClasificacionOut)
def clasificar(datos: ClasificarIn, _: Usuario = Depends(usuario_actual)):
    """Sugerencia orientativa de tipo de residuo. El usuario siempre confirma el tipo."""
    return ia_service.clasificar(datos.descripcion)
