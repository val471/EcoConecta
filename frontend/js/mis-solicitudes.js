// EcoConecta · pantalla "Mis solicitudes" (el usuario solo ve lo suyo; sin datos de contacto de terceros)
requerirRol(["solicitante"]);
renderNavbar();
document.getElementById("aviso-puntos").textContent = AVISO_PUNTOS;

function tarjeta(s) {
  const prog = s.programacion
    ? `<dl class="bloque-programacion mt-3 mb-0">
         <dt><i class="bi bi-calendar-check" aria-hidden="true"></i> Día y hora</dt><dd class="dato">${esc(formatDia(s.programacion.fecha, s.programacion.hora))}</dd>
         <dt><i class="bi bi-person-check" aria-hidden="true"></i> Persona que irá</dt><dd class="mb-0">${esc(s.programacion.persona)}</dd>
       </dl>`
    : "";

  const puntos = s.puntos
    ? `<div class="mt-3">${badgePuntos(s.puntos.total)}<div class="ayuda mt-1">${esc(s.puntos.explicacion)}</div></div>`
    : "";

  const mensaje = {
    recibida: "Recibimos tu solicitud. Pronto un coordinador la revisará.",
    en_revision: "Un coordinador está revisando tu solicitud.",
    asignada: "Ya hay una persona asignada. Falta acordar el día y la hora.",
    programada: "¡Todo listo! Te esperamos en el día y la hora indicados.",
    recolectada: "Ya recogimos tus residuos. ¡Gracias por participar!",
    cancelada: "Esta solicitud fue cancelada.",
  }[s.estado];

  return `<article class="eco-card destacada">
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
      <span class="id-solicitud" style="font-size:1.2rem">${esc(s.id)}</span>
      <span>${badgeFlujo(s.flujo)} ${badgeEstado(s.estado)}</span>
    </div>
    <p class="mt-2 mb-0">${mensaje}</p>
    <div class="ayuda">Enviada el ${formatFecha(s.creada)}</div>
    ${prog}${puntos}
    <details class="mt-3"><summary>Ver historial</summary>${lineaTiempoHTML(s.historial)}</details>
  </article>`;
}

async function cargar() {
  const lista = document.getElementById("lista");
  try {
    const [sols, pts] = await Promise.all([api.misSolicitudes(), api.puntosUsuario()]);
    document.getElementById("total-puntos").innerHTML = badgePuntos(pts.total);
    lista.innerHTML = sols.length
      ? sols.map(tarjeta).join("")
      : `<div class="eco-card text-center py-4"><p class="mb-3">Todavía no has hecho ninguna solicitud.</p>
         <a class="btn btn-eco" href="solicitud.html">Solicitar mi primera recolección</a></div>`;
  } catch (e) {
    mostrarAlerta("No pudimos cargar tus solicitudes. " + e.message, "danger");
    lista.innerHTML = `<button class="btn btn-outline-eco" onclick="cargar()">Intentar de nuevo</button>`;
  } finally { lista.setAttribute("aria-busy", "false"); }
}
cargar();