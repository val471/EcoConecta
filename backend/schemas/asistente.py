from typing import Literal

from pydantic import BaseModel, Field


class TurnoChat(BaseModel):
    rol: Literal["usuario", "asistente"]
    texto: str = Field(max_length=2000)


class MensajeIn(BaseModel):
    mensaje: str = Field(min_length=1, max_length=1000)
    historial: list[TurnoChat] = Field(default_factory=list, max_length=12)


class ClasificarIn(BaseModel):
    descripcion: str = Field(min_length=3, max_length=1000)


class RespuestaIA(BaseModel):
    respuesta: str
    modo: str  # "claude" | "local"
    aviso: str


class ClasificacionOut(BaseModel):
    tipo_sugerido: str  # organico | reciclable | indefinido
    colectivo_sugerido: str | None
    motivo: str
    modo: str
    aviso: str
