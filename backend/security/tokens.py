import base64
import hashlib
import hmac
import json
import os
import time

from backend.config import settings


# Duración del token: 8 horas
DURACION_TOKEN = 8 * 60 * 60


def _clave_secreta():
    clave = getattr(settings, "SECRET_KEY", "")
    if not clave:
        raise RuntimeError("Falta configurar SECRET_KEY en el archivo .env")
    return clave.encode("utf-8")


def crear_token(usuario_id: int, rol: str) -> str:
    datos = {
        "sub": usuario_id,
        "rol": rol,
        "exp": int(time.time()) + DURACION_TOKEN
    }

    contenido = base64.urlsafe_b64encode(
        json.dumps(datos).encode("utf-8")
    ).rstrip(b"=")

    firma = hmac.new(
        _clave_secreta(),
        contenido,
        hashlib.sha256
    ).digest()

    firma_codificada = base64.urlsafe_b64encode(firma).rstrip(b"=")

    return (
        contenido.decode("utf-8")
        + "."
        + firma_codificada.decode("utf-8")
    )


def verificar_token(token: str) -> dict | None:
    try:
        contenido, firma_recibida = token.split(".")

        contenido_bytes = contenido.encode("utf-8")

        firma_esperada = hmac.new(
            _clave_secreta(),
            contenido_bytes,
            hashlib.sha256
        ).digest()

        firma_recibida_bytes = base64.urlsafe_b64decode(
            firma_recibida + "=" * (-len(firma_recibida) % 4)
        )

        if not hmac.compare_digest(
            firma_esperada,
            firma_recibida_bytes
        ):
            return None

        datos_bytes = base64.urlsafe_b64decode(
            contenido + "=" * (-len(contenido) % 4)
        )

        datos = json.loads(datos_bytes)

        if datos.get("exp", 0) < time.time():
            return None

        return datos

    except Exception:
        return None