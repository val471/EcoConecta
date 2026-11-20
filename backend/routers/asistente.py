"""Endpoints del asistente con IA. 

- POST /api/asistente/chat        -> responde una pregunta (guía conversacional)
- POST /api/asistente/clasificar  -> sugerencia ORIENTATIVA de tipo de residuo

La IA solo orienta. No asigna, programa ni cierra solicitudes (eso lo hace
una persona). Los textos se limpian de datos personales en ia_service.
"""
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.services import ia_service

router = APIRouter(prefix="/api/asistente", tags=["asistente"])

# --- Límite simple por IP: protege el saldo de la API de abusos -------------
MAX_PETICIONES = 20      # peticiones permitidas...
VENTANA_SEGUNDOS = 60    # ...por cada minuto
_registro: dict[str, deque] = defaultdict(deque)


def _limitar(request: Request) -> None:
    # En Render la IP real llega en X-Forwarded-For
    reenviado = request.headers.get("x-forwarded-for", "")
    ip = reenviado.split(",")[0].strip() or (request.client.host if request.client else "?")
    ahora = time.monotonic()
    cola = _registro[ip]
    while cola and ahora - cola[0] > VENTANA_SEGUNDOS:
        cola.popleft()
    if len(cola) >= MAX_PETICIONES:
        raise HTTPException(status_code=429, detail="Demasiadas preguntas seguidas. Espera un momento.")
    cola.append(ahora)


# --- Esquemas de entrada ----------------------------------------------------
class Turno(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(max_length=1000)


class PreguntaIn(BaseModel):
    pregunta: str = Field(min_length=1, max_length=500)
    historial: list[Turno] = Field(default_factory=list, max_length=10)


class ClasificarIn(BaseModel):
    descripcion: str = Field(min_length=1, max_length=500)


# --- Endpoints ---------------------------------------------------------------
# Se definen con "def" (no "async def") porque el cliente de Anthropic es
# síncrono: FastAPI los corre en un hilo aparte y no bloquea el servidor.
@router.post("/chat")
def chat(datos: PreguntaIn, request: Request):
    _limitar(request)
    historial = [t.model_dump() for t in datos.historial]
    respuesta = ia_service.guia(datos.pregunta, historial)
    return {
        "respuesta": respuesta,
        # True si la IA no pudo responder y se mostró el mensaje de respaldo
        "respaldo": respuesta == ia_service.MENSAJE_RESPALDO,
    }


@router.post("/clasificar")
def clasificar(datos: ClasificarIn, request: Request):
    _limitar(request)
    # Orientativo: el tipo final lo confirma la persona y lo revisa el coordinador (RN-01)
    return ia_service.clasificar(datos.descripcion)