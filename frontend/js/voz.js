// EcoConecta · voz LOCAL del dispositivo (speechSynthesis). Sin micrófono: no se envía audio a terceros.
// Solo se usan voces en español instaladas en el dispositivo (localService); las de red se descartan.
const Voz = (() => {
  let voz = null;
  const oyentes = [];

  function elegir() {
    if (!("speechSynthesis" in window)) return null;
    const locales = speechSynthesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith("es") && v.localService);
    return locales.find((v) => /co|mx|us|419/i.test(v.lang)) || locales[0] || null;
  }
  function iniciar() { voz = elegir(); oyentes.forEach((f) => f(voz)); }
  if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = iniciar;
  iniciar();

  return {
    get disponible() { return !!voz; },
    alCambiar(f) { oyentes.push(f); f(voz); },            // se avisa cuando las voces terminan de cargar
    hablar(texto, alIniciar, alTerminar) {
      if (!voz) return;
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(texto);
      u.voice = voz; u.lang = voz.lang; u.rate = 0.95;
      u.onstart = () => alIniciar && alIniciar();
      u.onend = u.onerror = () => alTerminar && alTerminar();
      speechSynthesis.speak(u);
    },
    parar() { if ("speechSynthesis" in window) speechSynthesis.cancel(); },
  };
})();
