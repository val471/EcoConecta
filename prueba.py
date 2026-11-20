from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routers import asistente

app = FastAPI()
app.include_router(asistente.router)
app.mount("/", StaticFiles(directory="frontend", html=True))