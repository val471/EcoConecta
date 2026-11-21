// EcoConecta · educación ambiental. Lee /api/contenidos y permite escuchar cada tema con voz local.
renderNavbar();

const $ = (id) => document.getElementById(id);
const CATEGORIAS = { todo: "Todo", separacion: "Cómo separar", organicos: "Orgánicos", reciclables: "Reciclables",
  horarios: "Horarios y rutas", plataforma: "Usar la plataforma", puntos: "Puntos" };
let contenidos = [], categoria = "todo";

function pintarCategorias() {
  const hay = new Set(contenidos.map((c) => c.categoria));
  $("categorias").innerHTML = Object.entries(CATEGORIAS).filter(([k]) => k === "todo" || hay.has(k)).map(([k, t]) =>
    `<button type="button" class="chip me-2 mb-2" data-cat="${k}" aria-pressed="${k === categoria}">${t}</button>`).join("");
}

function tema(c, i) {
  const parrafos = (c.cuerpo || "").split("\n").filter(Boolean).map((p) => `<p class="mb-2">${esc(p)}</p>`).join("");
  return `<details class="eco-card tema">
    <summary><span><strong>${esc(c.titulo)}</strong><br><span class="texto-suave fw-normal">${esc(c.resumen || "")}</span></span></summary>
    <div class="mt-2">${parrafos}
      <button type="button" class="btn btn-outline-eco btn-sm" data-escuchar="${i}" ${Voz.disponible ? "" : "hidden"}>
        <i class="bi bi-volume-up" aria-hidden="true"></i> Escuchar este tema</button></div>
  </details>`;
}

function pintar() {
  pintarCategorias();
  const lista = contenidos.filter((c) => categoria === "todo" || c.categoria === categoria);
  $("lista").innerHTML = lista.length ? lista.map((c) => tema(c, contenidos.indexOf(c))).join("")
    : `<div class="eco-card text-center py-4">Todavía no hay contenidos en este tema.</div>`;
  $("lista").setAttribute("aria-busy", "false");
}

async function cargar() {
  try { contenidos = await api.contenidos(); pintar(); }
  catch (e) {
    $("lista").innerHTML = `<div class="eco-card">No pudimos cargar los contenidos. ${esc(e.message)}
      <button class="btn btn-outline-eco ms-2" type="button" onclick="cargar()">Intentar de nuevo</button></div>`;
  }
}

$("categorias").addEventListener("click", (e) => { const b = e.target.closest("[data-cat]"); if (b) { categoria = b.dataset.cat; pintar(); } });
$("lista").addEventListener("click", (e) => {
  const b = e.target.closest("[data-escuchar]"); if (!b) return;
  const c = contenidos[Number(b.dataset.escuchar)];
  Voz.hablar(`${c.titulo}. ${c.cuerpo.replace(/\n/g, " ")}`);
});
Voz.alCambiar(() => { if (contenidos.length) pintar(); });   // si la voz carga después, aparecen los botones "Escuchar"

cargar();
