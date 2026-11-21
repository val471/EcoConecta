"""Convierte los modelos al formato JSON que espera el frontend (js/api.js)."""
from datetime import datetime


def iso(dt):
    if dt is None:
        return None
    if isinstance(dt, datetime) and dt.tzinfo is None:
        return dt.isoformat() + "+00:00"
    return dt.isoformat()


def usuario_dict(u) -> dict:
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol, "flujo": u.flujo,
            "tipo": u.tipo, "telefono": u.telefono, "es_piloto": bool(u.es_piloto)}


def solicitud_dict(s, operativo: bool = False) -> dict:
    a, p, r, m = s.asignacion, s.programacion, s.recoleccion, s.movimiento
    d = {
        "id": s.codigo, "flujo": s.flujo, "estado": s.estado, "creada": iso(s.creada),
        "tipo_generador": s.tipo_generador, "direccion": s.direccion,
        "observaciones": s.observaciones or "", "preferencia_horaria": s.preferencia_horaria or "",
        "nombre_usuario": s.usuario.nombre if s.usuario else None,
        "recolector_id": a.recolector_id if a else None,
        "recolector_nombre": a.recolector.nombre if a and a.recolector else None,
        "programacion": {"fecha": p.fecha.isoformat(), "hora": p.hora, "persona": p.persona} if p else None,
        "recoleccion": {"tipo_residuo": r.tipo_residuo, "cantidad": float(r.cantidad), "unidad": r.unidad,
                        "fecha": iso(r.fecha)} if r else None,
        "puntos": {"total": m.puntos, "explicacion": m.explicacion} if m else None,
        "historial": [{"estado": h.estado, "fecha": iso(h.fecha), "por": h.por, "nota": h.nota or ""}
                      for h in s.historial],
    }
    if operativo:                     # RN-07: el contacto solo lo ven quienes atienden la solicitud
        d["contacto"] = s.contacto
    return d
