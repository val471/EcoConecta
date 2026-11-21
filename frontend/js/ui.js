// EcoConecta · utilidades de interfaz (todas las pantallas usan estas funciones)

function esc(texto) {
  const d = document.createElement("div");
  d.textContent = texto ?? "";
  return d.innerHTML;
}

function badgeEstado(estado) {
  return `<span class="estado estado-${estado}"><i class="bi ${ICONOS_ESTADO[estado] || "bi-circle"}" aria-hidden="true"></i>${ESTADOS[estado] || estado}</span>`;
}

function badgeFlujo(flujo) {
  return `<span class="flujo flujo-${flujo}"><i class="bi ${ICONOS_FLUJO[flujo] || "bi-circle"}" aria-hidden="true"></i>${FLUJOS[flujo]?.etiqueta || flujo}</span>`;
}

function badgePuntos(total) {
  return `<span class="puntos"><i class="bi bi-star-fill" aria-hidden="true"></i>${total} puntos</span>`;
}

function formatFecha(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
}

function formatDia(fecha, hora) {
  if (!fecha) return "";
  const d = new Date(fecha + "T00:00:00");
  return `${d.toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long" })}, ${hora}`;
}

// Mensaje claro: tipo = success | danger | warning | info
function mostrarAlerta(mensaje, tipo = "info", contenedorId = "alertas") {
  const cont = document.getElementById(contenedorId);
  if (!cont) return alert(mensaje);
  cont.innerHTML = `<div class="alert alert-${tipo} alert-dismissible" role="alert">
    ${esc(mensaje)}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button></div>`;
  cont.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function lineaTiempoHTML(historial = []) {
  if (!historial.length) return "";
  return `<ul class="linea-tiempo">${historial
    .map((h) => `<li>${badgeEstado(h.estado)} <small class="texto-suave">${formatFecha(h.fecha)}</small>
      ${h.nota ? `<div class="small">${esc(h.nota)}</div>` : ""}</li>`).join("")}</ul>`;
}

function etiquetaResiduo(clave) { return TIPOS_RESIDUO[clave]?.etiqueta || clave; }
