"""Contenidos educativos y horarios de ejemplo.

- GET /api/contenidos                    -> todo el contenido
- GET /api/contenidos?tipo=organico      -> solo orgánicos
- GET /api/contenidos?tipo=reciclable    -> solo reciclables
- GET /api/contenidos?tipo=general       -> cómo funciona la plataforma

Los textos son orientativos. Los horarios son de EJEMPLO: el día y la hora
reales de cada recolección los confirma el coordinador al programarla (RN-02).
"""
from typing import Literal

from fastapi import APIRouter

router = APIRouter(prefix="/api/contenidos", tags=["contenidos"])

AVISO_HORARIOS = (
    "Estos horarios son de ejemplo. El día, la hora y la persona encargada de tu "
    "recolección te los confirma el coordinador cuando la programa."
)

HORARIOS = [
    {
        "colectivo": "Huerteros",
        "recoge": "Residuos orgánicos",
        "dias": "Martes y viernes",
        "franja": "7:00 a. m. a 10:00 a. m.",
    },
    {
        "colectivo": "Recicladores",
        "recoge": "Residuos reciclables",
        "dias": "Lunes y jueves",
        "franja": "2:00 p. m. a 5:00 p. m.",
    },
]

# Cada contenido tiene: id, tipo, titulo, texto, listas (marca: si | no | punto)
# y, opcionalmente, pasos (una secuencia numerada).
CONTENIDOS = [
    {
        "id": "organico-que-entregar",
        "tipo": "organico",
        "titulo": "Qué entregar a los huerteros",
        "texto": "Los residuos orgánicos se convierten en abono para las huertas de la comunidad.",
        "listas": [
            {
                "titulo": "Sí van",
                "marca": "si",
                "items": [
                    "Cáscaras y restos de frutas y verduras",
                    "Borra de café y bolsitas de té sin grapa",
                    "Cáscaras de huevo",
                    "Hojas secas y poda pequeña",
                    "Restos de comida sin plásticos ni servilletas",
                ],
            },
            {
                "titulo": "No van",
                "marca": "no",
                "items": [
                    "Plástico, vidrio, latas ni papel",
                    "Pañales, toallas higiénicas ni colillas",
                    "Aceite usado ni líquidos",
                    "Carnes, huesos y lácteos: pregunta antes si el colectivo los recibe",
                ],
            },
        ],
    },
    {
        "id": "reciclable-que-entregar",
        "tipo": "reciclable",
        "titulo": "Qué entregar a los recicladores",
        "texto": "Los materiales limpios y secos se pueden aprovechar de nuevo. Los sucios o mojados se pierden.",
        "listas": [
            {
                "titulo": "Sí van",
                "marca": "si",
                "items": [
                    "Papel y cartón limpios y secos",
                    "Botellas y envases de plástico, enjuagados",
                    "Frascos y botellas de vidrio, enjuagados",
                    "Latas de aluminio y de metal, enjuagadas",
                ],
            },
            {
                "titulo": "No van",
                "marca": "no",
                "items": [
                    "Papel o cartón con grasa, comida o humedad",
                    "Servilletas y papel higiénico usados",
                    "Pañales ni residuos de baño",
                    "Vidrio roto: envuélvelo bien y avísale al reciclador",
                ],
            },
        ],
    },
    {
        "id": "general-separar-en-casa",
        "tipo": "general",
        "titulo": "Cómo separar en casa",
        "texto": "Con dos recipientes es suficiente para empezar.",
        "listas": [
            {
                "titulo": "Consejos",
                "marca": "punto",
                "items": [
                    "Usa un recipiente para orgánicos y otro para reciclables, y no los mezcles",
                    "Ponle tapa al de orgánicos para evitar olores y moscas",
                    "Enjuaga y seca los envases antes de guardarlos",
                    "Aplasta botellas y cajas para que ocupen menos espacio",
                ],
            }
        ],
    },
    {
        "id": "general-pedir-recoleccion",
        "tipo": "general",
        "titulo": "Cómo pedir una recolección",
        "texto": "Tu solicitud llega al colectivo que corresponde: huerteros para orgánicos y recicladores para reciclables.",
        "pasos": [
            "Entra a Solicitar recolección y elige si tus residuos son orgánicos o reciclables.",
            "Cuéntanos cuánto tienes, de forma aproximada.",
            "Un coordinador revisa tu solicitud y asigna a la persona que irá a recogerla.",
            "Recibes el día, la hora y el nombre de quien te visita. Hasta entonces la solicitud no está programada.",
            "Entrega tus residuos cuando llegue. Después de que quede registrada la recolección, se suman tus puntos.",
        ],
        "listas": [],
    },
    {
        "id": "general-puntos-y-datos",
        "tipo": "general",
        "titulo": "Tus puntos y tus datos",
        "texto": "",
        "listas": [
            {
                "titulo": "Importante",
                "marca": "punto",
                "items": [
                    "Los puntos se suman solo después de que el recolector registra la recolección.",
                    "Cuánto vale cada residuo lo define el administrador de la plataforma. Los valores que ves son de ejemplo y no son reglas oficiales de la Fundación Santo Domingo.",
                    "Tu teléfono y tu dirección solo los ven las personas que atienden tu solicitud.",
                ],
            }
        ],
    },
]


@router.get("")
def listar(tipo: Literal["organico", "reciclable", "general"] | None = None):
    contenidos = [c for c in CONTENIDOS if tipo is None or c["tipo"] == tipo]
    return {
        "contenidos": contenidos,
        "horarios": HORARIOS,
        "aviso_horarios": AVISO_HORARIOS,
    }