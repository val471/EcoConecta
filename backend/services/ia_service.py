"""Asistente de educación ambiental con Claude API.
- Solo SUGIERE: no asigna, no programa ni cierra nada (control humano).
- No envía datos personales al modelo (se limpian teléfonos y correos antes de enviar).
- Si no hay clave de API o Claude falla, responde con un modo de respaldo por palabras clave (se declara como tal)."""
import json
import re
import unicodedata
import urllib.request
from typing import List, Optional, Tuple

from ..config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

SISTEMA = """Eres el asistente de educación ambiental de EcoConecta, una plataforma comunitaria de Villas de San Pablo (Barranquilla).
Reglas:
- Responde en español sencillo, con frases cortas y en máximo 90 palabras. Muchas personas que te escriben son adultos mayores.
- Solo hablas de separar residuos orgánicos y reciclables, compostaje, la huerta comunitaria y cómo usar la plataforma (solicitar una recolección, ver el estado, los puntos).
- Los residuos orgánicos los recogen los huerteros y los reciclables los recogen los recicladores. Si no estás seguro de dónde va un residuo, dilo con honestidad y sugiere preguntar al coordinador.
- No prometas fechas, horas ni asignaciones: eso lo decide y lo confirma un coordinador, que es una persona.
- Los puntos son valores de ejemplo y no son reglas oficiales de la Fundación Santo Domingo.
- No pidas ni repitas nombres, teléfonos, direcciones ni otros datos personales.
- Si la pregunta no tiene que ver con estos temas, di amablemente que solo puedes ayudar con residuos y con la plataforma.
Al final de tu respuesta, en una línea aparte, escribe exactamente una de estas etiquetas: [[FLUJO:organico]], [[FLUJO:reciclable]] o [[FLUJO:ninguno]], según el tipo de residuo del que habló la persona (ninguno si no aplica o si mencionó los dos tipos)."""

MAX_TEXTO = 500


def _norm(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def limpiar(texto: str) -> str:
    """Quita correos y números largos (teléfonos) antes de enviar nada a un modelo."""
    texto = (texto or "")[:MAX_TEXTO]
    texto = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[correo omitido]", texto)
    texto = re.sub(r"\+?\d(?:[\s\-.]?\d){6,}", "[número omitido]", texto)
    return texto.strip()


def construir_mensajes(historial: List[dict], mensaje: str) -> List[dict]:
    """Arma la conversación alternando usuario/asistente y terminando en un mensaje del usuario."""
    msgs: List[dict] = []
    for h in (historial or [])[-6:]:
        rol = {"usuario": "user", "asistente": "assistant"}.get(h.get("rol"))
        texto = limpiar(h.get("texto", ""))
        if not rol or not texto:
            continue
        if msgs and msgs[-1]["role"] == rol:
            msgs[-1]["content"] += "\n" + texto
        else:
            msgs.append({"role": rol, "content": texto})
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    nuevo = limpiar(mensaje)
    if msgs and msgs[-1]["role"] == "user":
        msgs[-1]["content"] += "\n" + nuevo
    else:
        msgs.append({"role": "user", "content": nuevo})
    return msgs


def extraer_flujo(texto: str) -> Tuple[str, Optional[str]]:
    m = re.search(r"\[\[FLUJO:(organico|reciclable|ninguno)\]\]", texto)
    flujo = m.group(1) if m else None
    limpio = re.sub(r"\[\[FLUJO:[a-z]*\]\]", "", texto).strip()
    return limpio, (flujo if flujo in ("organico", "reciclable") else None)


def _llamar_claude(mensajes: List[dict]) -> str:
    cuerpo = json.dumps({"model": ANTHROPIC_MODEL, "max_tokens": 400, "system": SISTEMA, "messages": mensajes}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=cuerpo, method="POST",
        headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        datos = json.loads(r.read())
    return "".join(b.get("text", "") for b in datos.get("content", []) if b.get("type") == "text")


# ---------------- Modo de respaldo (sin IA) ----------------
ORGANICOS = ["cascara", "fruta", "verdura", "comida", "resto", "cafe", "borra", "huevo", "poda", "hoja", "pasto", "sobras"]
RECICLABLES = ["botella", "plastico", "carton", "papel", "vidrio", "lata", "metal", "envase", "periodico", "aluminio", "frasco", "revista"]
NO_APROVECHABLES = ["papel higienico", "panal", "colilla", "servilleta usada", "toalla higienica"]


def respaldo(mensaje: str) -> Tuple[str, Optional[str]]:
    t = _norm(mensaje)
    if any(p in t for p in NO_APROVECHABLES):
        return ("Ese residuo no se aprovecha: va con los residuos ordinarios, no con los orgánicos ni los reciclables.", None)
    org, rec = any(p in t for p in ORGANICOS), any(p in t for p in RECICLABLES)
    if org and rec:
        return ("Veo residuos de los dos tipos. Sepáralos: los orgánicos por un lado y los reciclables por otro, "
                "y haz una solicitud para cada tipo.", None)
    if org:
        return ("Eso es un residuo orgánico (restos de comida, cáscaras, café, hojas). Lo recoge un huertero para hacer abono "
                "en la huerta comunitaria. Puedes pedir la recolección en «Solicitar recolección».", "organico")
    if rec:
        return ("Eso es reciclable. Déjalo limpio y seco, separado de los orgánicos. Lo recoge un reciclador de oficio. "
                "Puedes pedir la recolección en «Solicitar recolección».", "reciclable")
    return ("No estoy seguro de qué tipo de residuo es. Dime el nombre, por ejemplo «cáscara de naranja» o «botella de plástico», "
            "o consulta la sección «Aprende». También puedes preguntarle a tu coordinador.", None)


def responder(mensaje: str, historial: List[dict]) -> dict:
    mensaje = limpiar(mensaje)
    if ANTHROPIC_API_KEY:
        try:
            texto = _llamar_claude(construir_mensajes(historial, mensaje))
            respuesta, flujo = extraer_flujo(texto)
            if respuesta:
                return {"respuesta": respuesta, "flujo_sugerido": flujo, "origen": "claude"}
        except Exception as e:      # no se imprime el mensaje del usuario, solo el tipo de error
            print(f"[asistente] Claude no respondió ({type(e).__name__} {getattr(e, 'code', '')}); se usa el modo de respaldo")
    respuesta, flujo = respaldo(mensaje)
    return {"respuesta": respuesta, "flujo_sugerido": flujo, "origen": "respaldo"}
