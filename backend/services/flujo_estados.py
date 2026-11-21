"""RN-02, RN-03, RN-04: máquina de estados con historial y precondiciones."""
from sqlalchemy.orm import Session

from backend.constantes import ESTADOS
from backend.models import HistorialEstado, Solicitud, Usuario


class FlujoError(Exception):
    """Operación no permitida por las reglas del flujo (se responde 409)."""


TRANSICIONES: dict[str, set[str]] = {
    "recibida": {"en_revision", "cancelada"},
    "en_revision": {"asignada", "cancelada"},
    "asignada": {"programada", "cancelada"},
    "programada": {"recolectada", "cancelada"},
    "recolectada": set(),
    "cancelada": set(),
}


def _validar_precondiciones(s: Solicitud, nuevo: str) -> None:
    if nuevo == "asignada":  # RN-03
        a = s.asignacion
        if a is None or not a.coordinador_id or not a.recolector_id:
            raise FlujoError("RN-03: la asignación requiere coordinador y recolector.")
    if nuevo == "programada":  # RN-02
        p = s.programacion
        if p is None or p.fecha_hora is None or not p.encargado_id:
            raise FlujoError("RN-02: no está programada hasta registrar día, hora y persona encargada.")
    if nuevo == "recolectada":
        if s.recoleccion is None:
            raise FlujoError("Debe registrarse la recolección antes de marcarla como recolectada.")


def cambiar_estado(db: Session, solicitud: Solicitud, nuevo: str, usuario: Usuario | None, nota: str | None = None) -> None:
    actual = solicitud.estado
    if nuevo not in ESTADOS:
        raise FlujoError(f"Estado desconocido: {nuevo!r}")
    if nuevo not in TRANSICIONES.get(actual, set()):
        raise FlujoError(f"No se puede pasar de '{actual}' a '{nuevo}'.")
    _validar_precondiciones(solicitud, nuevo)
    solicitud.estado = nuevo
    # RN-04: cada cambio guarda una fila en el historial
    db.add(
        HistorialEstado(
            solicitud_id=solicitud.id,
            estado_anterior=actual,
            estado_nuevo=nuevo,
            usuario_id=usuario.id if usuario else None,
            nota=nota,
        )
    )
    db.flush()
