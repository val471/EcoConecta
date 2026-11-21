"""Pruebas del asistente que no necesitan red ni base de datos."""
from backend.services.ia_service import construir_mensajes, extraer_flujo, limpiar, respaldo


def test_no_envia_datos_personales():
    t = limpiar("Mi cel es 300 123 4567 y mi correo es ana@demo.co, ¿dónde va el vidrio?")
    assert "4567" not in t and "@" not in t and "vidrio" in t


def test_extrae_flujo_y_limpia_etiqueta():
    assert extraer_flujo("Va con los orgánicos.\n[[FLUJO:organico]]") == ("Va con los orgánicos.", "organico")
    assert extraer_flujo("Depende.\n[[FLUJO:ninguno]]") == ("Depende.", None)
    assert extraer_flujo("Sin etiqueta") == ("Sin etiqueta", None)


def test_respaldo_clasifica():
    assert respaldo("¿Qué hago con una cáscara de naranja?")[1] == "organico"
    assert respaldo("tengo una botella de plástico")[1] == "reciclable"
    assert respaldo("papel higiénico")[1] is None and "no se aprovecha" in respaldo("papel higiénico")[0]
    assert respaldo("cáscara y botella")[1] is None
    assert respaldo("hola")[1] is None


def test_mensajes_alternan_y_terminan_en_usuario():
    m = construir_mensajes([{"rol": "asistente", "texto": "Hola"}, {"rol": "usuario", "texto": "a"},
                            {"rol": "usuario", "texto": "b"}, {"rol": "asistente", "texto": "c"}], "d")
    assert m[0]["role"] == "user" and m[-1] == {"role": "user", "content": "d"}
    assert all(m[i]["role"] != m[i + 1]["role"] for i in range(len(m) - 1))
