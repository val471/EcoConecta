"""Token firmado con HMAC-SHA256 (usuario + vencimiento). Sin dependencias extra."""
import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from ..config import JWT_SECRET, TOKEN_HORAS


def _b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def _des64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def _firma(cuerpo: str) -> str:
    return _b64(hmac.new(JWT_SECRET.encode(), cuerpo.encode(), hashlib.sha256).digest())


def crear_token(usuario_id: int, horas: int = TOKEN_HORAS) -> str:
    cuerpo = _b64(json.dumps({"uid": usuario_id, "exp": int(time.time()) + horas * 3600}).encode())
    return f"{cuerpo}.{_firma(cuerpo)}"


def leer_token(token: str) -> Optional[int]:
    """Devuelve el id del usuario si el token es válido y no ha vencido."""
    try:
        cuerpo, firma = token.split(".")
        if not hmac.compare_digest(firma, _firma(cuerpo)):
            return None
        datos = json.loads(_des64(cuerpo))
        return int(datos["uid"]) if datos["exp"] > time.time() else None
    except Exception:
        return None
