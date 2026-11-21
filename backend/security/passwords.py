import base64
import hashlib
import hmac
import os

_ITERACIONES = 200_000


def hashear(password: str) -> str:
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, _ITERACIONES)
    return f"pbkdf2${_ITERACIONES}${base64.b64encode(sal).decode()}${base64.b64encode(h).decode()}"


def verificar(password: str, guardado: str) -> bool:
    try:
        _, iters, sal_b64, hash_b64 = guardado.split("$")
        sal = base64.b64decode(sal_b64)
        esperado = base64.b64decode(hash_b64)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, int(iters))
        return hmac.compare_digest(h, esperado)
    except Exception:
        return False
