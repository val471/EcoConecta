// EcoConecta · encabezado: franja blanca con el logo original (≥220 px) + barra verde bosque con el menú.
// Uso: <div id="navbar"></div> y renderNavbar();

function renderNavbar() {
  const u = usuarioActual();
  const items = MENU[u ? u.rol : "publico"] || MENU.publico;
  const simple = items.length <= 3; // pocas opciones: menú siempre visible, sin botón "Menú"
  const actual = location.pathname.split("/").pop() || "index.html";
  const home = u ? HOME_POR_ROL[u.rol] || "index.html" : "index.html";

  const enlaces = items.map((i) =>
    `<li class="nav-item"><a class="nav-link ${i.href === actual ? "active" : ""}" ${i.href === actual ? 'aria-current="page"' : ""} href="${i.href}">${i.texto}</a></li>`).join("");

  const acceso = u
    ? `<span class="usuario me-lg-2">${esc(u.nombre)}</span><button class="btn btn-sol btn-sm" style="min-height:44px" onclick="cerrarSesion()"><i class="bi bi-box-arrow-right" aria-hidden="true"></i> Salir</button>`
    : `<a class="btn btn-sol btn-sm d-inline-flex align-items-center" style="min-height:44px" href="login.html"><i class="bi bi-person" aria-hidden="true"></i>&nbsp;Ingresar</a>`;

  const aviso = USAR_MOCK ? `<div class="aviso-mock">Modo de prueba: los datos se guardan solo en este navegador</div>` : "";

  const boton = simple ? "" :
    `<button class="eco-menu-btn" type="button" data-bs-toggle="collapse" data-bs-target="#menu" aria-controls="menu" aria-label="Abrir o cerrar el menú">
       <i class="bi bi-list" aria-hidden="true"></i> Menú</button>`;

  document.getElementById("navbar").innerHTML = `${aviso}
  <header class="eco-header">
    <div class="contenedor-nav">
      <a href="${home}" aria-label="EcoConecta Villas de San Pablo, ir al inicio">
        <img class="eco-logo" src="assets/logo.png" alt="EcoConecta Villas de San Pablo">
      </a>
    </div>
  </header>
  <nav class="navbar ${simple ? "navbar-expand" : "navbar-expand-lg"} eco-nav" aria-label="Menú principal">
    <div class="container-fluid contenedor-nav py-0">
      ${boton}
      <div class="${simple ? "" : "collapse"} navbar-collapse" id="menu">
        <ul class="navbar-nav me-auto">${enlaces}</ul>
        <div class="d-flex align-items-center gap-2 py-2 py-lg-0">${acceso}</div>
      </div>
    </div>
  </nav>`;
}