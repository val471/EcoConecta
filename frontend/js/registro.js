// EcoConecta · crear cuenta de solicitante. Se pide solo lo necesario: nombre, celular, tipo de lugar y contraseña.
renderNavbar();
const $ = (id) => document.getElementById(id);

$("tipo").innerHTML = Object.entries(TIPOS_GENERADOR).map(([v, t]) => `<option value="${v}">${t}</option>`).join("");
$("celular").addEventListener("input", (e) => { e.target.value = e.target.value.replace(/\D/g, ""); });
$("ver").addEventListener("change", (e) => { $("password").type = e.target.checked ? "text" : "password"; });

function error(id, mensaje) { const el = $("error-" + id); el.textContent = mensaje; el.hidden = !mensaje; return !!mensaje; }

$("form-registro").addEventListener("submit", async (e) => {
  e.preventDefault();
  const nombre = $("nombre").value.trim().replace(/\s+/g, " "), celular = $("celular").value.trim(), password = $("password").value;
  const malos = [
    error("nombre", nombre.length >= 3 ? "" : "Escribe tu nombre completo."),
    error("celular", /^3\d{9}$/.test(celular) ? "" : "Escribe tu celular de 10 números, empezando por 3. Ejemplo: 3001234567."),
    error("password", password.length >= 6 ? "" : "La contraseña debe tener al menos 6 caracteres."),
  ];
  if (malos.some(Boolean)) return mostrarAlerta("Falta completar algunos datos. Revisa los mensajes en rojo.", "warning");

  const btn = $("btn-registro");
  btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Creando…';
  try {
    await registrarse({ nombre, celular, password, tipo: $("tipo").value });   // guarda la sesión y entra
  } catch (err) {
    mostrarAlerta(err.message, "danger");
    btn.disabled = false; btn.innerHTML = '<i class="bi bi-person-plus" aria-hidden="true"></i> Crear mi cuenta';
  }
});
