// EcoConecta · pantalla del recolector (huertero o reciclador). Solo ve lo que le asignaron (RN-07).
const usuario = requerirRol(["recolector"]);
renderNavbar();

const $ = (id) => document.getElementById(id);
const FLUJO = usuario.flujo;
const modal = (id) => bootstrap.Modal.getOrCreateInstance($(id));

let todas = [], pestana = "porrecoger", actual = null;
const PESTANAS = {
  porrecoger: { texto: "Por recoger",  icono: "bi-bag",          estados: ["asignada", "programada"], vacio: "No tienes recolecciones pendientes." },
  recogidas:  { texto: "Ya recogidas", icono: "bi-check-circle", estados: ["recolectada"],            vacio: "Todavía no has registrado recolecciones." },
};

$("subtitulo").innerHTML = `${badgeFlujo(FLUJO)} &nbsp; ${FLUJOS[FLUJO].recolector}: ${esc(usuario.nombre)}`;

function tarjeta(s) {
  const tel = esc(s.contacto || "");
  const prog = s.programacion
    ? `<dl class="bloque-programacion mt-3 mb-0">
         <dt><i class="bi bi-calendar-check" aria-hidden="true"></i> Día y hora</dt>
         <dd class="dato mb-0" style="font-size:1.25rem;font-weight:600">${esc(formatDia(s.programacion.fecha, s.programacion.hora))}</dd></dl>`
    : `<div class="aviso-puntos mt-3"><i class="bi bi-hourglass-split" aria-hidden="true"></i> El coordinador todavía debe acordar el día y la hora.</div>`;

  let acciones = "";
  if (s.estado === "programada" || s.estado === "asignada")
    acciones += `<a class="btn btn-outline-eco accion-grande" href="tel:${tel}"><i class="bi bi-telephone" aria-hidden="true"></i> Llamar: <span class="dato">${tel}</span></a>`;
  if (s.estado === "programada")
    acciones += `<button class="btn btn-eco accion-grande" data-accion="recoger" data-id="${s.id}"><i class="bi bi-check-circle" aria-hidden="true"></i> Ya recogí</button>`;

  const hecho = s.recoleccion
    ? `<div class="mt-3">Recogiste <strong>${esc(s.recoleccion.cantidad)} ${esc(s.recoleccion.unidad)}</strong> de ${esc(etiquetaResiduo(s.recoleccion.tipo_residuo).toLowerCase())}.
       ${s.puntos ? `<div class="mt-1">${badgePuntos(s.puntos.total)} <span class="ayuda">para ${esc(s.nombre_usuario || "el usuario")}</span></div>` : ""}</div>` : "";

  return `<article class="eco-card destacada">
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
      <span class="id-solicitud" style="font-size:1.2rem">${esc(s.id)}</span>${badgeEstado(s.estado)}</div>
    ${s.estado === "recolectada" ? "" : prog}
    <div class="mt-3"><i class="bi bi-geo-alt" aria-hidden="true"></i> <strong>${esc(s.direccion)}</strong><br>
      <span class="texto-suave">${esc(s.nombre_usuario || "")} · ${esc(TIPOS_GENERADOR[s.tipo_generador] || "")}</span></div>
    ${s.observaciones ? `<div class="mt-2"><i class="bi bi-chat-left-text" aria-hidden="true"></i> ${esc(s.observaciones)}</div>` : ""}
    ${hecho}
    ${acciones ? `<div class="d-grid gap-2 mt-3">${acciones}</div>` : ""}
  </article>`;
}

function pintar() {
  $("pestanas").innerHTML = Object.entries(PESTANAS).map(([k, p]) => {
    const n = todas.filter((s) => p.estados.includes(s.estado)).length, activo = k === pestana;
    return `<button type="button" class="btn ${activo ? "btn-eco" : "btn-outline-eco"}" data-pestana="${k}" aria-pressed="${activo}">
      <i class="bi ${p.icono}" aria-hidden="true"></i> ${p.texto} <span class="badge text-bg-light ms-1">${n}</span></button>`;
  }).join("");

  const lista = todas.filter((s) => PESTANAS[pestana].estados.includes(s.estado));
  // Por recoger: primero las programadas, de la fecha más próxima a la más lejana
  const clave = (s) => s.programacion ? `${s.programacion.fecha} ${s.programacion.hora}` : "9999";
  lista.sort((a, b) => pestana === "porrecoger" ? clave(a).localeCompare(clave(b)) : new Date(b.recoleccion?.fecha) - new Date(a.recoleccion?.fecha));
  $("lista").innerHTML = lista.length ? lista.map(tarjeta).join("") : `<div class="eco-card text-center py-4">${PESTANAS[pestana].vacio}</div>`;
  $("lista").setAttribute("aria-busy", "false");
}

async function cargar() {
  try { todas = await api.misAsignaciones(); pintar(); }
  catch (e) {
    mostrarAlerta("No pudimos cargar tus recolecciones. " + e.message, "danger");
    $("lista").innerHTML = `<button class="btn btn-outline-eco" onclick="cargar()">Intentar de nuevo</button>`;
  }
}

$("pestanas").addEventListener("click", (e) => { const b = e.target.closest("[data-pestana]"); if (b) { pestana = b.dataset.pestana; pintar(); } });
$("lista").addEventListener("click", (e) => {
  const b = e.target.closest("[data-accion]"); if (!b) return;
  actual = todas.find((s) => String(s.id) === b.dataset.id); if (actual) abrirRecoger();
});

/* ---------- Registrar recolección (RN-05: los puntos salen solo después de esto) ---------- */
const cantidadValida = () => {
  const t = $("cantidad").value.trim();
  if (!/^\d+([.,]\d+)?$/.test(t)) return null;
  const n = parseFloat(t.replace(",", "."));
  return n > 0 && n <= 1000 ? n : null;
};
function validar() {
  const n = cantidadValida(), tipo = $("tipo").value;
  $("btn-recoger").disabled = !(n && tipo);
  $("vista-registro").textContent = n && tipo ? `Vas a registrar: ${String(n).replace(".", ",")} kg de ${etiquetaResiduo(tipo).toLowerCase()}.` : "Elige qué recogiste y escribe los kilos.";
}
$("tipo").addEventListener("change", validar);
$("cantidad").addEventListener("input", validar);

function abrirRecoger() {
  $("alerta-recoger").innerHTML = "";
  $("resumen-recoger").innerHTML = `<strong>${esc(actual.id)}</strong> · ${esc(actual.direccion)}`;
  $("tipo").innerHTML = `<option value="">Elige una opción</option>` + Object.entries(TIPOS_RESIDUO)
    .filter(([, t]) => t.flujo === FLUJO).map(([k, t]) => `<option value="${k}">${esc(t.etiqueta)}</option>`).join("");
  if (FLUJO === "organico") $("tipo").value = "organico";   // un solo tipo: ya viene elegido
  $("cantidad").value = "";
  validar();
  modal("modal-recoger").show();
}

$("btn-recoger").addEventListener("click", async () => {
  const datos = { tipo_residuo: $("tipo").value, cantidad: cantidadValida(), unidad: "kg" };
  if (!datos.cantidad || !datos.tipo_residuo) return;
  $("btn-recoger").disabled = true;
  try {
    const s = await api.registrarRecoleccion(actual.id, datos);
    modal("modal-recoger").hide();
    await cargar();
    mostrarAlerta(`¡Listo! Quedó registrada la recolección de ${s.id}. Se asignaron ${s.puntos?.total ?? 0} puntos al usuario.`, "success");
  } catch (e) {
    mostrarAlerta("No se pudo registrar. " + e.message, "danger", "alerta-recoger");
    validar();
  }
});

cargar();
