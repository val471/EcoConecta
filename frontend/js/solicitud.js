// EcoConecta · pantalla "Solicitar recolección"
const usuario = requerirRol(["solicitante"]);
renderNavbar();

const $ = (id) => document.getElementById(id);

// Tipo de lugar: se rellena desde TIPOS_GENERADOR y se preselecciona el del perfil
$("tipo_generador").innerHTML = Object.entries(TIPOS_GENERADOR)
  .map(([v, t]) => `<option value="${v}" ${usuario?.tipo === v ? "selected" : ""}>${t}</option>`).join("");
if (usuario?.telefono) $("contacto").value = usuario.telefono;
refrescarUsuario().then((u) => {
  if (u && u.es_piloto === false) {
    mostrarAlerta("Tu cuenta todavía no está habilitada para solicitar recolecciones. El administrador del piloto debe habilitarla.", "warning");
    $("btn-enviar").disabled = true;
  }
});

// Solo números en el celular
$("contacto").addEventListener("input", (e) => { e.target.value = e.target.value.replace(/\D/g, ""); });

const flujoSugerido = new URLSearchParams(location.search).get("flujo");
if (["organico", "reciclable"].includes(flujoSugerido)) $("flujo-" + flujoSugerido).checked = true;

function error(id, mensaje) {
  const el = $("error-" + id);
  el.textContent = mensaje; el.hidden = !mensaje;
  if (mensaje) el.previousElementSibling?.setAttribute?.("aria-invalid", "true");
  return !!mensaje;
}

function validar() {
  const flujo = document.querySelector('input[name="flujo"]:checked')?.value;
  const direccion = $("direccion").value.trim();
  const contacto = $("contacto").value.trim();
  let primero = null;
  const marca = (hayError, el) => { if (hayError && !primero) primero = el; };

  marca(error("flujo", flujo ? "" : "Elige si tus residuos son orgánicos o reciclables."), $("flujo-organico"));
  marca(error("direccion", direccion.length >= 5 ? "" : "Escribe tu dirección completa, por ejemplo: Manzana 12, casa 5."), $("direccion"));
  marca(error("contacto", /^3\d{9}$/.test(contacto) ? "" : "Escribe tu celular de 10 números, empezando por 3. Ejemplo: 3001234567."), $("contacto"));

  if (primero) { primero.focus(); primero.scrollIntoView({ behavior: "smooth", block: "center" }); return null; }
  return { flujo, direccion, contacto };
}

$("form-solicitud").addEventListener("submit", async (e) => {
  e.preventDefault();
  const base = validar();
  if (!base) return mostrarAlerta("Falta completar algunos datos. Revisa los mensajes en rojo.", "warning");

  const btn = $("btn-enviar");
  btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Enviando…';
  try {
    const sol = await api.crearSolicitud({
      ...base,
      tipo_generador: $("tipo_generador").value,
      preferencia_horaria: $("preferencia_horaria").value,
      observaciones: $("observaciones").value.trim(),
    });
    $("ok-id").textContent = sol.id;
    $("ok-flujo").innerHTML = `${badgeFlujo(sol.flujo)} &nbsp; Irá al ${FLUJOS[sol.flujo].coordinador.toLowerCase()}.`;
    $("vista-form").hidden = true; $("vista-ok").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    mostrarAlerta(err.message.includes("habilitada") ? err.message : "No pudimos enviar tu solicitud. " + err.message + " Inténtalo de nuevo.", err.message.includes("habilitada") ? "warning" : "danger");
  } finally {
    btn.disabled = false; btn.innerHTML = '<i class="bi bi-send" aria-hidden="true"></i> Enviar solicitud';
  }
});

$("btn-otra").addEventListener("click", () => {
  $("form-solicitud").reset();
  if (usuario?.telefono) $("contacto").value = usuario.telefono;
  $("vista-ok").hidden = true; $("vista-form").hidden = false;
});
