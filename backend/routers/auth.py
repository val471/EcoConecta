from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import settings
from backend.constantes import ROL_SOLICITANTE
from backend.database import get_db
from backend.models import Usuario
from backend.schemas.auth import LoginIn, RegistroIn, TokenOut, UsuarioMe
from backend.security import passwords
from backend.security.permisos import usuario_actual
from backend.security.tokens import crear_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.email == datos.email.lower()))
    if usuario is None or not usuario.activo or not passwords.verificar(datos.password, usuario.password_hash):
        raise HTTPException(401, "Correo o contraseña incorrectos.")
    return TokenOut(access_token=crear_token(usuario.id, usuario.rol), usuario=UsuarioMe.model_validate(usuario))


@router.post("/registro", response_model=TokenOut, status_code=201)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    """Registro público: solo crea usuarios con rol solicitante."""
    email = datos.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(409, "Ya existe una cuenta con ese correo.")
    usuario = Usuario(
        nombre=datos.nombre.strip(), email=email, telefono=datos.telefono, direccion=datos.direccion,
        password_hash=passwords.hashear(datos.password), rol=ROL_SOLICITANTE,
        tipo_solicitante=datos.tipo_solicitante,
        es_piloto=not settings.SOLO_USUARIOS_PILOTO,  # RN-08: con modo piloto activo, el admin debe habilitarlos
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return TokenOut(access_token=crear_token(usuario.id, usuario.rol), usuario=UsuarioMe.model_validate(usuario))


@router.get("/me", response_model=UsuarioMe)
def me(usuario: Usuario = Depends(usuario_actual)):
    return usuario
