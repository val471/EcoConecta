"""Contraseñas con PBKDF2 (biblioteca estándar de Python, sin dependencias extra)."""
import hashlib
import hmac
import os

ITERACIONES = 120_000


def hash_password(password: str) -> str:
    sal = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, ITERACIONES)
    return f"pbkdf2${ITERACIONES}${sal.hex()}${dk.hex()}"


def verificar_password(password: str, guardado: str) -> bool:
    try:
        _, iteraciones, sal, esperado = guardado.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(sal), int(iteraciones))
        return hmac.compare_digest(dk.hex(), esperado)
    except Exception:
        return False
