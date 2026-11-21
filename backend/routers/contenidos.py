from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Contenido

router = APIRouter(prefix="/contenidos", tags=["contenidos"])


@router.get("")
def listar(categoria: Optional[str] = None, db: Session = Depends(get_db)):
    """Público: la educación ambiental se consulta sin iniciar sesión."""
    q = db.query(Contenido).filter(Contenido.publicado.is_(True))
    if categoria:
        q = q.filter(Contenido.categoria == categoria)
    return [{"id": c.id, "categoria": c.categoria, "titulo": c.titulo, "resumen": c.resumen, "cuerpo": c.cuerpo}
            for c in q.order_by(Contenido.orden, Contenido.id).all()]
