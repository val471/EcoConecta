# Roles de los usuarios
ROL_SOLICITANTE = "solicitante"
ROL_COORD_HUERTEROS = "coordinador_huerteros"
ROL_COORD_RECICLADORES = "coordinador_recicladores"
ROL_RECOLECTOR = "recolector"
ROL_ADMIN = "admin"

# Roles de coordinadores
ROLES_COORDINADOR = (
    ROL_COORD_HUERTEROS,
    ROL_COORD_RECICLADORES
)

# Colectivo correspondiente a cada coordinador
COLECTIVO_POR_ROL_COORD = {
    ROL_COORD_HUERTEROS: "huerteros",
    ROL_COORD_RECICLADORES: "recicladores"
}

# Colectivo correspondiente a cada tipo de residuo
COLECTIVO_POR_TIPO = {
    "organico": "huerteros",
    "reciclable": "recicladores"
}

# Aviso sobre las respuestas de inteligencia artificial
AVISO_IA = "La información del asistente es orientativa y puede requerir confirmación de un coordinador."