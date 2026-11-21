"""Datos de demostración. Solo se cargan si la base está vacía (se ejecuta solo al arrancar).
Todo es FICTICIO: no cargar información personal real sin autorización."""
from ..config import DEMO_PASSWORD
from ..constantes import REGLAS_PUNTOS_EJEMPLO
from ..models import Contenido, ReglaPuntos, Usuario
from ..security.passwords import hash_password

USUARIOS = [
    # (nombre, email, rol, flujo, tipo, telefono, es_piloto)   El orden fija los ids 1..9
    ("Ana Pérez (negocio)", "ana@demo.co", "solicitante", None, "unidad_productiva", "3000000001", True),
    ("Luis Gómez (hogar)", "luis@demo.co", "solicitante", None, "hogar", "3000000002", True),
    ("Coord. Huerteros", "coordh@demo.co", "coord_huerteros", None, None, None, False),
    ("Coord. Recicladores", "coordr@demo.co", "coord_recicladores", None, None, None, False),
    ("Huertero Carlos", "huertero@demo.co", "recolector", "organico", None, None, False),
    ("Huertera María", "huertera@demo.co", "recolector", "organico", None, None, False),
    ("Reciclador Jorge", "reciclador@demo.co", "recolector", "reciclable", None, None, False),
    ("Administrador", "admin@demo.co", "admin", None, None, None, False),
    ("Vecina sin habilitar", "vecina@demo.co", "solicitante", None, "hogar", "3000000009", False),
]

# Contenido de EJEMPLO para que la pantalla de educación tenga qué mostrar. Debe ser revisado por el equipo.
CONTENIDOS = [
    ("separacion", "Cómo separar tus residuos en casa",
     "Tres grupos sencillos: orgánicos, reciclables y el resto.",
     "Orgánicos: restos de comida, cáscaras, borra de café, hojas y poda.\n"
     "Reciclables: plástico, cartón, papel, vidrio y metal, limpios y secos.\n"
     "El resto: lo que no se puede aprovechar, como papel higiénico o servilletas muy sucias.\n"
     "Si tienes duda con un residuo, pregúntale al asistente."),
    ("organicos", "Residuos orgánicos y la huerta comunitaria",
     "Lo que sobra de tu cocina puede volver como abono.",
     "Los huerteros recogen los residuos orgánicos, los clasifican y los convierten en compost, un abono natural que se usa en la huerta comunitaria.\n"
     "Entre más limpios lleguen, sin plástico ni vidrio mezclado, mejor abono se produce."),
    ("reciclables", "Prepara tus reciclables",
     "Limpios, secos y separados valen más.",
     "Enjuaga los envases, déjalos secar y aplástalos para que ocupen menos espacio.\n"
     "No los mezcles con residuos orgánicos. Los recicladores de oficio los recogen y los llevan a aprovechamiento."),
    ("horarios", "Horarios y rutas de recolección",
     "El día y la hora los acuerda el coordinador contigo.",
     "La ruta ideal que se propuso con la comunidad es recolección diaria para negocios y día de por medio para hogares.\n"
     "Cuando haces una solicitud, un coordinador la revisa y te confirma el día, la hora y la persona que irá. Lo ves en «Mis solicitudes»."),
    ("plataforma", "Cómo solicitar una recolección",
     "Cuatro pasos: aprende, solicita, programamos y recogemos.",
     "1. Elige si tus residuos son orgánicos o reciclables.\n2. Escribe tu dirección y tu celular.\n"
     "3. Espera a que el coordinador programe el día y la hora.\n4. Entrega tus residuos y recibe tus puntos."),
    ("puntos", "Cómo ganas puntos",
     "Los puntos reconocen tu participación.",
     "Cuando el recolector registra lo que entregaste, ganas puntos según el material y los kilos.\n"
     "Los valores de los puntos son de ejemplo y los puede ajustar el administrador; no son reglas oficiales de la Fundación Santo Domingo."),
]


def cargar_datos_demo(db) -> None:
    if db.query(Usuario).count() == 0:
        clave = hash_password(DEMO_PASSWORD)          # una sola vez: es más rápido
        for nombre, email, rol, flujo, tipo, tel, piloto in USUARIOS:
            db.add(Usuario(nombre=nombre, email=email, password_hash=clave, rol=rol, flujo=flujo,
                           tipo=tipo, telefono=tel, es_piloto=piloto))
        db.commit()
    if db.query(ReglaPuntos).count() == 0:
        for tipo, unidad, puntos in REGLAS_PUNTOS_EJEMPLO:
            db.add(ReglaPuntos(tipo_residuo=tipo, unidad=unidad, puntos_por_unidad=puntos))
        db.commit()
    if db.query(Contenido).count() == 0:
        for i, (cat, titulo, resumen, cuerpo) in enumerate(CONTENIDOS):
            db.add(Contenido(categoria=cat, titulo=titulo, resumen=resumen, cuerpo=cuerpo, orden=i))
        db.commit()
