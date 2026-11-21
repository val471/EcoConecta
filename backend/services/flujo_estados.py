"""Cambios de estado válidos y trazables (RN-02, RN-04)."""
from fastapi import HTTPException

from ..constantes import ETIQUETA_ESTADO, TRANSICIONES
from ..models import HistorialEstado


def validar_transicion(actual: str, nuevo: str) -> None:
    if nuevo not in TRANSICIONES.get(actual, []):
        raise HTTPException(
            status_code=409,
            detail=f'No se puede pasar de "{ETIQUETA_ESTADO.get(actual, actual)}" a "{ETIQUETA_ESTADO.get(nuevo, nuevo)}"',
        )


def cambiar_estado(db, solicitud, nuevo: str, por: str, nota: str = "") -> None:
    validar_transicion(solicitud.estado, nuevo)
    solicitud.estado = nuevo
    db.add(HistorialEstado(solicitud_id=solicitud.id, estado=nuevo, por=por, nota=nota[:300]))
