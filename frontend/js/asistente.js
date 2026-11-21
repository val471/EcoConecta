// EcoConecta · asistente por texto, con voz LOCAL del dispositivo (speechSynthesis).
// No usa micrófono ni SpeechRecognition: así no se envía audio a servicios no autorizados.
// El asistente solo sugiere; asignar, programar y cerrar siguen siendo decisiones de una persona.
renderNavbar();

const $ = (id) => document.getElementById(id);
let historial = [];          // [{rol: "usuario" | "asistente", texto}]
const textosAsistente = [];  // para el botón "Escuchar" de cada respuesta

/* ---------- Voz (ver js/voz.js: solo voces locales en español) ---------- */
let marcadoAuto = false;
Voz.alCambiar((v) => {
  $("voz-panel").hidden = !v;
  $("voz-nota").hidden = !!v;
  document.querySelectorAll("[data-escuchar]").forEach((b) => (b.hidden = !v));
  if (v && !marcadoAuto) { $("leer-auto").checked = true; marcadoAuto = true; }   // por defecto, lee las respuestas
});
const hablar = (texto) => Voz.hablar(texto, () => ($("btn-callar").hidden = false), () => ($("btn-callar").hidden = true));
$("btn-callar").addEventListener("click", () => { Voz.parar(); $("btn-callar").hidden = true; });

/* ---------- Chat ---------- */
function burbuja(rol, texto, extra = "") {
  const div = document.createElement("div");
  div.className = "burbuja " + rol;
  div.innerHTML = `<div>${esc(texto)}</div>${extra}`;
  $("chat").appendChild(div);
  $("chat").scrollTop = $("chat").scrollHeight;
  return div;
}

function pieRespuesta(r, indice) {
  const acciones = [];
  acciones.push(`<button type="button" class="btn btn-outline-eco btn-sm" data-escuchar="${indice}" ${Voz.disponible ? "" : "hidden"}>
    <i class="bi bi-volume-up" aria-hidden="true"></i> Escuchar</button>`);
  if (r.flujo_sugerido) {
    const nombre = FLUJOS[r.flujo_sugerido].etiqueta.toLowerCase();
    const destino = usuarioActual() ? `solicitud.html?flujo=${r.flujo_sugerido}` : "login.html";
    acciones.push(`<a class="btn btn-eco btn-sm" href="${destino}"><i class="bi bi-send" aria-hidden="true"></i>
      ${usuarioActual() ? `Solicitar recolección de ${nombre}s` : "Ingresar para solicitar"}</a>`);
  }
  const nota = r.origen === "respaldo" ? `<div class="ayuda w-100">Respuesta básica del asistente automático.</div>` : "";
  return `<div class="pie">${acciones.join("")}${nota}</div>`;
}

async function preguntar(texto) {
  texto = texto.trim();
  if (!texto) return;
  burbuja("usuario", texto);
  $("pregunta").value = "";
  const pensando = burbuja("asistente", "Pensando…");
  $("btn-enviar").disabled = true;
  try {
    const r = await api.preguntarAsistente(texto, historial.slice(-6));
    historial.push({ rol: "usuario", texto }, { rol: "asistente", texto: r.respuesta });
    textosAsistente.push(r.respuesta);
    pensando.remove();
    burbuja("asistente", r.respuesta, pieRespuesta(r, textosAsistente.length - 1));
    if (Voz.disponible && $("leer-auto").checked) hablar(r.respuesta);
  } catch (e) {
    pensando.remove();
    mostrarAlerta("No pude responder ahora. " + e.message, "warning");
  } finally { $("btn-enviar").disabled = false; $("pregunta").focus(); }
}

$("form-chat").addEventListener("submit", (e) => { e.preventDefault(); preguntar($("pregunta").value); });
$("pregunta").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); preguntar($("pregunta").value); }
});
$("chat").addEventListener("click", (e) => {
  const b = e.target.closest("[data-escuchar]");
  if (b) hablar(textosAsistente[Number(b.dataset.escuchar)]);
});

/* ---------- Preguntas de ejemplo ---------- */
const EJEMPLOS = ["¿Dónde va una cáscara de naranja?", "¿Puedo reciclar una botella de plástico?", "¿Cómo pido una recolección?"];
$("sugerencias").innerHTML = EJEMPLOS.map((q, i) => `<button type="button" class="chip me-2 mb-2" data-q="${i}">${esc(q)}</button>`).join("");
$("sugerencias").addEventListener("click", (e) => {
  const b = e.target.closest("[data-q]"); if (b) preguntar(EJEMPLOS[Number(b.dataset.q)]);
});
