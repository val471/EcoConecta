"""Autenticación Bearer y permisos por rol. RN-07: contacto y ubicación solo para quien atiende."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.constantes import (COLECTIVO_POR_ROL_COORD, ROL_ADMIN, ROL_COORD_HUERTEROS, ROL_COORD_RECICLADORES,
                                ROL_RECOLECTOR, ROL_SOLICITANTE, ROLES_COORDINADOR)
from backend.database import get_db
from backend.models import Solicitud, Usuario
from backend.security.tokens import verificar_token

_bearer = HTTPBearer(auto_error=False)


def usuario_actual(cred: HTTPAuthorizationCredentials | None = Depends(_bearer), db: Session = Depends(get_db)) -> Usuario:
    if cred is None:
        raise HTTPException(401, "Falta el token de autenticación.")
    datos = verificar_token(cred.credentials)
    if not datos:
        raise HTTPException(401, "Token inválido o vencido.")
    usuario = db.get(Usuario, datos["sub"])
    if usuario is None or not usuario.activo:
        raise HTTPException(401, "Usuario no válido.")
    return usuario


def requiere_roles(*roles: str):
    def dependencia(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(403, "No tienes permiso para esta acción.")
        return usuario

    return dependencia


requiere_solicitante = requiere_roles(ROL_SOLICITANTE)
requiere_coordinador = requiere_roles(ROL_COORD_HUERTEROS, ROL_COORD_RECICLADORES)
requiere_recolector = requiere_roles(ROL_RECOLECTOR)
requiere_admin = requiere_roles(ROL_ADMIN)


def colectivo_de(usuario: Usuario) -> str | None:
    if usuario.rol in ROLES_COORDINADOR:
        return COLECTIVO_POR_ROL_COORD[usuario.rol]
    return usuario.colectivo


def modo_para(usuario: Usuario, s: Solicitud) -> str | None:
    """Devuelve cómo puede ver `usuario` la solicitud: 'propio', 'operativo' (contacto y dirección) o 'admin'."""
    if usuario.rol == ROL_SOLICITANTE:
        return "propio" if s.solicitante_id == usuario.id else None
    if usuario.rol in ROLES_COORDINADOR:
        return "operativo" if colectivo_de(usuario) == s.colectivo else None
    if usuario.rol == ROL_RECOLECTOR:
        a = s.asignacion
        return "operativo" if a is not None and a.recolector_id == usuario.id else None
    if usuario.rol == ROL_ADMIN:
        return "admin"
    return None
