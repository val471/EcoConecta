"""Webhook de WhatsApp Business Cloud API (mensajes entrantes)."""
import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from backend.config import settings
from backend.database import SessionLocal, get_db
from backend.models import Notificacion, Usuario
from backend.services import ia_service, whatsapp_service

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
def verificar(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and settings.WHATSAPP_VERIFY_TOKEN and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "")
    raise HTTPException(403, "Verificación rechazada.")


def _procesar(datos: dict) -> int:
    procesados = 0
    with SessionLocal() as db:
        usuarios = db.scalars(select(Usuario).where(Usuario.telefono.is_not(None))).all()
        por_telefono = {whatsapp_service.normalizar_telefono(u.telefono): u for u in usuarios}
        for entrada in datos.get("entry", []):
            for cambio in entrada.get("changes", []):
                for msg in cambio.get("value", {}).get("messages", []):
                    if msg.get("type") != "text":
                        continue
                    telefono = msg.get("from", "")
                    texto = msg.get("text", {}).get("body", "")
                    usuario = por_telefono.get(whatsapp_service.normalizar_telefono(telefono))
                    db.add(Notificacion(usuario_id=usuario.id if usuario else None, direccion="entrante",
                                        mensaje=texto, estado="recibida"))
                    # Guía por WhatsApp: el texto se sanitiza dentro de ia_service antes de llegar al modelo
                    respuesta = ia_service.responder(texto, [])
                    whatsapp_service.enviar(db, usuario, respuesta["respuesta"], telefono=telefono)
                    procesados += 1
        db.commit()
    return procesados


@router.post("/webhook")
async def recibir(request: Request):
    cuerpo = await request.body()
    if settings.WHATSAPP_APP_SECRET:
        firma = request.headers.get("X-Hub-Signature-256", "")
        esperada = "sha256=" + hmac.new(settings.WHATSAPP_APP_SECRET.encode(), cuerpo, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(firma, esperada):
            raise HTTPException(403, "Firma inválida.")
    try:
        datos = json.loads(cuerpo or b"{}")
    except ValueError as exc:
        raise HTTPException(400, "JSON inválido.") from exc
    procesados = await run_in_threadpool(_procesar, datos)
    return {"ok": True, "procesados": procesados}
