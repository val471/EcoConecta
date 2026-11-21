"""Prueba del escenario de demostración y de las reglas RN-01..RN-08.

⚠ Esta prueba BORRA y recrea las tablas. Usa una base de datos de pruebas distinta de la real:
    TEST_DATABASE_URL=postgresql://usuario:clave@localhost:5432/ecoconecta_test  python -m pytest -v
"""
import os

import pytest

URL = os.getenv("TEST_DATABASE_URL")
if not URL:
    pytest.skip("Define TEST_DATABASE_URL (PostgreSQL de pruebas) para ejecutar estas pruebas.", allow_module_level=True)

os.environ["DATABASE_URL"] = URL
os.environ["CARGAR_DEMO"] = "false"
for _v in ("ANTHROPIC_API_KEY", "WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"):
    os.environ[_v] = ""

from fastapi.testclient import TestClient  # noqa: E402

from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import Solicitud  # noqa: E402
from backend.seed.datos_demo import PASSWORD_DEMO, cargar_demo  # noqa: E402
from backend.services.flujo_estados import FlujoError, cambiar_estado  # noqa: E402

PROGRAMACION = "2026-11-25T09:00:00"


@pytest.fixture(scope="module")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        cargar_demo(db)
    with TestClient(app) as c:
        yield c


def login(client, email):
    r = client.post("/api/auth/login", json={"email": email, "password": PASSWORD_DEMO})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def nueva(client, h, tipo="organico", cantidad=5):
    r = client.post("/api/solicitudes", headers=h,
                    json={"tipo_residuo": tipo, "descripcion": "Residuos de prueba", "cantidad_estimada": cantidad,
                          "unidad_estimada": "kg"})
    assert r.status_code == 201, r.text
    return r.json()


def recolectores(client, h):
    return {r["nombre"]: r["id"] for r in client.get("/api/coordinador/recolectores", headers=h).json()}


def test_escenario_de_demostracion(client):
    usuario = login(client, "unidad.productiva@ecoconecta.demo")
    coord_h = login(client, "coord.huerteros@ecoconecta.demo")
    coord_r = login(client, "coord.recicladores@ecoconecta.demo")
    huertero = login(client, "huertero1@ecoconecta.demo")
    hogar = login(client, "hogar@ecoconecta.demo")

    # 1. Unidad productiva solicita recolección orgánica (RN-01, RN-04)
    s = nueva(client, usuario, "organico", 5)
    assert s["estado"] == "recibida" and s["colectivo"] == "huerteros"
    assert s["codigo"].startswith("SOL-") and len(s["historial"]) == 1
    sid = s["id"]

    # 2. El coordinador de huerteros la revisa y asigna un huertero (RN-03)
    assert client.post(f"/api/coordinador/solicitudes/{sid}/revisar", headers=coord_h, json={}).status_code == 200
    ids = recolectores(client, coord_h)
    r = client.post(f"/api/coordinador/solicitudes/{sid}/asignar", headers=coord_h, json={"recolector_id": ids["Huertero Uno"]})
    assert r.status_code == 200 and r.json()["estado"] == "asignada"
    assert r.json()["recolector_nombre"] == "Huertero Uno" and r.json()["coordinador_nombre"]

    # 3. Se registra día, hora y persona encargada (RN-02)
    r = client.post(f"/api/coordinador/solicitudes/{sid}/programar", headers=coord_h, json={"fecha_hora": PROGRAMACION})
    assert r.status_code == 200 and r.json()["estado"] == "programada"
    assert r.json()["programacion"]["encargado_nombre"] == "Huertero Uno"

    # RN-05: aún no hay puntos
    assert client.get("/api/solicitudes/puntos", headers=usuario).json()["total"] == 0

    # 4. El huertero registra la recolección → estado y puntos (RN-05, RN-06)
    r = client.post(f"/api/recolector/solicitudes/{sid}/recoleccion", headers=huertero,
                    json={"cantidad": 5, "unidad": "kg"})
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "recolectada" and r.json()["puntos"]["puntos"] == 10
    assert "no son reglas oficiales" in r.json()["puntos"]["explicacion"]
    assert client.get("/api/solicitudes/puntos", headers=usuario).json()["total"] == 10

    # historial completo (RN-04)
    estados = [h["estado_nuevo"] for h in client.get(f"/api/solicitudes/{sid}", headers=usuario).json()["historial"]]
    assert estados == ["recibida", "en_revision", "asignada", "programada", "recolectada"]

    # 5. Un segundo usuario solicita reciclables → coordinador de recicladores (RN-01)
    s2 = nueva(client, hogar, "reciclable", 3)
    assert s2["colectivo"] == "recicladores"
    bandeja_r = [x["id"] for x in client.get("/api/coordinador/solicitudes", headers=coord_r).json()]
    bandeja_h = [x["id"] for x in client.get("/api/coordinador/solicitudes", headers=coord_h).json()]
    assert s2["id"] in bandeja_r and s2["id"] not in bandeja_h


def test_rn02_no_se_programa_sin_asignar_ni_sin_fecha(client):
    usuario = login(client, "hogar@ecoconecta.demo")
    coord = login(client, "coord.huerteros@ecoconecta.demo")
    sid = nueva(client, usuario)["id"]
    # sin asignar → 409
    assert client.post(f"/api/coordinador/solicitudes/{sid}/programar", headers=coord,
                       json={"fecha_hora": PROGRAMACION}).status_code == 409
    # sin fecha → 422
    assert client.post(f"/api/coordinador/solicitudes/{sid}/programar", headers=coord, json={}).status_code == 422
    # la regla también se cumple en el servicio, no solo en el endpoint
    with SessionLocal() as db:
        s = db.get(Solicitud, sid)
        s.estado = "asignada"
        with pytest.raises(FlujoError):
            cambiar_estado(db, s, "programada", None)
        db.rollback()


def test_rn05_no_hay_recoleccion_ni_puntos_antes_de_programar(client):
    usuario = login(client, "hogar@ecoconecta.demo")
    coord = login(client, "coord.huerteros@ecoconecta.demo")
    huertero = login(client, "huertero1@ecoconecta.demo")
    sid = nueva(client, usuario)["id"]
    client.post(f"/api/coordinador/solicitudes/{sid}/revisar", headers=coord, json={})
    ids = recolectores(client, coord)
    client.post(f"/api/coordinador/solicitudes/{sid}/asignar", headers=coord, json={"recolector_id": ids["Huertero Uno"]})
    r = client.post(f"/api/recolector/solicitudes/{sid}/recoleccion", headers=huertero, json={"cantidad": 2})
    assert r.status_code == 409  # todavía no está programada


def test_rn07_privacidad(client):
    dueno = login(client, "hogar@ecoconecta.demo")
    otro = login(client, "unidad.productiva@ecoconecta.demo")
    coord = login(client, "coord.huerteros@ecoconecta.demo")
    coord_otro = login(client, "coord.recicladores@ecoconecta.demo")
    asignado = login(client, "huertero1@ecoconecta.demo")
    no_asignado = login(client, "huertero2@ecoconecta.demo")
    admin = login(client, "admin@ecoconecta.demo")

    sid = nueva(client, dueno)["id"]
    client.post(f"/api/coordinador/solicitudes/{sid}/revisar", headers=coord, json={})
    ids = recolectores(client, coord)
    client.post(f"/api/coordinador/solicitudes/{sid}/asignar", headers=coord, json={"recolector_id": ids["Huertero Uno"]})

    assert client.get(f"/api/solicitudes/{sid}", headers=otro).status_code == 404            # otro solicitante
    assert client.get(f"/api/solicitudes/{sid}", headers=coord_otro).status_code == 404      # otro colectivo
    assert client.get(f"/api/recolector/solicitudes/{sid}", headers=no_asignado).status_code == 404
    ve = client.get(f"/api/recolector/solicitudes/{sid}", headers=asignado).json()
    assert ve["contacto_telefono"] and ve["direccion"]                                       # quien atiende sí ve contacto
    adm = client.get(f"/api/solicitudes/{sid}", headers=admin).json()
    assert adm["contacto_telefono"] is None and adm["direccion"] is None                     # el admin no
    assert client.get("/api/coordinador/solicitudes", headers=dueno).status_code == 403      # permisos por rol


def test_rn06_regla_de_puntos_parametrizable(client):
    admin = login(client, "admin@ecoconecta.demo")
    reglas = client.get("/api/admin/reglas", headers=admin).json()
    assert reglas and all("aviso" in r for r in reglas)
    r = client.put(f"/api/admin/reglas/{reglas[0]['id']}", headers=admin, json={"puntos_por_unidad": 3})
    assert r.status_code == 200 and r.json()["puntos_por_unidad"] == 3


def test_rn08_usuarios_piloto_configurables(client):
    admin = login(client, "admin@ecoconecta.demo")
    u = client.post("/api/admin/usuarios", headers=admin, json={
        "nombre": "Piloto Nuevo", "email": "piloto@ecoconecta.demo", "password": "Piloto2026!",
        "rol": "solicitante", "tipo_solicitante": "hogar", "es_piloto": False}).json()
    r = client.patch(f"/api/admin/usuarios/{u['id']}", headers=admin, json={"es_piloto": True})
    assert r.status_code == 200 and r.json()["es_piloto"] is True


def test_asistente_clasifica_sin_datos_personales(client):
    from backend.services.ia_service import sanitizar

    h = login(client, "hogar@ecoconecta.demo")
    r = client.post("/api/asistente/clasificar", headers=h, json={"descripcion": "Botellas de plástico y cartón"})
    assert r.status_code == 200 and r.json()["tipo_sugerido"] == "reciclable"
    texto = sanitizar("Soy Ana, vivo en Calle 12 # 3-45, mi correo ana@correo.com y mi cel 3001234567")
    assert "ana@correo.com" not in texto and "3001234567" not in texto and "3-45" not in texto
