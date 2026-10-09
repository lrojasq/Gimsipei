/**
 * Fórmulas matemáticas con KaTeX.
 *
 * Uso: marcar un elemento con el atributo `data-math`. Las fórmulas escritas
 * en LaTeX entre \( ... \) (dentro del texto) o \[ ... \] (centradas en su
 * propio renglón) se dibujan como en Word.
 *
 * El signo $ NO se usa como delimitador: en los enunciados aparece como
 * moneda ("Juan tiene $5000") y se rompería el texto.
 *
 * Debe cargarse DESPUÉS de youtube_embed.js y de KaTeX + auto-render:
 * youtube_embed.js guarda el texto original en `data-original-text` antes de
 * modificar el elemento y la edición de contenidos lo lee de ahí. Si las
 * fórmulas se dibujaran primero, se guardaría el HTML de KaTeX en vez del LaTeX.
 */
(function () {
  "use strict";

  const OPTIONS = {
    delimiters: [
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false },
    ],
    // Una fórmula mal escrita se muestra en rojo en vez de romper la página
    throwOnError: false,
  };

  function render(root) {
    if (typeof window.renderMathInElement !== "function") return;
    window.renderMathInElement(root, OPTIONS);
  }

  function init() {
    document.querySelectorAll("[data-math]").forEach(render);
  }

  // La usa formula_editor.js para la vista previa
  window.MathRender = { render };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
