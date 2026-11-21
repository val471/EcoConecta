from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Contenido
from backend.schemas.contenido import ContenidoOut

router = APIRouter(prefix="/api/contenidos", tags=["contenidos"])


@router.get("", response_model=list[ContenidoOut])
def listar(categoria: str | None = None, db: Session = Depends(get_db)):
    consulta = select(Contenido).where(Contenido.publicado.is_(True)).order_by(Contenido.id)
    if categoria:
        consulta = consulta.where(Contenido.categoria == categoria)
    return db.scalars(consulta).all()


@router.get("/{contenido_id}", response_model=ContenidoOut)
def detalle(contenido_id: int, db: Session = Depends(get_db)):
    c = db.get(Contenido, contenido_id)
    if c is None or not c.publicado:
        raise HTTPException(404, "Contenido no encontrado.")
    return c
