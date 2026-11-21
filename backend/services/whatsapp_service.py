"""Notificaciones por WhatsApp Business Cloud API.
Si no hay credenciales configuradas, el mensaje queda registrado como SIMULADO (se declara así en la sustentación)."""
import json
import urllib.request

from ..config import WHATSAPP_ACTIVO, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_TOKEN
from ..models import Notificacion


def _enviar(telefono: str, mensaje: str) -> bool:
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    cuerpo = json.dumps({
        "messaging_product": "whatsapp", "to": "57" + telefono,
        "type": "text", "text": {"body": mensaje},
    }).encode()
    req = urllib.request.Request(url, data=cuerpo, method="POST", headers={
        "Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return 200 <= r.status < 300


def notificar(db, solicitud, mensaje: str) -> None:
    """Nunca debe romper la operación principal: cualquier fallo solo se registra."""
    try:
        estado = "simulada"
        if WHATSAPP_ACTIVO:
            try:
                estado = "enviada" if _enviar(solicitud.contacto, mensaje) else "error"
            except Exception:
                estado = "error"
        db.add(Notificacion(solicitud_id=solicitud.id, canal="whatsapp", mensaje=mensaje[:500], estado=estado))
        db.commit()
    except Exception:
        db.rollback()
