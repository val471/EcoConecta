"""Servicio de IA (Claude API) de EcoConecta. Responsable: persona C.

Reglas que cumple este archivo:
- La IA solo orienta: guía y clasifica de forma orientativa. Nunca asigna,
  programa ni cierra una solicitud (eso lo hace una persona).
- Antes de enviar cualquier texto al modelo se le quitan teléfonos, correos y
  direcciones. No se envían nombres, teléfonos ni direcciones.
- Si la API falla o no hay clave, se devuelve un mensaje de respaldo y la
  aplicación sigue funcionando.
"""
import json
import logging
import os
import re

from anthropic import Anthropic

log = logging.getLogger(__name__)

# El modelo y la clave vienen de variables de entorno (nunca van en el código).
MODELO = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
MAX_CARACTERES = 500          # límite de texto que se envía al modelo
MAX_TURNOS_HISTORIAL = 6      # cuántos mensajes previos se envían

TIPOS_VALIDOS = {"organico", "reciclable", "no_seguro"}

MENSAJE_RESPALDO = (
    "Ahora mismo no puedo responder con el asistente. "
    "Puedes consultar la sección de Educación o enviar tu solicitud y "
    "un coordinador la revisará."
)

SYSTEM_GUIA = (
    "Eres la guía de EcoConecta, una plataforma comunitaria de Villas de San Pablo "
    "(Barranquilla) para separar residuos y solicitar su recolección. "
    "Responde en español sencillo, cálido y en pocas frases (máximo 5). "
    "Habla solo de separación de residuos orgánicos y reciclables, de cómo "
    "preparar los residuos y de cómo usar la plataforma. "
    "Los residuos orgánicos los recogen los huerteros y los reciclables los "
    "recogen los recicladores. "
    "No pidas ni repitas nombres, teléfonos ni direcciones. "
    "No decidas asignaciones, horarios ni puntos: eso lo hacen los coordinadores "
    "y la plataforma. Si te preguntan por algo fuera de este tema, di amablemente "
    "que solo puedes ayudar con residuos y con la plataforma."
)

SYSTEM_CLASIFICAR = (
    "Clasificas de forma orientativa un residuo descrito por una persona. "
    "Responde SOLO con un objeto JSON, sin texto adicional, con esta forma: "
    '{"tipo": "organico" | "reciclable" | "no_seguro", "justificacion": "una frase corta"}. '
    "Usa organico para restos de comida, cáscaras, hojas y poda. "
    "Usa reciclable para papel, cartón, plástico, vidrio y metal limpios y secos. "
    "Usa no_seguro si la descripción es ambigua, mezclada o no corresponde a ninguno."
)

_cliente = None


def _obtener_cliente():
    """Crea el cliente una sola vez. Devuelve None si no hay clave."""
    global _cliente
    if _cliente is None:
        clave = os.getenv("ANTHROPIC_API_KEY")
        if not clave:
            log.warning("ANTHROPIC_API_KEY no está configurada")
            return None
        _cliente = Anthropic(api_key=clave, timeout=20.0, max_retries=1)
    return _cliente


# ---------------------------------------------------------------- privacidad

_CORREO = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_TELEFONO = re.compile(r"(?<!\w)\+?\d(?:[\s().-]?\d){6,}(?!\w)")
_DIRECCION = re.compile(
    r"\b(?:calle|cll|carrera|cra|cr|kr|diagonal|diag|transversal|trans|avenida|av|"
    r"manzana|mz|casa|apto|apartamento)\b\.?\s*#?\s*\d+\w*(?:\s*(?:#|no\.?|-)\s*\d+\w*)*",
    re.IGNORECASE,
)


def limpiar_datos_personales(texto: str) -> str:
    """Quita correos, teléfonos y direcciones y recorta el texto.

    Los nombres propios no se pueden detectar con seguridad, por eso el
    asistente también le pide al usuario que no los escriba.
    """
    texto = _CORREO.sub("[correo]", texto or "")
    texto = _DIRECCION.sub("[dirección]", texto)
    texto = _TELEFONO.sub("[teléfono]", texto)
    return texto.strip()[:MAX_CARACTERES]


# ------------------------------------------------------------------ llamadas

def _llamar(system: str, mensajes: list, max_tokens: int = 400):
    """Llama a Claude. Devuelve el texto o None si algo falla."""
    cliente = _obtener_cliente()
    if cliente is None:
        return None
    try:
        respuesta = cliente.messages.create(
            model=MODELO, max_tokens=max_tokens, system=system, messages=mensajes
        )
        return respuesta.content[0].text.strip()
    except Exception:  # la app no debe romperse si la IA falla
        log.exception("Error llamando a Claude API")
        return None


def guia(pregunta: str, historial: list | None = None) -> str:
    """Responde una pregunta del usuario. historial: [{"role", "content"}, ...]"""
    mensajes = []
    for turno in (historial or [])[-MAX_TURNOS_HISTORIAL:]:
        rol = turno.get("role")
        contenido = limpiar_datos_personales(turno.get("content", ""))
        if rol in ("user", "assistant") and contenido:
            mensajes.append({"role": rol, "content": contenido})
    while mensajes and mensajes[0]["role"] != "user":
        mensajes.pop(0)  # la conversación debe empezar con el usuario

    pregunta_limpia = limpiar_datos_personales(pregunta)
    if not pregunta_limpia:
        return "Escribe tu pregunta sobre residuos y con gusto te ayudo."
    mensajes.append({"role": "user", "content": pregunta_limpia})

    return _llamar(SYSTEM_GUIA, mensajes) or MENSAJE_RESPALDO


def clasificar(descripcion: str) -> dict:
    """Sugiere si un residuo es orgánico o reciclable. Es solo orientativo.

    Devuelve {"tipo", "justificacion", "origen"}. El tipo final lo confirma
    la persona que hace la solicitud y lo revisa el coordinador (RN-01).
    """
    respaldo = {
        "tipo": "no_seguro",
        "justificacion": "No pude clasificarlo; un coordinador lo revisará.",
        "origen": "respaldo",
    }
    texto = limpiar_datos_personales(descripcion)
    if not texto:
        return respaldo

    bruto = _llamar(SYSTEM_CLASIFICAR, [{"role": "user", "content": texto}], max_tokens=150)
    if not bruto:
        return respaldo
    try:
        inicio, fin = bruto.index("{"), bruto.rindex("}") + 1
        datos = json.loads(bruto[inicio:fin])
        tipo = datos.get("tipo")
        if tipo not in TIPOS_VALIDOS:
            return respaldo
        return {
            "tipo": tipo,
            "justificacion": str(datos.get("justificacion", ""))[:200],
            "origen": "ia",
        }
    except (ValueError, json.JSONDecodeError):
        return respaldo


if __name__ == "__main__":
    # Chat de prueba en la terminal. Escribe "salir" para terminar.
    # Para probar el clasificador escribe: clasificar: cáscaras de plátano
    historial = []
    print("Asistente EcoConecta (escribe 'salir' para terminar)")
    while True:
        texto = input("Tú: ").strip()
        if texto.lower() in ("salir", "exit"):
            break
        if texto.lower().startswith("clasificar:"):
            print("Clasificación:", clasificar(texto.split(":", 1)[1]))
            continue
        respuesta = guia(texto, historial)
        print("Guía:", respuesta)
        historial += [
            {"role": "user", "content": texto},
            {"role": "assistant", "content": respuesta},
        ]