from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..constantes import TIPOS_RESIDUO
from ..database import get_db
from ..models import ReglaPuntos, Usuario
from ..schemas import PilotoIn, ReglaIn
from ..security.permisos import requiere_roles
from ..services.serializacion import usuario_dict

router = APIRouter(prefix="/admin", tags=["admin"])
solo_admin = requiere_roles("admin")


def _reglas(db: Session):
    return [{"tipo_residuo": r.tipo_residuo, "unidad": r.unidad, "puntos_por_unidad": float(r.puntos_por_unidad)}
            for r in db.query(ReglaPuntos).order_by(ReglaPuntos.id).all()]


@router.get("/reglas-puntos")
def ver_reglas(db: Session = Depends(get_db), u: Usuario = Depends(solo_admin)):
    return _reglas(db)


@router.put("/reglas-puntos")
def guardar_reglas(datos: List[ReglaIn], db: Session = Depends(get_db), u: Usuario = Depends(solo_admin)):
    for r in datos:
        if r.tipo_residuo not in TIPOS_RESIDUO or r.unidad != "kg" or not (0 <= r.puntos_por_unidad <= 1000):
            raise HTTPException(400, "Revisa los puntos: deben ser un número de 0 a 1000")
    for r in datos:
        valor = Decimal(str(r.puntos_por_unidad)).quantize(Decimal("0.01"))
        regla = db.query(ReglaPuntos).filter(ReglaPuntos.tipo_residuo == r.tipo_residuo, ReglaPuntos.unidad == r.unidad).first()
        if regla:
            regla.puntos_por_unidad = valor
        else:
            db.add(ReglaPuntos(tipo_residuo=r.tipo_residuo, unidad=r.unidad, puntos_por_unidad=valor))
    db.commit()
    return _reglas(db)


@router.get("/usuarios")
def usuarios(db: Session = Depends(get_db), u: Usuario = Depends(solo_admin)):
    return [usuario_dict(x) for x in db.query(Usuario).order_by(Usuario.id).all()]


@router.patch("/usuarios/{usuario_id}/piloto")
def cambiar_piloto(usuario_id: int, datos: PilotoIn, db: Session = Depends(get_db), u: Usuario = Depends(solo_admin)):
    objetivo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not objetivo:
        raise HTTPException(404, "Usuario no encontrado")
    objetivo.es_piloto = datos.es_piloto
    db.commit()
    return usuario_dict(objetivo)
