/**
 * Visor de imágenes (lightbox) reutilizable.
 *
 * Uso: marcar un contenedor con el atributo `data-image-gallery`.
 * Todas las <img> dentro de ese contenedor se pueden ampliar y se navega
 * entre ellas en el orden en que aparecen. Para excluir una imagen,
 * agregarle `data-gallery-ignore`.
 */
(function () {
  "use strict";

  const MIN_SCALE = 1;
  const MAX_SCALE = 4;
  const SWIPE_THRESHOLD = 50;

  let overlay, imgEl, counterEl, captionEl, prevBtn, nextBtn, zoomBtn, stage;
  let images = [];
  let index = 0;
  let lastFocused = null;

  // Estado de zoom / arrastre
  let scale = 1;
  let tx = 0;
  let ty = 0;
  let dragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let startTx = 0;
  let startTy = 0;
  let moved = false;

  function buildOverlay() {
    overlay = document.createElement("div");
    overlay.className = "ig-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Visor de imágenes");
    overlay.hidden = true;

    overlay.innerHTML = `
      <div class="ig-toolbar">
        <span class="ig-counter" aria-live="polite"></span>
        <div class="ig-toolbar-actions">
          <button type="button" class="ig-btn ig-zoom" aria-label="Ampliar" title="Ampliar">
            <i class="bi bi-zoom-in"></i>
          </button>
          <button type="button" class="ig-btn ig-close" aria-label="Cerrar" title="Cerrar (Esc)">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
      <button type="button" class="ig-btn ig-nav ig-prev" aria-label="Imagen anterior" title="Anterior">
        <i class="bi bi-chevron-left"></i>
      </button>
      <div class="ig-stage">
        <img class="ig-image" alt="" draggable="false">
      </div>
      <button type="button" class="ig-btn ig-nav ig-next" aria-label="Imagen siguiente" title="Siguiente">
        <i class="bi bi-chevron-right"></i>
      </button>
      <p class="ig-caption"></p>
    `;

    document.body.appendChild(overlay);

    stage = overlay.querySelector(".ig-stage");
    imgEl = overlay.querySelector(".ig-image");
    counterEl = overlay.querySelector(".ig-counter");
    captionEl = overlay.querySelector(".ig-caption");
    prevBtn = overlay.querySelector(".ig-prev");
    nextBtn = overlay.querySelector(".ig-next");
    zoomBtn = overlay.querySelector(".ig-zoom");

    overlay.querySelector(".ig-close").addEventListener("click", close);
    prevBtn.addEventListener("click", () => go(-1));
    nextBtn.addEventListener("click", () => go(1));
    zoomBtn.addEventListener("click", () => setScale(scale > 1 ? 1 : 2));

    // Clic en el fondo (fuera de la imagen) cierra el visor
    stage.addEventListener("click", (e) => {
      // Si venimos de arrastrar la imagen, el click no debe cerrar
      if (moved) return;
      if (e.target === stage) close();
    });

    // Doble clic en la imagen alterna el zoom
    imgEl.addEventListener("dblclick", (e) => {
      e.preventDefault();
      setScale(scale > 1 ? 1 : 2);
    });

    // Rueda del mouse: zoom
    stage.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.2 : 1 / 1.2;
        setScale(scale * factor);
      },
      { passive: false }
    );

    imgEl.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointercancel", onPointerUp);

    document.addEventListener("keydown", onKeyDown);
  }

  function collectImages(root) {
    return Array.from(root.querySelectorAll("img")).filter(
      (img) => !img.hasAttribute("data-gallery-ignore") && img.getAttribute("src")
    );
  }

  function open(root, clickedImg) {
    if (!overlay) buildOverlay();

    images = collectImages(root);
    index = Math.max(0, images.indexOf(clickedImg));
    lastFocused = document.activeElement;

    overlay.hidden = false;
    document.body.classList.add("ig-open");
    const single = images.length <= 1;
    prevBtn.hidden = single;
    nextBtn.hidden = single;

    show();
    overlay.querySelector(".ig-close").focus();
  }

  function close() {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    document.body.classList.remove("ig-open");
    imgEl.removeAttribute("src");
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
  }

  function go(step) {
    if (images.length <= 1) return;
    index = (index + step + images.length) % images.length;
    show();
  }

  function show() {
    const source = images[index];
    resetZoom();
    imgEl.src = source.currentSrc || source.src;
    imgEl.alt = source.alt || "";
    captionEl.textContent = source.alt || "";
    captionEl.hidden = !source.alt;
    counterEl.textContent = `${index + 1} / ${images.length}`;
    preload(index + 1);
    preload(index - 1);
  }

  function preload(i) {
    if (images.length <= 1) return;
    const target = images[(i + images.length) % images.length];
    const pre = new Image();
    pre.src = target.currentSrc || target.src;
  }

  // ---------- Zoom y arrastre ----------

  function resetZoom() {
    scale = 1;
    tx = 0;
    ty = 0;
    applyTransform();
  }

  function setScale(value) {
    scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, value));
    if (scale === 1) {
      tx = 0;
      ty = 0;
    }
    clampTranslation();
    applyTransform();
  }

  function clampTranslation() {
    const maxX = (imgEl.offsetWidth * (scale - 1)) / 2;
    const maxY = (imgEl.offsetHeight * (scale - 1)) / 2;
    tx = Math.min(maxX, Math.max(-maxX, tx));
    ty = Math.min(maxY, Math.max(-maxY, ty));
  }

  function applyTransform() {
    imgEl.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
    overlay.classList.toggle("ig-zoomed", scale > 1);
    const zoomed = scale > 1;
    zoomBtn.setAttribute("aria-label", zoomed ? "Reducir" : "Ampliar");
    zoomBtn.title = zoomed ? "Reducir" : "Ampliar";
    zoomBtn.querySelector("i").className = zoomed ? "bi bi-zoom-out" : "bi bi-zoom-in";
  }

  function onPointerDown(e) {
    if (e.button !== undefined && e.button !== 0) return;
    e.preventDefault();
    dragging = true;
    moved = false;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    startTx = tx;
    startTy = ty;
    imgEl.classList.add("ig-dragging");
  }

  function onPointerMove(e) {
    if (!dragging) return;
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) moved = true;

    if (scale > 1) {
      tx = startTx + dx;
      ty = startTy + dy;
      clampTranslation();
      applyTransform();
    }
  }

  function onPointerUp(e) {
    if (!dragging) return;
    dragging = false;
    imgEl.classList.remove("ig-dragging");

    // Sin zoom, deslizar horizontalmente cambia de imagen
    if (scale === 1 && moved) {
      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;
      if (Math.abs(dx) > SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
        go(dx < 0 ? 1 : -1);
      }
    }

    // El click de compatibilidad, si el navegador lo emite, llega en este mismo
    // turno y tiene que ver moved=true para que arrastrar no cierre el visor.
    // Recien despues se limpia: en touch un swipe no emite ningun click, y sin
    // esto el flag quedaba pegado y se comia el siguiente tap en el fondo.
    if (moved) setTimeout(() => { moved = false; }, 0);
  }

  // ---------- Teclado ----------

  function onKeyDown(e) {
    if (!overlay || overlay.hidden) return;

    switch (e.key) {
      case "Escape":
        e.preventDefault();
        close();
        break;
      case "ArrowLeft":
        e.preventDefault();
        go(-1);
        break;
      case "ArrowRight":
        e.preventDefault();
        go(1);
        break;
      case "+":
      case "=":
        setScale(scale * 1.2);
        break;
      case "-":
        setScale(scale / 1.2);
        break;
      case "Tab":
        trapFocus(e);
        break;
    }
  }

  function trapFocus(e) {
    const focusables = Array.from(overlay.querySelectorAll("button")).filter(
      (el) => !el.hidden
    );
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  // ---------- Inicialización ----------

  function init() {
    document.querySelectorAll("[data-image-gallery]").forEach((root) => {
      collectImages(root).forEach((img) => {
        img.classList.add("ig-thumb");
        img.setAttribute("tabindex", "0");
        img.setAttribute("role", "button");
        if (!img.getAttribute("aria-label")) {
          img.setAttribute("aria-label", `Ampliar imagen${img.alt ? ": " + img.alt : ""}`);
        }
      });

      root.addEventListener("click", (e) => {
        const img = e.target.closest("img");
        if (!img || !root.contains(img) || img.hasAttribute("data-gallery-ignore")) return;
        e.preventDefault();
        open(root, img);
      });

      root.addEventListener("keydown", (e) => {
        if (e.key !== "Enter" && e.key !== " ") return;
        const img = e.target.closest("img.ig-thumb");
        if (!img) return;
        e.preventDefault();
        open(root, img);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
