from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.auth import EMAIL_RE


class ReglaIn(BaseModel):
    tipo_residuo: Literal["organico", "reciclable"]
    unidad: str = Field(min_length=1, max_length=20)
    puntos_por_unidad: float = Field(ge=0)
    descripcion: str | None = Field(default=None, max_length=300)
    activa: bool = True


class ReglaUpdate(BaseModel):
    unidad: str | None = Field(default=None, min_length=1, max_length=20)
    puntos_por_unidad: float | None = Field(default=None, ge=0)
    descripcion: str | None = Field(default=None, max_length=300)
    activa: bool | None = None


class ReglaOut(BaseModel):
    id: int
    tipo_residuo: str
    unidad: str
    puntos_por_unidad: float
    descripcion: str | None
    activa: bool
    aviso: str


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=EMAIL_RE, max_length=160)
    password: str = Field(min_length=8, max_length=100)
    rol: Literal["solicitante", "coordinador_huerteros", "coordinador_recicladores", "recolector", "administrador"]
    colectivo: Literal["huerteros", "recicladores"] | None = None  # obligatorio para recolector
    tipo_solicitante: Literal["hogar", "unidad_productiva"] | None = None
    telefono: str | None = Field(default=None, max_length=30)
    direccion: str | None = Field(default=None, max_length=200)
    es_piloto: bool = False


class UsuarioUpdate(BaseModel):
    es_piloto: bool | None = None  # RN-08
    activo: bool | None = None
    nombre: str | None = Field(default=None, min_length=2, max_length=120)


class UsuarioAdminOut(BaseModel):
    """El administrador no ve teléfono ni dirección (RN-07)."""

    id: int
    nombre: str
    email: str
    rol: str
    colectivo: str | None
    tipo_solicitante: str | None
    es_piloto: bool
    activo: bool


class NotificacionOut(BaseModel):
    id: int
    solicitud_id: int | None
    direccion: str
    mensaje: str
    estado: str
    detalle: str | None
    creado_en: datetime
