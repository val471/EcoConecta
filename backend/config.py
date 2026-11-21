"""Configuración leída de variables de entorno (nunca se guardan valores en el código)."""
import os


def _env(nombre: str, defecto: str = "") -> str:
    valor = (os.getenv(nombre) or defecto).strip()
    # "pendiente" es el valor provisional que se escribió en Render mientras llegan las claves reales
    return "" if valor.lower() == "pendiente" else valor


JWT_SECRET = _env("JWT_SECRET") or "cambiar-este-secreto-en-produccion"
TOKEN_HORAS = 24

ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = _env("ANTHROPIC_MODEL") or "claude-haiku-5-5"   # configurable por variable de entorno
WHATSAPP_TOKEN = _env("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = _env("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = _env("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACTIVO = bool(WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID)

# Contraseña de los usuarios de demostración (se puede cambiar con la variable DEMO_PASSWORD)
DEMO_PASSWORD = _env("DEMO_PASSWORD") or "demo123"
