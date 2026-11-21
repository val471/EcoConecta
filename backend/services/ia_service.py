"""Asistente con Claude API. SOLO sugiere, clasifica orientativamente y guía.

- La asignación, la confirmación del horario y el cierre los hace siempre una persona.
- Nunca se envían nombres, teléfonos, correos ni direcciones al modelo: `sanitizar` los enmascara.
- Sin ANTHROPIC_API_KEY (o si la API falla) responde en modo 'local' con reglas simples.
"""
import json
import logging
import re

import httpx

from backend.config import settings
from backend.constantes import AVISO_IA, COLECTIVO_POR_TIPO

log = logging.getLogger("ecoconecta.ia")
API_URL = "https://api.anthropic.com/v1/messages"

SISTEMA_ASISTENTE = (
    "Eres la guía de EcoConecta, una plataforma comunitaria de Villas de San Pablo para separar residuos. "
    "Responde en español, claro y breve (máximo 5 frases). Orienta sobre cómo separar residuos orgánicos "
    "(los recogen huerteros) y reciclables (los recogen recicladores) y sobre cómo usar la plataforma: "
    "solicitar recolección, esperar la revisión del coordinador, la programación y los puntos. "
    "Solo orientas: no asignas recolectores, no confirmas horarios ni cierras solicitudes; eso lo hace una persona. "
    "Los puntos son valores de ejemplo, no reglas oficiales. No pidas ni repitas nombres, teléfonos ni direcciones; "
    "si aparecen, ignóralos. Si no sabes algo, dilo y sugiere hablar con el coordinador."
)

SISTEMA_CLASIFICADOR = (
    "Clasifica de forma orientativa el residuo descrito. Responde SOLO un JSON con las claves "
    '"tipo" ("organico", "reciclable" o "indefinido") y "motivo" (una frase corta en español). '
    "Orgánico: restos de comida, cáscaras, poda, café, hojas. Reciclable: plástico, cartón, papel, vidrio, metal. "
    "No incluyas nada más que el JSON."
)

_PATRONES_PII = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[correo]"),
    (re.compile(r"\+?\d[\d\s().-]{6,}\d"), "[número]"),
    (re.compile(r"\b(calle|carrera|cra|cr|cl|kr|diagonal|diag|transversal|trans|avenida|av|manzana|mz)\b\.?\s*#?\s*\d[\w\s#-]*",
                re.IGNORECASE), "[dirección]"),
]


def sanitizar(texto: str) -> str:
    """Enmascara correos, números largos y direcciones antes de enviar texto al modelo."""
    for patron, reemplazo in _PATRONES_PII:
        texto = patron.sub(reemplazo, texto)
    return texto


def _llamar_claude(sistema: str, mensajes: list[dict], max_tokens: int = 400) -> str:
    resp = httpx.post(
        API_URL,
        headers={
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={"model": settings.ANTHROPIC_MODEL, "max_tokens": max_tokens, "system": sistema, "messages": mensajes},
        timeout=20,
    )
    resp.raise_for_status()
    bloques = resp.json().get("content", [])
    return "".join(b.get("text", "") for b in bloques if b.get("type") == "text").strip()


# ---------------- guía conversacional ----------------
def responder(mensaje: str, historial: list[dict]) -> dict:
    mensajes = []
    for turno in historial[-10:]:
        rol = "user" if turno["rol"] == "usuario" else "assistant"
        mensajes.append({"role": rol, "content": sanitizar(turno["texto"])})
    mensajes.append({"role": "user", "content": sanitizar(mensaje)})
    # la API exige que el primer mensaje sea del usuario y que los roles alternen
    while mensajes and mensajes[0]["role"] != "user":
        mensajes.pop(0)
    if settings.ANTHROPIC_API_KEY:
        try:
            return {"respuesta": _llamar_claude(SISTEMA_ASISTENTE, mensajes), "modo": "claude", "aviso": AVISO_IA}
        except Exception as exc:  # noqa: BLE001
            log.warning("Claude API falló, se usa modo local: %s", exc)
    return {"respuesta": _respuesta_local(mensaje), "modo": "local", "aviso": AVISO_IA}


def _respuesta_local(mensaje: str) -> str:
    m = mensaje.lower()
    if any(p in m for p in ("punto", "premio", "recompensa")):
        return ("Recibes puntos cuando la recolección queda registrada. Cuántos depende del tipo y la cantidad de "
                "residuo según una regla de ejemplo que configura el administrador.")
    if any(p in m for p in ("orgánico", "organico", "cáscara", "cascara", "comida", "fruta", "verdura")):
        return ("Los residuos orgánicos (cáscaras, restos de comida, poda) los recogen los huerteros. Sepáralos en "
                "un recipiente aparte, sin plásticos, y haz tu solicitud en la sección 'Solicitar recolección'.")
    if any(p in m for p in ("plástico", "plastico", "cartón", "carton", "papel", "vidrio", "lata", "botella", "reciclable")):
        return ("Los reciclables (plástico, cartón, papel, vidrio, metal) los recogen los recicladores. Entrégalos "
                "limpios y secos, y haz tu solicitud en 'Solicitar recolección'.")
    return ("Puedo orientarte sobre cómo separar residuos orgánicos y reciclables y cómo usar la plataforma. "
            "Un coordinador revisa tu solicitud y una persona programa la recolección.")


# ---------------- clasificación orientativa ----------------
_ORGANICO = ("cáscara", "cascara", "fruta", "verdura", "comida", "resto", "poda", "café", "cafe", "huevo",
             "hoja", "pasto", "orgánico", "organico", "compost", "sobras")
_RECICLABLE = ("plástico", "plastico", "botella", "cartón", "carton", "papel", "vidrio", "lata", "metal",
               "aluminio", "tetra", "periódico", "periodico", "reciclable", "chatarra")


def _clasificar_local(descripcion: str) -> dict:
    d = descripcion.lower()
    o = sum(p in d for p in _ORGANICO)
    r = sum(p in d for p in _RECICLABLE)
    if o > r:
        return {"tipo": "organico", "motivo": "Menciona residuos de origen orgánico.", "modo": "local"}
    if r > o:
        return {"tipo": "reciclable", "motivo": "Menciona materiales reciclables.", "modo": "local"}
    return {"tipo": "indefinido", "motivo": "No es claro si es orgánico o reciclable; elige el tipo manualmente.", "modo": "local"}


def clasificar(descripcion: str) -> dict:
    resultado = None
    if settings.ANTHROPIC_API_KEY:
        try:
            texto = _llamar_claude(SISTEMA_CLASIFICADOR, [{"role": "user", "content": sanitizar(descripcion)}], 150)
            m = re.search(r"\{.*\}", texto, re.DOTALL)
            datos = json.loads(m.group(0)) if m else {}
            if datos.get("tipo") in ("organico", "reciclable", "indefinido"):
                resultado = {"tipo": datos["tipo"], "motivo": str(datos.get("motivo", ""))[:300], "modo": "claude"}
        except Exception as exc:  # noqa: BLE001
            log.warning("Clasificación con Claude falló, se usa modo local: %s", exc)
    if resultado is None:
        resultado = _clasificar_local(descripcion)
    return {
        "tipo_sugerido": resultado["tipo"],
        "colectivo_sugerido": COLECTIVO_POR_TIPO.get(resultado["tipo"]),
        "motivo": resultado["motivo"],
        "modo": resultado["modo"],
        "aviso": AVISO_IA,
    }
