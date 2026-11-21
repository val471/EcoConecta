// EcoConecta · ÚNICO punto de comunicación con el backend.
// Las pantallas NUNCA llaman a fetch: solo a las funciones de `api`.
// Cuando Persona A termine el backend: USAR_MOCK = false y ajustar RUTAS según el contrato.

const USAR_MOCK = false;
const API_BASE = "/api";

/* ========================= Sesión (compartida con auth.js) ========================= */
const Sesion = {
  get() { try { return JSON.parse(localStorage.getItem("eco_sesion")); } catch { return null; } },
  set(s) { localStorage.setItem("eco_sesion", JSON.stringify(s)); },
  clear() { localStorage.removeItem("eco_sesion"); },
};

/* ========================= Modo real (fetch) ========================= */
async function http(metodo, ruta, cuerpo) {
  const s = Sesion.get();
  const res = await fetch(API_BASE + ruta, {
    method: metodo,
    headers: {
      "Content-Type": "application/json",
      ...(s?.token ? { Authorization: `Bearer ${s.token}` } : {}),
    },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  if (res.status === 401) { Sesion.clear(); location.href = "login.html"; throw new Error("Sesión vencida"); }
  const datos = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = datos.detail; // FastAPI: texto, o lista de errores de validación (422)
    throw new Error(typeof d === "string" ? d : Array.isArray(d) ? "Revisa que los datos estén completos y correctos." : datos.mensaje || "No se pudo completar la acción");
  }
  return datos;
}

const apiReal = {
  login: (email, password) => http("POST", "/auth/login", { email, password }),
  crearSolicitud: (d) => http("POST", "/solicitudes", d),
  misSolicitudes: () => http("GET", "/solicitudes/mias"),
  getSolicitud: (id) => http("GET", `/solicitudes/${id}`),
  bandeja: (estado) => http("GET", `/coordinador/bandeja${estado ? `?estado=${estado}` : ""}`),
  resumen: () => http("GET", "/coordinador/resumen"),
  recolectores: () => http("GET", "/coordinador/recolectores"),
  asignar: (id, recolector_id) => http("POST", `/coordinador/solicitudes/${id}/asignar`, { recolector_id }),
  programar: (id, d) => http("POST", `/coordinador/solicitudes/${id}/programar`, d),
  cancelar: (id, motivo) => http("POST", `/coordinador/solicitudes/${id}/cancelar`, { motivo }),
  misAsignaciones: () => http("GET", "/recolector/asignaciones"),
  registrarRecoleccion: (id, d) => http("POST", `/recolector/solicitudes/${id}/recoleccion`, d),
  getReglas: () => http("GET", "/admin/reglas-puntos"),
  setReglas: (reglas) => http("PUT", "/admin/reglas-puntos", reglas),
  getUsuarios: () => http("GET", "/admin/usuarios"),
  setPiloto: (id, es_piloto) => http("PATCH", `/admin/usuarios/${id}/piloto`, { es_piloto }),
  puntosUsuario: () => http("GET", "/solicitudes/puntos"),
};

/* ========================= Modo simulado (localStorage) ========================= */
const DB_KEY = "eco_mock_db";
const ahora = () => new Date().toISOString();

function dbInicial() {
  return {
    seq: 2,
    usuarios: [
      { id: 1, nombre: "Ana Pérez (negocio)", email: "ana@demo.co", rol: "solicitante", tipo: "unidad_productiva", es_piloto: true, telefono: "3000000001" },
      { id: 2, nombre: "Luis Gómez (hogar)", email: "luis@demo.co", rol: "solicitante", tipo: "hogar", es_piloto: true, telefono: "3000000002" },
      { id: 3, nombre: "Coord. Huerteros", email: "coordh@demo.co", rol: "coord_huerteros" },
      { id: 4, nombre: "Coord. Recicladores", email: "coordr@demo.co", rol: "coord_recicladores" },
      { id: 5, nombre: "Huertero Carlos", email: "huertero@demo.co", rol: "recolector", flujo: "organico" },
      { id: 6, nombre: "Huertera María", email: "huertera@demo.co", rol: "recolector", flujo: "organico" },
      { id: 7, nombre: "Reciclador Jorge", email: "reciclador@demo.co", rol: "recolector", flujo: "reciclable" },
      { id: 8, nombre: "Administrador", email: "admin@demo.co", rol: "admin" },
      { id: 9, nombre: "Vecina sin habilitar", email: "vecina@demo.co", rol: "solicitante", tipo: "hogar", es_piloto: false, telefono: "3000000009" },
    ],
    reglas: [
      { tipo_residuo: "organico", unidad: "kg", puntos_por_unidad: 5 },
      { tipo_residuo: "plastico", unidad: "kg", puntos_por_unidad: 8 },
      { tipo_residuo: "carton_papel", unidad: "kg", puntos_por_unidad: 4 },
      { tipo_residuo: "vidrio", unidad: "kg", puntos_por_unidad: 3 },
      { tipo_residuo: "metal", unidad: "kg", puntos_por_unidad: 10 },
    ],
    solicitudes: [],
    puntos: [],
  };
}
function leerDB() {
  let db = JSON.parse(localStorage.getItem(DB_KEY) || "null");
  if (!db) { db = dbInicial(); guardarDB(db); }
  return db;
}
const guardarDB = (db) => localStorage.setItem(DB_KEY, JSON.stringify(db));
const reiniciarMock = () => { localStorage.removeItem(DB_KEY); location.reload(); };
const yo = () => { const s = Sesion.get(); if (!s) throw new Error("Debes iniciar sesión"); return s.usuario; };
const espera = (v) => new Promise((r) => setTimeout(() => r(structuredClone(v)), 150));

function cambiarEstado(sol, nuevo, por, nota = "") {
  if (!TRANSICIONES[sol.estado].includes(nuevo))
    throw new Error(`No se puede pasar de "${ESTADOS[sol.estado]}" a "${ESTADOS[nuevo]}"`);
  sol.estado = nuevo;
  sol.historial.push({ estado: nuevo, fecha: ahora(), por, nota }); // RN-04
}

// RN-07: lo que ve cada perfil
function vistaSolicitud(sol, db, vista) {
  const u = db.usuarios.find((x) => x.id === sol.usuario_id);
  const copia = { ...sol, nombre_usuario: u?.nombre };
  if (vista === "usuario") { delete copia.contacto; }
  return copia;
}

function calcularPuntos(db, tipo_residuo, cantidad, unidad) {
  const regla = db.reglas.find((r) => r.tipo_residuo === tipo_residuo && r.unidad === unidad);
  if (!regla) return { total: 0, explicacion: "Sin regla de puntos para este material; no se asignan puntos." };
  const total = Math.round(cantidad * regla.puntos_por_unidad);
  return { total, explicacion: `${cantidad} ${unidad} de ${etiquetaResiduo(tipo_residuo).toLowerCase()} × ${regla.puntos_por_unidad} puntos/${unidad} = ${total} puntos` };
}

const apiMock = {
  async login(email, password) {
    const db = leerDB();
    const u = db.usuarios.find((x) => x.email === email.trim().toLowerCase());
    if (!u || password !== "demo123") throw new Error("Correo o contraseña incorrectos");
    return espera({ token: "mock-" + u.id, usuario: u });
  },

  async crearSolicitud(d) {
    const db = leerDB(); const u = yo();
    // RN-08: solo usuarios piloto habilitados pueden solicitar
    if (!db.usuarios.find((x) => x.id === u.id)?.es_piloto)
      throw new Error("Tu cuenta todavía no está habilitada para solicitar recolecciones. Habla con el administrador.");
    if (!d.flujo || !["organico", "reciclable"].includes(d.flujo)) throw new Error("Elige el tipo de residuo");
    db.seq += 1;
    const sol = {
      id: "SOL-" + String(db.seq).padStart(4, "0"),
      usuario_id: u.id, flujo: d.flujo, // RN-01: el flujo define el coordinador
      tipo_generador: d.tipo_generador, direccion: d.direccion, contacto: d.contacto,
      observaciones: d.observaciones || "", preferencia_horaria: d.preferencia_horaria || "",
      estado: "recibida", recolector_id: null, programacion: null, recoleccion: null, puntos: null,
      creada: ahora(), historial: [{ estado: "recibida", fecha: ahora(), por: u.nombre, nota: "Solicitud registrada" }],
    };
    db.solicitudes.push(sol); guardarDB(db);
    return espera(vistaSolicitud(sol, db, "usuario"));
  },

  async misSolicitudes() {
    const db = leerDB(); const u = yo();
    return espera(db.solicitudes.filter((s) => s.usuario_id === u.id).map((s) => vistaSolicitud(s, db, "usuario")).reverse());
  },
  async getSolicitud(id) {
    const db = leerDB(); const u = yo();
    const s = db.solicitudes.find((x) => x.id === id);
    if (!s || s.usuario_id !== u.id) throw new Error("Solicitud no encontrada");
    return espera(vistaSolicitud(s, db, "usuario"));
  },
  async puntosUsuario() {
    const db = leerDB(); const u = yo();
    const movs = db.puntos.filter((p) => p.usuario_id === u.id);
    return espera({ total: movs.reduce((a, p) => a + p.puntos, 0), movimientos: movs.reverse() });
  },

  // --- Coordinador: solo ve su flujo (RN-01 / RN-07)
  async bandeja(estado) {
    const db = leerDB(); const u = yo();
    const flujo = u.rol === "coord_huerteros" ? "organico" : "reciclable";
    let lista = db.solicitudes.filter((s) => s.flujo === flujo);
    if (estado === "pendientes") lista = lista.filter((s) => ["recibida", "en_revision"].includes(s.estado));
    else if (estado) lista = lista.filter((s) => s.estado === estado);
    return espera(lista.map((s) => {
      const r = vistaSolicitud(s, db, "operativo");
      r.recolector_nombre = db.usuarios.find((x) => x.id === s.recolector_id)?.nombre || null;
      return r;
    }).reverse());
  },
  async resumen() {
    const db = leerDB(); const u = yo();
    const flujo = u.rol === "coord_huerteros" ? "organico" : "reciclable";
    const lista = db.solicitudes.filter((s) => s.flujo === flujo);
    const por_estado = {}; Object.keys(ESTADOS).forEach((e) => (por_estado[e] = lista.filter((s) => s.estado === e).length));
    return espera({ flujo, total: lista.length, por_estado });
  },
  async recolectores() {
    const db = leerDB(); const u = yo();
    const flujo = u.rol === "coord_huerteros" ? "organico" : "reciclable";
    return espera(db.usuarios.filter((x) => x.rol === "recolector" && x.flujo === flujo));
  },
  async asignar(id, recolector_id) {
    const db = leerDB(); const u = yo();
    const s = db.solicitudes.find((x) => x.id === id);
    const r = db.usuarios.find((x) => x.id === Number(recolector_id));
    if (!s || !r) throw new Error("Datos inválidos");
    if (s.estado === "recibida") cambiarEstado(s, "en_revision", u.nombre, "Revisada por el coordinador");
    cambiarEstado(s, "asignada", u.nombre, `Asignada a ${r.nombre}`); // RN-03
    s.recolector_id = r.id; s.coordinador_id = u.id; guardarDB(db);
    return espera(s);
  },
  async programar(id, { fecha, hora, persona }) {
    const db = leerDB(); const u = yo();
    if (!fecha || !hora || !persona) throw new Error("Falta día, hora o persona encargada"); // RN-02
    const s = db.solicitudes.find((x) => x.id === id);
    if (!s) throw new Error("Solicitud no encontrada");
    cambiarEstado(s, "programada", u.nombre, `Programada: ${formatDia(fecha, hora)}, a cargo de ${persona}`);
    s.programacion = { fecha, hora, persona }; guardarDB(db);
    return espera(s);
  },
  async cancelar(id, motivo) {
    const db = leerDB(); const u = yo();
    const s = db.solicitudes.find((x) => x.id === id);
    cambiarEstado(s, "cancelada", u.nombre, motivo || "Cancelada"); guardarDB(db);
    return espera(s);
  },

  // --- Recolector: solo ve lo asignado a él
  async misAsignaciones() {
    const db = leerDB(); const u = yo();
    return espera(db.solicitudes.filter((s) => s.recolector_id === u.id && !["cancelada"].includes(s.estado))
      .map((s) => vistaSolicitud(s, db, "operativo")).reverse());
  },
  async registrarRecoleccion(id, { tipo_residuo, cantidad, unidad }) {
    const db = leerDB(); const u = yo();
    const s = db.solicitudes.find((x) => x.id === id && x.recolector_id === u.id);
    if (!s) throw new Error("Solicitud no asignada a ti");
    if (!(cantidad > 0)) throw new Error("Indica una cantidad mayor a 0");
    cambiarEstado(s, "recolectada", u.nombre, "Recolección registrada");
    s.recoleccion = { tipo_residuo, cantidad, unidad, fecha: ahora() };
    s.puntos = calcularPuntos(db, tipo_residuo, cantidad, unidad); // RN-05: solo después del cierre
    db.puntos.push({ usuario_id: s.usuario_id, solicitud_id: s.id, puntos: s.puntos.total, explicacion: s.puntos.explicacion, fecha: ahora() });
    guardarDB(db);
    return espera(s);
  },

  // --- Admin
  async getReglas() { return espera(leerDB().reglas); },
  async setReglas(reglas) { const db = leerDB(); db.reglas = reglas; guardarDB(db); return espera(reglas); },
  async getUsuarios() { return espera(leerDB().usuarios); },
  async setPiloto(id, es_piloto) {
    const db = leerDB(); const u = db.usuarios.find((x) => x.id === id);
    if (u) u.es_piloto = es_piloto; guardarDB(db); return espera(u);
  },
};

const api = USAR_MOCK ? apiMock : apiReal;