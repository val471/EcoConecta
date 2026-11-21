from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class LoginIn(BaseModel):
    email: str = Field(pattern=EMAIL_RE)
    password: str = Field(min_length=1)


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=EMAIL_RE, max_length=160)
    password: str = Field(min_length=8, max_length=100)
    telefono: str | None = Field(default=None, max_length=30)
    direccion: str | None = Field(default=None, max_length=200)
    tipo_solicitante: Literal["hogar", "unidad_productiva"] = "hogar"


class UsuarioMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    rol: str
    colectivo: str | None = None
    tipo_solicitante: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    es_piloto: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioMe
