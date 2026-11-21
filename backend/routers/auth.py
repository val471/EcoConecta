from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginIn
from ..security.passwords import verificar_password
from ..security.tokens import crear_token
from ..services.serializacion import usuario_dict

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(datos: LoginIn, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email.strip().lower()).first()
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return {"token": crear_token(usuario.id), "usuario": usuario_dict(usuario)}
