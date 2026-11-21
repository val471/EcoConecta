import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request

from ..schemas import AsistenteIn
from ..services.ia_service import responder

router = APIRouter(prefix="/asistente", tags=["asistente"])

# Límite sencillo por IP: el asistente es público y cada pregunta puede costar
_visitas = defaultdict(deque)
LIMITE, VENTANA = 15, 60


def _permitido(ip: str) -> bool:
    ahora, cola = time.time(), _visitas[ip]
    while cola and ahora - cola[0] > VENTANA:
        cola.popleft()
    if len(cola) >= LIMITE:
        return False
    cola.append(ahora)
    return True


@router.post("")
def preguntar(datos: AsistenteIn, request: Request):
    """Orienta sobre residuos. Solo sugiere: nunca crea, asigna ni programa solicitudes."""
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "?")).split(",")[0].strip()
    if not _permitido(ip):
        raise HTTPException(429, "Hiciste muchas preguntas seguidas. Espera un minuto e inténtalo de nuevo.")
    mensaje = datos.mensaje.strip()
    if not mensaje:
        raise HTTPException(400, "Escribe tu pregunta")
    historial = [{"rol": h.rol, "texto": h.texto} for h in datos.historial]
    return responder(mensaje, historial)
