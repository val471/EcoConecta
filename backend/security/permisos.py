"""Control de acceso por rol (RN-07)."""
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from .tokens import leer_token


def usuario_actual(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)) -> Usuario:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Debes iniciar sesión")
    uid = leer_token(authorization[7:].strip())
    usuario = db.query(Usuario).filter(Usuario.id == uid).first() if uid else None
    if not usuario:
        raise HTTPException(status_code=401, detail="Sesión vencida")
    return usuario


def requiere_roles(*roles: str):
    def dependencia(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")
        return usuario
    return dependencia
