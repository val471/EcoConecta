
from fastapi import FastAPI

from backend.routers import auth, asistente


app = FastAPI(
    title="EcoConecta API",
    description="Backend de la plataforma EcoConecta",
    version="1.0.0"
)


# Rutas de autenticación
app.include_router(auth.router)

# Rutas del asistente inteligente
app.include_router(asistente.router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a la API de EcoConecta",
        "estado": "activo"
    }


@app.get("/health")
def verificar_estado():
    return {
        "estado": "funcionando"
    }