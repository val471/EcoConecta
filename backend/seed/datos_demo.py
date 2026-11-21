"""Datos FICTICIOS para la demostración. No cargar información personal real.

Ejecutar manualmente:  python -m backend.seed.datos_demo
Es idempotente: no duplica lo que ya existe.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Contenido, ReglaPuntos, Usuario
from backend.security import passwords

PASSWORD_DEMO = "Demo2026!"  # solo para la demo; cambiar o desactivar CARGAR_DEMO fuera de ella

USUARIOS = [
    # nombre, email, rol, colectivo, tipo_solicitante, teléfono ficticio, dirección ficticia
    ("Administrador Demo", "admin@ecoconecta.demo", "administrador", None, None, None, None),
    ("Coordinadora Huerteros", "coord.huerteros@ecoconecta.demo", "coordinador_huerteros", "huerteros", None, "3000000011", None),
    ("Coordinador Recicladores", "coord.recicladores@ecoconecta.demo", "coordinador_recicladores", "recicladores", None, "3000000012", None),
    ("Huertero Uno", "huertero1@ecoconecta.demo", "recolector", "huerteros", None, "3000000021", None),
    ("Huertera Dos", "huertero2@ecoconecta.demo", "recolector", "huerteros", None, "3000000022", None),
    ("Reciclador Uno", "reciclador1@ecoconecta.demo", "recolector", "recicladores", None, "3000000031", None),
    ("Restaurante La Huerta (demo)", "unidad.productiva@ecoconecta.demo", "solicitante", None, "unidad_productiva",
     "3000000041", "Calle Ficticia 1 # 2-3, Villas de San Pablo"),
    ("Hogar Ejemplo (demo)", "hogar@ecoconecta.demo", "solicitante", None, "hogar",
     "3000000042", "Carrera Ficticia 4 # 5-6, Villas de San Pablo"),
]

# RN-06: valores de EJEMPLO, no oficiales de FSD
REGLAS = [
    ("organico", "kg", 2.0, "Ejemplo: 2 puntos por kg de orgánicos"),
    ("reciclable", "kg", 1.0, "Ejemplo: 1 punto por kg de reciclables"),
    ("reciclable", "unidad", 0.5, "Ejemplo: 0,5 puntos por unidad de reciclables"),
]

CONTENIDOS = [
    ("¿Por qué separar los residuos?", "general", "Separar en la fuente reduce lo que llega al relleno y da trabajo a huerteros y recicladores.",
     "Cuando separas en casa o en tu negocio, los orgánicos se vuelven abono para las huertas y los reciclables vuelven a la industria. Separar es el primer paso."),
    ("Qué es un residuo orgánico", "organico", "Cáscaras, restos de comida, poda y borra de café.",
     "Son residuos de origen vegetal o animal que se descomponen. Guárdalos en un recipiente aparte, sin bolsas plásticas ni líquidos de más."),
    ("Cómo preparar los orgánicos para la recolección", "organico", "Recipiente cerrado, sin plásticos y sin mezclar.",
     "Usa un balde con tapa. Evita mezclar con vidrio, plástico o aceite. Escurre los líquidos para reducir olores."),
    ("Qué es un residuo reciclable", "reciclable", "Plástico, cartón, papel, vidrio y metal limpios y secos.",
     "Enjuaga envases, aplana cajas de cartón y separa por material cuando sea posible. Lo sucio o mojado pierde valor."),
    ("Cómo preparar los reciclables", "reciclable", "Limpios, secos y aplastados.",
     "Retira restos de comida, aplasta botellas y latas, y guarda todo en una bolsa o caja aparte de los orgánicos."),
    ("Cómo funciona EcoConecta", "general", "Solicitas, un coordinador asigna, se programa, se recolecta y ganas puntos.",
     "1) Haces la solicitud. 2) Llega al colectivo correcto. 3) El coordinador la revisa y asigna a una persona. "
     "4) Se registra día, hora y encargado. 5) Se recoge y se registra. 6) Recibes puntos (valores de ejemplo)."),
]


def cargar_demo(db: Session) -> None:
    for nombre, email, rol, colectivo, tipo, telefono, direccion in USUARIOS:
        if db.scalar(select(Usuario).where(Usuario.email == email)):
            continue
        db.add(Usuario(nombre=nombre, email=email, rol=rol, colectivo=colectivo, tipo_solicitante=tipo,
                       telefono=telefono, direccion=direccion, password_hash=passwords.hashear(PASSWORD_DEMO),
                       es_piloto=True))
    if db.scalar(select(ReglaPuntos).limit(1)) is None:
        for tipo, unidad, ppu, desc in REGLAS:
            db.add(ReglaPuntos(tipo_residuo=tipo, unidad=unidad, puntos_por_unidad=ppu, descripcion=desc))
    if db.scalar(select(Contenido).limit(1)) is None:
        for titulo, categoria, resumen, cuerpo in CONTENIDOS:
            db.add(Contenido(titulo=titulo, categoria=categoria, resumen=resumen, cuerpo=cuerpo))
    db.commit()


if __name__ == "__main__":
    from backend.database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as sesion:
        cargar_demo(sesion)
    print("Datos demo cargados.")
