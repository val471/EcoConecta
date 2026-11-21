// EcoConecta · constantes compartidas. Mismos nombres que usa el backend (acordar con Persona A).

const ROLES = {
  SOLICITANTE: "solicitante",
  COORD_HUERTEROS: "coord_huerteros",
  COORD_RECICLADORES: "coord_recicladores",
  RECOLECTOR: "recolector",
  ADMIN: "admin",
};

const FLUJOS = {
  organico:  { etiqueta: "Orgánico",  recolector: "Huertero",   coordinador: "Coordinador de huerteros" },
  reciclable:{ etiqueta: "Reciclable", recolector: "Reciclador", coordinador: "Coordinador de recicladores" },
};

const ESTADOS = {
  recibida:    "Recibida",
  en_revision: "En revisión",
  asignada:    "Asignada",
  programada:  "Programada",
  recolectada: "Recolectada",
  cancelada:   "Cancelada",
};

// Transiciones permitidas (RN-02, RN-05)
const TRANSICIONES = {
  recibida:    ["en_revision", "asignada", "cancelada"],
  en_revision: ["asignada", "cancelada"],
  asignada:    ["programada", "cancelada"],
  programada:  ["recolectada", "cancelada"],
  recolectada: [],
  cancelada:   [],
};

const TIPOS_GENERADOR = { hogar: "Hogar", unidad_productiva: "Unidad productiva (negocio)" };

// Menú de la barra superior según el rol
const MENU = {
  publico: [
    { href: "index.html", texto: "Inicio" },
    { href: "educacion.html", texto: "Aprende" },
    { href: "asistente.html", texto: "Asistente" },
  ],
  solicitante: [
    { href: "index.html", texto: "Inicio" },
    { href: "educacion.html", texto: "Aprende" },
    { href: "asistente.html", texto: "Asistente" },
    { href: "solicitud.html", texto: "Solicitar recolección" },
    { href: "mis-solicitudes.html", texto: "Mis solicitudes" },
  ],
  coord_huerteros: [{ href: "coordinador.html", texto: "Solicitudes" }, { href: "educacion.html", texto: "Aprender" }],
  coord_recicladores: [{ href: "coordinador.html", texto: "Solicitudes" }, { href: "educacion.html", texto: "Aprender" }],
  recolector: [{ href: "recolector.html", texto: "Mis recolecciones" }, { href: "educacion.html", texto: "Aprender" }],
  admin: [
    { href: "admin.html", texto: "Administrar" },
    { href: "educacion.html", texto: "Aprender" },
  ],
};

// Página de inicio de cada rol después de iniciar sesión
const HOME_POR_ROL = {
  solicitante: "mis-solicitudes.html",
  coord_huerteros: "coordinador.html",
  coord_recicladores: "coordinador.html",
  recolector: "recolector.html",
  admin: "admin.html",
};

// Aviso obligatorio: los puntos NO son reglas oficiales de FSD
const AVISO_PUNTOS =
  "Valores de ejemplo configurables por el administrador. No son reglas oficiales de la Fundación Santo Domingo.";

// Iconos de Bootstrap Icons (una sola biblioteca de línea, como pide el manual)
const ICONOS_ESTADO = {
  recibida: "bi-inbox", en_revision: "bi-search", asignada: "bi-person-check",
  programada: "bi-calendar-check", recolectada: "bi-check-circle", cancelada: "bi-x-circle",
};
const ICONOS_FLUJO = { organico: "bi-flower1", reciclable: "bi-recycle" };

// Tipos de residuo que se registran al cerrar la recolección (claves fijas, deben coincidir con el backend)
const TIPOS_RESIDUO = {
  organico:     { etiqueta: "Orgánico",        flujo: "organico" },
  plastico:     { etiqueta: "Plástico",        flujo: "reciclable" },
  carton_papel: { etiqueta: "Cartón y papel",  flujo: "reciclable" },
  vidrio:       { etiqueta: "Vidrio",          flujo: "reciclable" },
  metal:        { etiqueta: "Metal",           flujo: "reciclable" },
};
