/**
 * Editor visual de fórmulas (MathLive).
 *
 * Uso: marcar un <textarea> o <input type="text"> con `data-formula-editor`.
 * Debajo del campo aparece un botón "Insertar fórmula" que abre un editor al
 * estilo Word (fracciones, raíces, potencias y teclado matemático en el
 * celular). Al aceptar, la fórmula se inserta en LaTeX entre \( ... \) donde
 * estaba el cursor. Si el cursor está dentro de una fórmula ya escrita, el
 * editor la abre para modificarla.
 *
 * Si el campo está dentro de una fila (ej. las opciones de una pregunta),
 * marcar la fila con `data-formula-anchor` para que el botón y la vista
 * previa queden debajo de ella.
 *
 * Los campos que se crean después (preguntas de evaluación) se detectan
 * solos. MathLive se descarga recién la primera vez que se abre el editor.
 * La vista previa usa math_render.js, que debe estar cargado en la página.
 */
(function () {
  "use strict";

  const MATHLIVE_URL =
    "https://cdn.jsdelivr.net/npm/mathlive@0.101.0/dist/mathlive.min.js";
  const FIELD_SELECTOR =
    "textarea[data-formula-editor], input[data-formula-editor]";
  const HAS_FORMULA = /\\\(|\\\[/;

  // Botones rápidos del editor. #@ = lo que está antes del cursor,
  // #0 = lo seleccionado, #? = casilla vacía para completar.
  const TOOLBAR = [
    { label: "a⁄b", title: "Fracción", latex: "\\frac{#@}{#?}" },
    { label: "√", title: "Raíz cuadrada", latex: "\\sqrt{#0}" },
    { label: "ⁿ√", title: "Raíz n-ésima", latex: "\\sqrt[#?]{#0}" },
    { label: "xⁿ", title: "Potencia", latex: "#@^{#?}" },
    { label: "xₙ", title: "Subíndice", latex: "#@_{#?}" },
    { label: "( )", title: "Paréntesis", latex: "\\left(#0\\right)" },
    { label: "×", title: "Multiplicación", latex: "\\times" },
    { label: "÷", title: "División", latex: "\\div" },
    { label: "±", title: "Más o menos", latex: "\\pm" },
    { label: "≠", title: "Distinto", latex: "\\ne" },
    { label: "≤", title: "Menor o igual", latex: "\\le" },
    { label: "≥", title: "Mayor o igual", latex: "\\ge" },
    { label: "≈", title: "Aproximadamente", latex: "\\approx" },
    { label: "°", title: "Grados", latex: "^{\\circ}" },
    { label: "π", title: "Pi", latex: "\\pi" },
    { label: "∞", title: "Infinito", latex: "\\infty" },
    { label: "α", title: "Alfa", latex: "\\alpha" },
    { label: "β", title: "Beta", latex: "\\beta" },
    { label: "θ", title: "Theta", latex: "\\theta" },
    { label: "Δ", title: "Delta", latex: "\\Delta" },
    { label: "Σ", title: "Sumatoria", latex: "\\sum_{#?}^{#?}" },
    { label: "∫", title: "Integral", latex: "\\int_{#?}^{#?}" },
    { label: "x⃗", title: "Vector", latex: "\\vec{#@}" },
  ];

  let mathlivePromise = null;
  let modal = null;
  let mathField = null;
  // Campo que se está editando y rango del texto a reemplazar
  let target = null;

  function loadMathLive() {
    if (!mathlivePromise) {
      mathlivePromise = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = MATHLIVE_URL;
        script.onload = () =>
          customElements.whenDefined("math-field").then(resolve);
        script.onerror = () => {
          mathlivePromise = null;
          script.remove();
          reject(new Error("No se pudo cargar el editor de fórmulas"));
        };
        document.head.appendChild(script);
      });
    }
    return mathlivePromise;
  }

  /** Si `pos` cae dentro de \( ... \) o \[ ... \], devuelve sus límites. */
  function findFormulaAt(text, pos) {
    const pattern = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const start = match.index;
      const end = start + match[0].length;
      if (start >= pos) break;
      if (pos < end) {
        const display = match[1] === undefined;
        return { start, end, latex: display ? match[2] : match[1], display };
      }
    }
    return null;
  }

  function buildModal() {
    modal = document.createElement("div");
    modal.className = "formula-modal";
    modal.hidden = true;
    modal.innerHTML = `
      <div class="formula-modal__box" role="dialog" aria-modal="true" aria-labelledby="formulaModalTitle">
        <div class="formula-modal__header">
          <h3 id="formulaModalTitle">INSERTAR FÓRMULA</h3>
          <button type="button" class="formula-modal__close" aria-label="Cerrar">&times;</button>
        </div>
        <div class="formula-modal__toolbar" role="toolbar" aria-label="Símbolos"></div>
        <div class="formula-modal__field">
          <p class="formula-modal__status">Cargando editor…</p>
        </div>
        <p class="formula-modal__hint">
          Escribe como en Word: <kbd>/</kbd> hace una fracción, <kbd>^</kbd> una potencia
          y <kbd>_</kbd> un subíndice. Con las flechas te mueves entre las casillas.
        </p>
        <label class="formula-modal__display">
          <input type="checkbox"> Mostrar centrada en su propio renglón
        </label>
        <div class="formula-modal__actions">
          <button type="button" class="formula-btn" data-action="cancel">CANCELAR</button>
          <button type="button" class="formula-btn formula-btn--primary" data-action="insert" disabled>INSERTAR</button>
        </div>
      </div>
    `;

    const toolbar = modal.querySelector(".formula-modal__toolbar");
    TOOLBAR.forEach(({ label, title, latex }) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "formula-modal__tool";
      button.textContent = label;
      button.title = title;
      button.setAttribute("aria-label", title);
      button.addEventListener("click", () => {
        if (!mathField) return;
        mathField.insert(latex, { selectionMode: "placeholder", focus: true });
      });
      toolbar.appendChild(button);
    });

    modal.addEventListener("click", (event) => {
      if (event.target === modal) close();
      const action = event.target.closest("[data-action]")?.dataset.action;
      if (action === "cancel") close();
      if (action === "insert") apply();
    });
    modal
      .querySelector(".formula-modal__close")
      .addEventListener("click", close);

    // Sin stopPropagation, el Escape también cerraría el modal de la página
    // que está debajo (ej. crear evaluación)
    modal.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close();
      }
    });

    document.body.appendChild(modal);
  }

  function open(field) {
    if (!modal) buildModal();

    const value = field.value;
    let start = field.selectionStart ?? value.length;
    let end = field.selectionEnd ?? value.length;
    let latex = "";
    let display = false;

    const existing = start === end ? findFormulaAt(value, start) : null;
    if (existing) {
      ({ start, end, latex, display } = existing);
    }

    target = { field, start, end, editing: Boolean(existing) };

    const isTextarea = field.tagName === "TEXTAREA";
    const displayLabel = modal.querySelector(".formula-modal__display");
    displayLabel.hidden = !isTextarea;
    displayLabel.querySelector("input").checked = isTextarea && display;

    modal.querySelector("#formulaModalTitle").textContent = existing
      ? "EDITAR FÓRMULA"
      : "INSERTAR FÓRMULA";
    modal.querySelector('[data-action="insert"]').textContent = existing
      ? "GUARDAR"
      : "INSERTAR";

    modal.hidden = false;
    document.body.classList.add("formula-modal-open");

    if (!mathField) {
      modal.querySelector(".formula-modal__status").textContent =
        "Cargando editor…";
    }

    loadMathLive()
      .then(() => {
        if (!mathField) createMathField();
        mathField.value = latex;
        modal.querySelector('[data-action="insert"]').disabled = false;
        mathField.focus();
      })
      .catch((error) => {
        modal.querySelector(".formula-modal__status").textContent =
          `${error.message}. Revisa tu conexión e inténtalo de nuevo.`;
      });
  }

  function createMathField() {
    const container = modal.querySelector(".formula-modal__field");
    mathField = document.createElement("math-field");
    mathField.setAttribute("aria-label", "Fórmula");
    // En el celular aparece el teclado matemático al tocar el campo
    mathField.mathVirtualKeyboardPolicy = "auto";
    mathField.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        apply();
      }
    });
    container.replaceChildren(mathField);
  }

  function apply() {
    if (!target || !mathField) return;

    const { field, start, end, editing } = target;
    // latex-expanded convierte los atajos propios de MathLive a LaTeX
    // estándar, así KaTeX los entiende al mostrarlos
    const latex = mathField.getValue("latex-expanded").trim();

    if (!latex && !editing) {
      close();
      return;
    }

    const display = modal.querySelector(".formula-modal__display input").checked;
    const formula = !latex ? "" : display ? `\\[${latex}\\]` : `\\(${latex}\\)`;

    field.value = field.value.slice(0, start) + formula + field.value.slice(end);
    close();

    const caret = start + formula.length;
    field.focus();
    field.setSelectionRange(caret, caret);
    field.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function close() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("formula-modal-open");
    window.mathVirtualKeyboard?.hide();
    target = null;
  }

  function updatePreview(field, preview) {
    const text = field.value;
    if (!HAS_FORMULA.test(text) || !window.MathRender) {
      preview.hidden = true;
      return;
    }
    const content = preview.querySelector(".formula-preview__content");
    content.textContent = text;
    window.MathRender.render(content);
    preview.hidden = false;
  }

  function attach(field) {
    if (field.dataset.formulaEditorReady) return;
    field.dataset.formulaEditorReady = "true";

    const tools = document.createElement("div");
    tools.className = "formula-tools";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "formula-tools__button";
    button.innerHTML = '<span aria-hidden="true">∑</span> Insertar fórmula';
    // mousedown robaría el foco antes de leer la posición del cursor
    button.addEventListener("mousedown", (event) => event.preventDefault());
    button.addEventListener("click", () => open(field));

    const preview = document.createElement("div");
    preview.className = "formula-preview";
    preview.hidden = true;
    preview.innerHTML =
      '<span class="formula-preview__label">Vista previa</span><div class="formula-preview__content"></div>';

    tools.append(button, preview);
    (field.closest("[data-formula-anchor]") || field).after(tools);

    const refresh = () => updatePreview(field, preview);
    field.addEventListener("input", refresh);
    // form.reset() no dispara "input" y el valor cambia después del evento
    field.form?.addEventListener("reset", () => setTimeout(refresh));
    refresh();
  }

  function attachAll(root) {
    if (root.matches?.(FIELD_SELECTOR)) attach(root);
    root.querySelectorAll?.(FIELD_SELECTOR).forEach(attach);
  }

  function init() {
    attachAll(document);
    new MutationObserver((mutations) => {
      mutations.forEach((mutation) =>
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) attachAll(node);
        })
      );
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
