"""Valores fijos compartidos con el frontend (mismos nombres que js/config.js)."""

ROLES = ("solicitante", "coord_huerteros", "coord_recicladores", "recolector", "admin")
FLUJOS = ("organico", "reciclable")
TIPOS_GENERADOR = ("hogar", "unidad_productiva")

ETIQUETA_ESTADO = {
    "recibida": "Recibida",
    "en_revision": "En revisión",
    "asignada": "Asignada",
    "programada": "Programada",
    "recolectada": "Recolectada",
    "cancelada": "Cancelada",
}

# Transiciones permitidas (RN-02, RN-05)
TRANSICIONES = {
    "recibida": ["en_revision", "asignada", "cancelada"],
    "en_revision": ["asignada", "cancelada"],
    "asignada": ["programada", "cancelada"],
    "programada": ["recolectada", "cancelada"],
    "recolectada": [],
    "cancelada": [],
}

TIPOS_RESIDUO = {
    "organico": {"etiqueta": "Orgánico", "flujo": "organico"},
    "plastico": {"etiqueta": "Plástico", "flujo": "reciclable"},
    "carton_papel": {"etiqueta": "Cartón y papel", "flujo": "reciclable"},
    "vidrio": {"etiqueta": "Vidrio", "flujo": "reciclable"},
    "metal": {"etiqueta": "Metal", "flujo": "reciclable"},
}

# Valores de EJEMPLO. No son reglas oficiales de la Fundación Santo Domingo (RN-06).
REGLAS_PUNTOS_EJEMPLO = [
    ("organico", "kg", 5),
    ("plastico", "kg", 8),
    ("carton_papel", "kg", 4),
    ("vidrio", "kg", 3),
    ("metal", "kg", 10),
]
