// EcoConecta · sesión y control de acceso por rol en el navegador.
// OJO: esto solo mejora la experiencia. La seguridad real (RN-07) la aplica el backend.

function usuarioActual() { return Sesion.get()?.usuario || null; }

async function iniciarSesion(email, password) {
  const r = await api.login(email, password);
  Sesion.set({ token: r.token, usuario: r.usuario });
  location.href = HOME_POR_ROL[r.usuario.rol] || "index.html";
}

function cerrarSesion() { Sesion.clear(); location.href = "login.html"; }

// Llamar al inicio de cada página protegida: requerirRol(["coord_huerteros", "coord_recicladores"])
function requerirRol(rolesPermitidos) {
  const u = usuarioActual();
  if (!u) { location.href = "login.html"; return null; }
  if (rolesPermitidos && !rolesPermitidos.includes(u.rol)) {
    location.href = HOME_POR_ROL[u.rol] || "index.html";
    return null;
  }
  return u;
}

// Crear cuenta de solicitante y entrar de una vez
async function registrarse(datos) {
  const r = await api.registro(datos);
  Sesion.set({ token: r.token, usuario: r.usuario });
  location.href = "mis-solicitudes.html";
}

// Trae del servidor los datos actuales del usuario (por ejemplo, si el administrador ya lo habilitó)
async function refrescarUsuario() {
  try {
    const u = await api.yo(), s = Sesion.get();
    if (s) { s.usuario = u; Sesion.set(s); }
    return u;
  } catch { return usuarioActual(); }
}
