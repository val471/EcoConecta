// EcoConecta · bandeja del coordinador (huerteros u recicladores). Solo ve las solicitudes de su flujo.
const usuario = requerirRol(["coord_huerteros", "coord_recicladores"]);
renderNavbar();

const $ = (id) => document.getElementById(id);
const FLUJO = usuario.rol === "coord_huerteros" ? "organico" : "reciclable";
const modal = (id) => bootstrap.Modal.getOrCreateInstance($(id));

let todas = [];        // todas las solicitudes de mi flujo
let recolectores = []; // personas de mi colectivo
let filtro = "pendientes";
let periodo = "todo";
let actual = null;     // solicitud sobre la que se está actuando

const FILTROS = {
  pendientes:  { texto: "Pendientes",  icono: "bi-inbox",          estados: ["recibida", "en_revision"], ayuda: "Solicitudes nuevas: falta asignar a una persona.", vacio: "No hay solicitudes pendientes. ¡Buen trabajo!" },
  asignadas:   { texto: "Asignadas",   icono: "bi-person-check",   estados: ["asignada"],                ayuda: "Ya tienen persona asignada: falta acordar día y hora.", vacio: "No hay solicitudes por programar." },
  programadas: { texto: "Programadas", icono: "bi-calendar-check", estados: ["programada"],              ayuda: "Tienen día, hora y persona. Esperan la recolección.", vacio: "No hay recolecciones programadas." },
  atendidas:   { texto: "Atendidas",   icono: "bi-check-circle",   estados: ["recolectada"],             ayuda: "Recolecciones ya realizadas, con puntos asignados.", vacio: "Todavía no hay recolecciones atendidas." },
  todas:       { texto: "Todas",       icono: "bi-list-ul",        estados: null,                        ayuda: "Historial completo, incluidas las canceladas.", vacio: "Todavía no hay solicitudes." },
};

$("subtitulo").innerHTML = `${badgeFlujo(FLUJO)} &nbsp; Residuos ${FLUJOS[FLUJO].etiqueta.toLowerCase()}s · los recoge ${FLUJOS[FLUJO].recolector.toLowerCase()}`;

/* ---------- Periodo y conteos ---------- */
function enPeriodo(s) {
  if (periodo === "todo") return true;
  const f = new Date(s.creada), hoy = new Date();
  if (periodo === "hoy") return f.toDateString() === hoy.toDateString();
  if (periodo === "semana") return hoy - f <= 7 * 24 * 3600 * 1000;
  if (periodo === "mes") return f.getMonth() === hoy.getMonth() && f.getFullYear() === hoy.getFullYear();
  return true;
}
const delFiltro = (s, f) => !FILTROS[f].estados || FILTROS[f].estados.includes(s.estado);

function pintarFiltros() {
  const base = todas.filter(enPeriodo);
  $("filtros").innerHTML = Object.entries(FILTROS).map(([k, f]) => {
    const n = base.filter((s) => delFiltro(s, k)).length;
    const activo = k === filtro;
    return `<button type="button" class="btn ${activo ? "btn-eco" : "btn-outline-eco"}" data-filtro="${k}" aria-pressed="${activo}">
      <i class="bi ${f.icono}" aria-hidden="true"></i> ${f.texto} <span class="badge text-bg-light ms-1">${n}</span></button>`;
  }).join("");
  $("ayuda-filtro").textContent = FILTROS[filtro].ayuda;
}

/* ---------- Tarjetas ---------- */
function tarjeta(s) {
  const tel = esc(s.contacto || "");
  const prog = s.programacion
    ? `<dl class="bloque-programacion mt-3 mb-0">
         <dt><i class="bi bi-calendar-check" aria-hidden="true"></i> Día y hora</dt><dd class="dato">${esc(formatDia(s.programacion.fecha, s.programacion.hora))}</dd>
         <dt><i class="bi bi-person-check" aria-hidden="true"></i> Persona encargada</dt><dd class="mb-0">${esc(s.programacion.persona)}</dd>
       </dl>` : "";
  const rec = s.recoleccion
    ? `<div class="mt-3">Recolectado: <strong>${esc(s.recoleccion.cantidad)} ${esc(s.recoleccion.unidad)}</strong> de ${esc(etiquetaResiduo(s.recoleccion.tipo_residuo).toLowerCase())}
       ${s.puntos ? " · " + badgePuntos(s.puntos.total) : ""}</div>` : "";

  let botones = "";
  if (["recibida", "en_revision"].includes(s.estado))
    botones = `<button class="btn btn-eco" data-accion="asignar" data-id="${s.id}"><i class="bi bi-person-plus" aria-hidden="true"></i> Asignar ${FLUJOS[FLUJO].recolector.toLowerCase()}</button>`;
  else if (s.estado === "asignada")
    botones = `<button class="btn btn-eco" data-accion="programar" data-id="${s.id}"><i class="bi bi-calendar-plus" aria-hidden="true"></i> Programar día y hora</button>`;
  if (!["recolectada", "cancelada"].includes(s.estado))
    botones += ` <button class="btn btn-outline-eco" data-accion="cancelar" data-id="${s.id}"><i class="bi bi-x-circle" aria-hidden="true"></i> Cancelar</button>`;

  return `<article class="eco-card destacada">
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
      <span class="id-solicitud" style="font-size:1.2rem">${esc(s.id)}</span>
      <span>${badgeEstado(s.estado)}</span>
    </div>
    <div class="row g-2 mt-2">
      <div class="col-md-6"><i class="bi bi-geo-alt" aria-hidden="true"></i> <strong>${esc(s.direccion)}</strong><br>
        <span class="texto-suave">${esc(TIPOS_GENERADOR[s.tipo_generador] || s.tipo_generador)} · ${esc(s.nombre_usuario || "")}</span></div>
      <div class="col-md-6"><i class="bi bi-telephone" aria-hidden="true"></i> <a class="dato fw-semibold" href="tel:${tel}">${tel}</a><br>
        <span class="texto-suave"><i class="bi bi-clock" aria-hidden="true"></i> Prefiere: ${esc(s.preferencia_horaria || "cualquier hora")}</span></div>
    </div>
    ${s.observaciones ? `<div class="mt-2"><i class="bi bi-chat-left-text" aria-hidden="true"></i> ${esc(s.observaciones)}</div>` : ""}
    ${s.recolector_nombre ? `<div class="mt-2"><i class="bi bi-person" aria-hidden="true"></i> ${FLUJOS[FLUJO].recolector}: <strong>${esc(s.recolector_nombre)}</strong></div>` : ""}
    ${prog}${rec}
    ${botones ? `<div class="d-flex flex-wrap gap-2 mt-3">${botones}</div>` : ""}
    <details class="mt-3"><summary>Ver historial</summary>${lineaTiempoHTML(s.historial)}</details>
  </article>`;
}

function pintarLista() {
  let lista = todas.filter(enPeriodo).filter((s) => delFiltro(s, filtro));
  // Pendientes: las más antiguas primero (llevan más tiempo esperando)
  lista.sort((a, b) => filtro === "pendientes" ? new Date(a.creada) - new Date(b.creada) : new Date(b.creada) - new Date(a.creada));
  $("lista").innerHTML = lista.length ? lista.map(tarjeta).join("")
    : `<div class="eco-card text-center py-4">${FILTROS[filtro].vacio}</div>`;
  $("lista").setAttribute("aria-busy", "false");
}

function pintar() { pintarFiltros(); pintarLista(); }

async function cargar() {
  try {
    [todas, recolectores] = await Promise.all([api.bandeja(), api.recolectores()]);
    pintar();
  } catch (e) {
    mostrarAlerta("No pudimos cargar las solicitudes. " + e.message, "danger");
    $("lista").innerHTML = `<button class="btn btn-outline-eco" onclick="cargar()">Intentar de nuevo</button>`;
  }
}

/* ---------- Eventos de filtros y acciones ---------- */
$("filtros").addEventListener("click", (e) => {
  const b = e.target.closest("[data-filtro]"); if (!b) return;
  filtro = b.dataset.filtro; pintar();
});
$("periodo").addEventListener("change", (e) => { periodo = e.target.value; pintar(); });

$("lista").addEventListener("click", (e) => {
  const b = e.target.closest("[data-accion]"); if (!b) return;
  actual = todas.find((s) => s.id === b.dataset.id);
  if (!actual) return;
  ({ asignar: abrirAsignar, programar: abrirProgramar, cancelar: abrirCancelar })[b.dataset.accion]();
});

const resumenSol = (s) => `<strong>${esc(s.id)}</strong> · ${esc(s.direccion)}`;

/* ---------- Asignar ---------- */
function abrirAsignar() {
  $("alerta-asignar").innerHTML = "";
  $("resumen-asignar").innerHTML = resumenSol(actual);
  $("lbl-recolector").textContent = `${FLUJOS[FLUJO].recolector} que hará la recolección`;
  $("sel-recolector").innerHTML = `<option value="">Elige una persona</option>` +
    recolectores.map((r) => `<option value="${r.id}">${esc(r.nombre)}</option>`).join("");
  $("btn-asignar").disabled = true;
  if (!recolectores.length) $("alerta-asignar").innerHTML = `<div class="alert alert-warning">No hay personas registradas en tu colectivo. Pide al administrador que las agregue.</div>`;
  modal("modal-asignar").show();
}
$("sel-recolector").addEventListener("change", (e) => { $("btn-asignar").disabled = !e.target.value; });

$("btn-asignar").addEventListener("click", async () => {
  const id = actual.id, rid = $("sel-recolector").value;
  $("btn-asignar").disabled = true;
  try {
    await api.asignar(id, rid);
    modal("modal-asignar").hide();
    await cargar();
    mostrarAlerta(`Solicitud ${id} asignada. Ahora acuerda el día y la hora.`, "success");
    actual = todas.find((s) => s.id === id);
    if (actual?.estado === "asignada") setTimeout(abrirProgramar, 350);   // flujo continuo: asignar → programar
  } catch (e) {
    mostrarAlerta("No se pudo asignar. " + e.message, "danger", "alerta-asignar");
    $("btn-asignar").disabled = false;
  }
});

/* ---------- Programar (RN-02: no se guarda incompleto) ---------- */
function opcionesHora() {
  const o = ['<option value="">Elige la hora</option>'];
  for (let m = 6 * 60; m <= 18 * 60; m += 30) {
    const h = Math.floor(m / 60), mm = String(m % 60).padStart(2, "0");
    const txt = `${((h + 11) % 12) + 1}:${mm} ${h < 12 ? "a. m." : "p. m."}`;
    o.push(`<option value="${txt}">${txt}</option>`);
  }
  return o.join("");
}
$("hora").innerHTML = opcionesHora();

function validarProgramacion() {
  const ok = $("fecha").value && $("hora").value && $("persona").value.trim();
  $("btn-programar").disabled = !ok;
}
["fecha", "hora"].forEach((id) => $(id).addEventListener("input", validarProgramacion));

function abrirProgramar() {
  if (!actual) return;
  $("alerta-programar").innerHTML = "";
  $("resumen-programar").innerHTML = `${resumenSol(actual)}<br><i class="bi bi-telephone" aria-hidden="true"></i> <a class="dato" href="tel:${esc(actual.contacto)}">${esc(actual.contacto)}</a>
    <span class="texto-suave"> · prefiere: ${esc(actual.preferencia_horaria || "cualquier hora")}</span>`;
  $("fecha").min = new Date().toLocaleDateString("en-CA");
  $("fecha").value = ""; $("hora").value = "";
  $("persona").value = actual.recolector_nombre || "";
  validarProgramacion();
  modal("modal-programar").show();
}

$("btn-programar").addEventListener("click", async () => {
  const datos = { fecha: $("fecha").value, hora: $("hora").value, persona: $("persona").value.trim() };
  if (!datos.fecha || !datos.hora || !datos.persona) return;
  if (datos.fecha < $("fecha").min) return mostrarAlerta("Elige un día de hoy en adelante.", "warning", "alerta-programar");
  $("btn-programar").disabled = true;
  try {
    await api.programar(actual.id, datos);
    modal("modal-programar").hide();
    await cargar();
    mostrarAlerta(`Solicitud ${actual.id} programada para ${formatDia(datos.fecha, datos.hora)}, a cargo de ${datos.persona}. El usuario ya puede verla.`, "success");
  } catch (e) {
    mostrarAlerta("No se pudo programar. " + e.message, "danger", "alerta-programar");
    validarProgramacion();
  }
});

/* ---------- Cancelar ---------- */
function abrirCancelar() {
  $("alerta-cancelar").innerHTML = "";
  $("resumen-cancelar").innerHTML = resumenSol(actual);
  modal("modal-cancelar").show();
}
$("btn-cancelar").addEventListener("click", async () => {
  const id = actual.id;
  try {
    await api.cancelar(id, $("motivo").value);
    modal("modal-cancelar").hide();
    await cargar();
    mostrarAlerta(`Solicitud ${id} cancelada.`, "info");
  } catch (e) { mostrarAlerta("No se pudo cancelar. " + e.message, "danger", "alerta-cancelar"); }
});

cargar();