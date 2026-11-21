"""Pruebas de la lógica pura (no necesitan base de datos). Ejecutar: python -m pytest backend/tests"""
from decimal import Decimal

from backend.constantes import TRANSICIONES
from backend.security.passwords import hash_password, verificar_password
from backend.security.tokens import crear_token, leer_token
from backend.services.puntos import calcular_puntos


def test_puntos_explicables():
    total, texto = calcular_puntos(Decimal("8"), "plastico", Decimal("2.5"), "kg")
    assert total == 20 and "2,5 kg de plástico × 8 puntos/kg = 20 puntos" in texto


def test_sin_regla_no_hay_puntos():
    assert calcular_puntos(None, "vidrio", Decimal("1"), "kg")[0] == 0


def test_estados_terminales():
    assert TRANSICIONES["recolectada"] == [] and TRANSICIONES["cancelada"] == []
    assert "recolectada" not in TRANSICIONES["asignada"]          # RN-05: no se cierra sin programar


def test_password_y_token():
    h = hash_password("clave")
    assert verificar_password("clave", h) and not verificar_password("otra", h)
    t = crear_token(7)
    assert leer_token(t) == 7 and leer_token(t + "x") is None
