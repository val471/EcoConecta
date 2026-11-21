"""RN-01: cada solicitud llega al colectivo correcto según su flujo."""
COORDINADOR_POR_FLUJO = {"organico": "coord_huerteros", "reciclable": "coord_recicladores"}
FLUJO_POR_COORDINADOR = {rol: flujo for flujo, rol in COORDINADOR_POR_FLUJO.items()}


def flujo_de_coordinador(usuario) -> str:
    return FLUJO_POR_COORDINADOR[usuario.rol]
