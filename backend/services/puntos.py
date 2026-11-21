"""Cálculo de puntos explicable y parametrizable (RN-05, RN-06)."""
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional, Tuple

from ..constantes import TIPOS_RESIDUO


def numero(valor: Decimal) -> str:
    """2.50 -> '2,5'   10.00 -> '10'"""
    return format(Decimal(valor).normalize(), "f").replace(".", ",")


def calcular_puntos(puntos_por_unidad: Optional[Decimal], tipo: str, cantidad: Decimal, unidad: str) -> Tuple[int, str]:
    if puntos_por_unidad is None:
        return 0, "Sin regla de puntos para este material; no se asignan puntos."
    ppu = Decimal(str(puntos_por_unidad))
    total = int((Decimal(cantidad) * ppu).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    etiqueta = TIPOS_RESIDUO.get(tipo, {}).get("etiqueta", tipo).lower()
    return total, f"{numero(cantidad)} {unidad} de {etiqueta} × {numero(ppu)} puntos/{unidad} = {total} puntos"
