from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SolicitudCrear(BaseModel):
    tipo_residuo: Literal["organico", "reciclable"]
    descripcion: str = Field(min_length=3, max_length=1000)
    cantidad_estimada: float | None = Field(default=None, gt=0)
    unidad_estimada: str | None = Field(default=None, max_length=20)
    direccion: str | None = Field(default=None, max_length=200)


class HistorialOut(BaseModel):
    estado_anterior: str | None
    estado_nuevo: str
    nota: str | None
    fecha: datetime
    por: str | None = None


class ProgramacionOut(BaseModel):
    fecha_hora: datetime
    encargado_id: int
    encargado_nombre: str


class RecoleccionOut(BaseModel):
    cantidad: float
    unidad: str
    observaciones: str | None
    fecha: datetime


class PuntosOut(BaseModel):
    puntos: int
    explicacion: str


class SolicitudOut(BaseModel):
    id: int
    codigo: str | None
    tipo_residuo: str
    colectivo: str
    descripcion: str
    cantidad_estimada: float | None
    unidad_estimada: str | None
    estado: str
    creado_en: datetime
    historial: list[HistorialOut] = []
    coordinador_nombre: str | None = None
    recolector_nombre: str | None = None
    programacion: ProgramacionOut | None = None
    recoleccion: RecoleccionOut | None = None
    puntos: PuntosOut | None = None
    # RN-07: solo se llenan para quien atiende la solicitud (o el dueño, su propia dirección)
    solicitante_nombre: str | None = None
    contacto_telefono: str | None = None
    direccion: str | None = None


class AsignarIn(BaseModel):
    recolector_id: int
    nota: str | None = Field(default=None, max_length=500)


class ProgramarIn(BaseModel):
    fecha_hora: datetime
    encargado_id: int | None = None  # por defecto, el recolector asignado
    nota: str | None = Field(default=None, max_length=500)


class CancelarIn(BaseModel):
    motivo: str | None = Field(default=None, max_length=500)


class RevisarIn(BaseModel):
    nota: str | None = Field(default=None, max_length=500)


class RecoleccionIn(BaseModel):
    cantidad: float = Field(gt=0)
    unidad: str = Field(default="kg", min_length=1, max_length=20)
    observaciones: str | None = Field(default=None, max_length=500)


class RecolectorPublico(BaseModel):
    id: int
    nombre: str
    colectivo: str | None
