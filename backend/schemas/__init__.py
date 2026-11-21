"""Datos de entrada de la API. Se validan a mano en los routers para dar mensajes claros en español."""
from typing import List, Optional

from pydantic import BaseModel


class LoginIn(BaseModel):
    email: str = ""
    password: str = ""


class SolicitudIn(BaseModel):
    flujo: str = ""
    tipo_generador: str = ""
    direccion: str = ""
    contacto: str = ""
    observaciones: Optional[str] = ""
    preferencia_horaria: Optional[str] = ""


class AsignarIn(BaseModel):
    recolector_id: int


class ProgramarIn(BaseModel):
    fecha: Optional[str] = ""
    hora: Optional[str] = ""
    persona: Optional[str] = ""


class CancelarIn(BaseModel):
    motivo: Optional[str] = ""


class RecoleccionIn(BaseModel):
    tipo_residuo: str = ""
    cantidad: float = 0
    unidad: str = "kg"


class ReglaIn(BaseModel):
    tipo_residuo: str
    unidad: str = "kg"
    puntos_por_unidad: float


class PilotoIn(BaseModel):
    es_piloto: bool


class TurnoIn(BaseModel):
    rol: str = ""        # "usuario" | "asistente"
    texto: str = ""


class AsistenteIn(BaseModel):
    mensaje: str = ""
    historial: List[TurnoIn] = []
