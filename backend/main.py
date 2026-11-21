import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from . import models  # noqa: F401  (registra las tablas)
from .database import Base, SessionLocal, engine
from .routers import admin, asistente, auth, contenidos, coordinador, recolector, solicitudes, whatsapp
from .seed.datos_demo import cargar_datos_demo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Al arrancar: crea las tablas y carga los datos demo si la base está vacía (sirve también en Render)."""
    if engine is not None:
        for intento in range(10):                      # la base puede tardar unos segundos en estar lista
            try:
                Base.metadata.create_all(engine)
                with SessionLocal() as db:
                    cargar_datos_demo(db)
                break
            except Exception as e:
                print(f"[arranque] base de datos no lista (intento {intento + 1}/10): {type(e).__name__}")
                time.sleep(2)
    yield


app = FastAPI(title="EcoConecta Villas de San Pablo", lifespan=lifespan)

for modulo in (auth, contenidos, solicitudes, coordinador, recolector, admin, asistente, whatsapp):
    app.include_router(modulo.router, prefix="/api")


@app.get("/api/salud")
def salud():
    """Prueba de despliegue: responde ok y comprueba la conexión a PostgreSQL."""
    estado_db = "sin DATABASE_URL"
    if engine is not None:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            estado_db = "ok"
        except Exception as e:
            estado_db = f"error: {type(e).__name__}"
    return {"estado": "ok", "base_de_datos": estado_db}


# El frontend va al final, para no tapar /api
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
