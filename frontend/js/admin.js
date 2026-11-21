// EcoConecta · administración: regla de puntos (RN-06) y usuarios piloto (RN-08)
requerirRol(["admin"]);
renderNavbar();

const $ = (id) => document.getElementById(id);
$("aviso-puntos").textContent = AVISO_PUNTOS;

let reglas = [], usuarios = [];

/* ---------- Reglas de puntos ---------- */
function pintarReglas() {
  $("tabla-reglas").innerHTML = reglas.map((r, i) => {
    const t = TIPOS_RESIDUO[r.tipo_residuo];
    return `<tr>
      <td>${t ? badgeFlujo(t.flujo) : ""} <strong>${esc(t?.etiqueta || r.tipo_residuo)}</strong></td>
      <td style="max-width:150px"><label class="visually-hidden" for="regla-${i}">Puntos por kg de ${esc(t?.etiqueta || r.tipo_residuo)}</label>
        <input id="regla-${i}" class="form-control" data-i="${i}" inputmode="decimal" value="${r.puntos_por_unidad}"></td>
      <td class="dato" id="ejemplo-${i}">${ejemplo(r.puntos_por_unidad, t?.etiqueta || r.tipo_residuo)}</td></tr>`;
  }).join("");
}
const parsear = (txt) => /^\d+([.,]\d+)?$/.test(String(txt).trim()) ? parseFloat(String(txt).replace(",", ".")) : null;
const ejemplo = (p, nombre) => (p == null ? "Escribe un número" : `2 kg de ${nombre.toLowerCase()} × ${p} = ${Math.round(2 * p)} puntos`);

$("tabla-reglas").addEventListener("input", (e) => {
  const i = e.target.dataset?.i; if (i === undefined) return;
  const t = TIPOS_RESIDUO[reglas[i].tipo_residuo];
  $("ejemplo-" + i).textContent = ejemplo(parsear(e.target.value), t?.etiqueta || reglas[i].tipo_residuo);
});

$("btn-guardar-reglas").addEventListener("click", async () => {
  const nuevas = [];
  for (const input of $("tabla-reglas").querySelectorAll("input[data-i]")) {
    const v = parsear(input.value);
    if (v === null || v > 1000) {
      input.focus();
      return mostrarAlerta("Revisa los puntos: escribe un número de 0 a 1000, por ejemplo 5 o 2,5.", "warning");
    }
    nuevas.push({ ...reglas[input.dataset.i], puntos_por_unidad: v });
  }
  try {
    reglas = await api.setReglas(nuevas);
    pintarReglas();
    mostrarAlerta("Listo, guardamos los puntos. Se aplicarán a las próximas recolecciones.", "success");
  } catch (e) { mostrarAlerta("No se pudo guardar. " + e.message, "danger"); }
});

/* ---------- Usuarios piloto ---------- */
function pintarUsuarios() {
  const sol = usuarios.filter((u) => u.rol === "solicitante");
  $("resumen-pilotos").textContent = `${sol.filter((u) => u.es_piloto).length} de ${sol.length} personas habilitadas`;
  $("lista-usuarios").innerHTML = sol.map((u) => `
    <li class="list-group-item d-flex flex-wrap justify-content-between align-items-center gap-2">
      <div><strong>${esc(u.nombre)}</strong><br><span class="texto-suave">${esc(TIPOS_GENERADOR[u.tipo] || "")}${u.telefono ? " · celular ••••" + esc(u.telefono.slice(-4)) : ""}</span></div>
      <div class="form-check form-switch fs-5 mb-0">
        <input class="form-check-input" type="checkbox" role="switch" id="piloto-${u.id}" data-piloto="${u.id}" ${u.es_piloto ? "checked" : ""}>
        <label class="form-check-label" for="piloto-${u.id}">${u.es_piloto ? "Habilitado" : "No habilitado"}</label>
      </div></li>`).join("") || `<li class="list-group-item">No hay usuarios registrados.</li>`;

  const equipo = usuarios.filter((u) => u.rol !== "solicitante" && u.rol !== "admin");
  const rolTxt = { coord_huerteros: "Coordinador de huerteros", coord_recicladores: "Coordinador de recicladores" };
  $("lista-equipo").innerHTML = equipo.map((u) =>
    `<li class="py-1"><i class="bi bi-person" aria-hidden="true"></i> <strong>${esc(u.nombre)}</strong> · <span class="texto-suave">${rolTxt[u.rol] || FLUJOS[u.flujo]?.recolector}</span></li>`).join("");
}

$("lista-usuarios").addEventListener("change", async (e) => {
  const id = e.target.dataset?.piloto; if (!id) return;
  const habilitar = e.target.checked;
  try {
    await api.setPiloto(Number(id), habilitar);
    usuarios = await api.getUsuarios(); pintarUsuarios();
    mostrarAlerta(habilitar ? "Persona habilitada para solicitar." : "Persona deshabilitada.", "success");
  } catch (err) {
    e.target.checked = !habilitar;
    mostrarAlerta("No se pudo cambiar. " + err.message, "danger");
  }
});

(async function cargar() {
  try { [reglas, usuarios] = await Promise.all([api.getReglas(), api.getUsuarios()]); pintarReglas(); pintarUsuarios(); }
  catch (e) { mostrarAlerta("No pudimos cargar la información. " + e.message, "danger"); }
})();
