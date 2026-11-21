"""WhatsApp Business Cloud API, con modo simulado si Meta no ha aprobado la cuenta.

En modo simulado el mensaje NO se envía: se guarda en la tabla `notificaciones` con estado 'simulada'
y el administrador puede verlo en pantalla (GET /api/admin/notificaciones). Declarar esto en la sustentación.
"""
import logging
import re

import httpx
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import Notificacion, Solicitud, Usuario

log = logging.getLogger("ecoconecta.whatsapp")
GRAPH_URL = "https://graph.facebook.com/v20.0"


def modo_real() -> bool:
    return bool(settings.WHATSAPP_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID) and settings.WHATSAPP_MODO != "simulado"


def normalizar_telefono(telefono: str | None) -> str:
    digitos = re.sub(r"\D", "", telefono or "")
    if len(digitos) == 10 and digitos.startswith("3"):  # celular colombiano sin indicativo
        digitos = "57" + digitos
    return digitos


def enviar(db: Session, destinatario: Usuario | None, texto: str, solicitud: Solicitud | None = None,
           telefono: str | None = None) -> Notificacion:
    """Envía (o simula) un mensaje y deja registro. Nunca lanza excepciones."""
    destino = normalizar_telefono(telefono or (destinatario.telefono if destinatario else None))
    notif = Notificacion(
        usuario_id=destinatario.id if destinatario else None,
        solicitud_id=solicitud.id if solicitud else None,
        direccion="saliente",
        mensaje=texto,
        estado="simulada",
    )
    if not destino:
        notif.estado = "error"
        notif.detalle = "El destinatario no tiene teléfono registrado."
    elif modo_real():
        try:
            resp = httpx.post(
                f"{GRAPH_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
                headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"},
                json={"messaging_product": "whatsapp", "to": destino, "type": "text", "text": {"body": texto}},
                timeout=10,
            )
            if resp.status_code < 300:
                notif.estado = "enviada"
            else:
                notif.estado = "error"
                notif.detalle = f"HTTP {resp.status_code}: {resp.text[:300]}"
        except Exception as exc:  # noqa: BLE001
            notif.estado = "error"
            notif.detalle = f"{type(exc).__name__}: {exc}"[:300]
    else:
        notif.detalle = "Modo simulado: no se envió a WhatsApp."
    db.add(notif)
    db.flush()
    if notif.estado == "error":
        log.warning("WhatsApp: %s", notif.detalle)
    return notif


# ---- mensajes por evento del flujo ----
def _fmt(fecha) -> str:
    return fecha.strftime("%d/%m/%Y a las %H:%M")


def notificar_recibida(db: Session, s: Solicitud) -> None:
    enviar(db, s.solicitante, f"EcoConecta: recibimos tu solicitud {s.codigo} ({s.tipo_residuo}). "
           f"Un coordinador de {s.colectivo} la revisará.", s)


def notificar_asignada(db: Session, s: Solicitud) -> None:
    enviar(db, s.asignacion.recolector, f"EcoConecta: se te asignó la solicitud {s.codigo}. "
           "Revisa tu panel para ver los detalles.", s)


def notificar_programada(db: Session, s: Solicitud) -> None:
    p = s.programacion
    enviar(db, s.solicitante, f"EcoConecta: tu solicitud {s.codigo} quedó programada para el {_fmt(p.fecha_hora)}. "
           f"Persona encargada: {p.encargado.nombre}.", s)
    enviar(db, p.encargado, f"EcoConecta: recolección {s.codigo} programada el {_fmt(p.fecha_hora)}.", s)


def notificar_recolectada(db: Session, s: Solicitud) -> None:
    pts = s.puntos.puntos if s.puntos else 0
    enviar(db, s.solicitante, f"EcoConecta: registramos la recolección de {s.codigo}. Sumaste {pts} puntos "
           "(valores de ejemplo, no oficiales). ¡Gracias por separar!", s)


def notificar_cancelada(db: Session, s: Solicitud, motivo: str | None) -> None:
    extra = f" Motivo: {motivo}" if motivo else ""
    enviar(db, s.solicitante, f"EcoConecta: la solicitud {s.codigo} fue cancelada.{extra}", s)
