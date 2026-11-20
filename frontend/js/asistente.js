// Chat de la guía EcoConecta. Responsable: persona C.
// - El texto de la respuesta SIEMPRE se muestra en pantalla.
// - El botón "Escuchar" usa speechSynthesis del navegador, solo con voces
//   locales en español (v.localService). No usa micrófono ni SpeechRecognition,
//   así no se envía audio a ningún tercero.
(() => {
  const URL_CHAT = "/api/asistente/chat";
  const MAX_HISTORIAL = 10;

  const $mensajes = document.getElementById("mensajes");
  const $formulario = document.getElementById("formulario");
  const $pregunta = document.getElementById("pregunta");
  const $enviar = document.getElementById("enviar");
  const $notaVoz = document.getElementById("nota-voz");

  let historial = [];   // [{role: "user"|"assistant", content: "..."}]
  let vozEs = null;     // voz local en español, si existe
  let botonHablando = null;

  // ------------------------------------------------------------------ voz
  const PREFERENCIA = ["es-co", "es-mx", "es-us", "es-419", "es-es"];

  function cargarVoz() {
    if (!("speechSynthesis" in window)) { vozEs = null; return actualizarBotonesVoz(); }
    const locales = speechSynthesis.getVoices().filter(
      (v) => v.localService && v.lang.toLowerCase().startsWith("es")
    );
    const orden = (v) => {
      const i = PREFERENCIA.indexOf(v.lang.toLowerCase().replace("_", "-"));
      return i === -1 ? 99 : i;
    };
    locales.sort((a, b) => orden(a) - orden(b));
    vozEs = locales[0] || null;
    actualizarBotonesVoz();
  }

  function actualizarBotonesVoz() {
    document.querySelectorAll(".btn-escuchar").forEach((b) => { b.hidden = !vozEs; });
    $notaVoz.hidden = !!vozEs;
  }

  function hablar(texto, boton) {
    if (!vozEs) return;
    const eraElMismo = botonHablando === boton;
    speechSynthesis.cancel();
    restaurarBoton();
    if (eraElMismo) return;            // segundo clic = detener
    const dicho = new SpeechSynthesisUtterance(texto);
    dicho.voice = vozEs;
    dicho.lang = vozEs.lang;
    dicho.rate = 0.95;
    dicho.onend = dicho.onerror = restaurarBoton;
    botonHablando = boton;
    boton.textContent = "⏹ Detener";
    speechSynthesis.speak(dicho);
  }

  function restaurarBoton() {
    if (botonHablando) botonHablando.textContent = "🔊 Escuchar";
    botonHablando = null;
  }

  if ("speechSynthesis" in window) {
    speechSynthesis.addEventListener("voiceschanged", cargarVoz); // las voces cargan tarde
    cargarVoz();
  } else {
    $notaVoz.hidden = false;
  }

  // ------------------------------------------------------------- mensajes
  // Hojita que se ve junto a las respuestas de la guía (contenido fijo, no viene del usuario)
  const HOJA_SVG =
    '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 28C4 14 12 5 28 4c0 14-8 22-20 22" fill="#1e4b2e"/></svg>';

  function agregarMensaje(rol, texto, { respaldo = false } = {}) {
    const esUsuario = rol === "user";
    const fila = document.createElement("div");
    fila.className = "chat-fila " + (esUsuario ? "chat-fila-usuario" : "chat-fila-guia");

    if (!esUsuario) {
      const avatar = document.createElement("span");
      avatar.className = "chat-avatar";
      avatar.innerHTML = HOJA_SVG;
      fila.appendChild(avatar);
    }

    const columna = document.createElement("div");
    columna.className = "chat-col";

    const burbuja = document.createElement("div");
    burbuja.className = "chat-burbuja " + (esUsuario ? "chat-usuario" : "chat-guia");
    if (respaldo) burbuja.classList.add("chat-respaldo");
    burbuja.textContent = texto;          // textContent: nunca interpreta HTML
    columna.appendChild(burbuja);

    if (!esUsuario) {
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "btn-escuchar";
      boton.textContent = "🔊 Escuchar";
      boton.hidden = !vozEs;
      boton.addEventListener("click", () => hablar(texto, boton));
      columna.appendChild(boton);
    }

    fila.appendChild(columna);
    $mensajes.appendChild(fila);
    $mensajes.scrollTop = $mensajes.scrollHeight;
    return fila;
  }

  function mostrarEscribiendo() {
    const fila = agregarMensaje("assistant", "Escribiendo…");
    fila.querySelector(".btn-escuchar").remove();
    fila.querySelector(".chat-burbuja").classList.add("chat-escribiendo");
    return fila;
  }

  // --------------------------------------------------------------- envío
  async function enviar(texto) {
    texto = texto.trim();
    if (!texto) return;

    agregarMensaje("user", texto);
    $pregunta.value = "";
    $pregunta.disabled = $enviar.disabled = true;
    const escribiendo = mostrarEscribiendo();

    try {
      const respuesta = await fetch(URL_CHAT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta: texto, historial: historial.slice(-MAX_HISTORIAL) }),
      });
      escribiendo.remove();

      if (respuesta.status === 429) {
        agregarMensaje("assistant", "Estás preguntando muy rápido. Espera un momento e inténtalo de nuevo.");
      } else if (!respuesta.ok) {
        agregarMensaje("assistant", "No pude procesar tu pregunta. Revisa que no sea muy larga e inténtalo de nuevo.");
      } else {
        const datos = await respuesta.json();
        agregarMensaje("assistant", datos.respuesta, { respaldo: datos.respaldo });
        if (!datos.respaldo) {       // el mensaje de respaldo no se guarda en la conversación
          historial.push({ role: "user", content: texto });
          historial.push({ role: "assistant", content: datos.respuesta });
        }
      }
    } catch (error) {
      escribiendo.remove();
      agregarMensaje("assistant", "No hay conexión con el servidor. Revisa tu internet e inténtalo de nuevo.");
    } finally {
      $pregunta.disabled = $enviar.disabled = false;
      $pregunta.focus();
    }
  }

  $formulario.addEventListener("submit", (e) => { e.preventDefault(); enviar($pregunta.value); });
  document.getElementById("sugerencias").addEventListener("click", (e) => {
    const boton = e.target.closest("[data-pregunta]");
    if (boton) enviar(boton.dataset.pregunta);
  });

  agregarMensaje("assistant",
    "¡Hola! Soy la guía de EcoConecta. Te ayudo a separar residuos orgánicos y reciclables " +
    "y a usar la plataforma. ¿Qué quieres saber?");
})();