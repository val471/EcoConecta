"""Webhook de WhatsApp Business Cloud API (verificación que exige Meta). Por ahora solo confirma recepción."""
import hmac

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from ..config import WHATSAPP_VERIFY_TOKEN

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook", response_class=PlainTextResponse)
def verificar(modo: str = Query("", alias="hub.mode"),
              token: str = Query("", alias="hub.verify_token"),
              reto: str = Query("", alias="hub.challenge")):
    if modo == "subscribe" and WHATSAPP_VERIFY_TOKEN and hmac.compare_digest(token, WHATSAPP_VERIFY_TOKEN):
        return reto
    raise HTTPException(403, "Token de verificación inválido")


@router.post("/webhook")
def recibir():
    return {"estado": "recibido"}
