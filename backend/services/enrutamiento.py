"""RN-01: cada solicitud es orgánica o reciclable y llega al colectivo correcto."""
from backend.constantes import COLECTIVO_POR_TIPO


class EnrutamientoError(ValueError):
    pass


def colectivo_para(tipo_residuo: str) -> str:
    try:
        return COLECTIVO_POR_TIPO[tipo_residuo]
    except KeyError:
        raise EnrutamientoError(f"Tipo de residuo no válido: {tipo_residuo!r}") from None
