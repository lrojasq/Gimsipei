/**
 * Reproductor de YouTube embebido (lazy / facade).
 *
 * Uso: marcar un elemento con el atributo `data-youtube-embed`.
 * Los links de YouTube que aparezcan en su texto se reemplazan por una
 * miniatura con botón de play; al hacer clic se carga el iframe y el video
 * se reproduce ahí mismo. El iframe no se descarga hasta que el usuario
 * hace clic, así la página no carga el JS de YouTube por cada tarea.
 *
 * El texto original se guarda en `data-original-text` para que la edición
 * de la tarea no pierda el link.
 */
(function () {
  "use strict";

  const URL_REGEX =
    /(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)\/[^\s<>"']+/gi;
  const ID_REGEX = /^[A-Za-z0-9_-]{11}$/;
  const TRAILING_PUNCTUATION = /[.,;:!?)\]]+$/;
  // Texto dentro de estos elementos no se transforma
  const SKIP_SELECTOR = "a, button, script, style, textarea, iframe, code, pre";

  /** Devuelve { id, start } o null si la URL no es un video válido. */
  function parseYouTubeUrl(raw) {
    let url;
    try {
      url = new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`);
    } catch (e) {
      return null;
    }

    const host = url.hostname.replace(/^(www\.|m\.)/, "");
    const parts = url.pathname.split("/").filter(Boolean);
    let id = null;

    if (host === "youtu.be") {
      id = parts[0];
    } else if (parts[0] === "watch") {
      id = url.searchParams.get("v");
    } else if (["shorts", "embed", "live", "v"].includes(parts[0])) {
      id = parts[1];
    }

    if (!id || !ID_REGEX.test(id)) return null;

    return { id, start: parseStart(url.searchParams.get("t") || url.searchParams.get("start")) };
  }

  /** Convierte "90", "90s" o "1h2m30s" a segundos. */
  function parseStart(value) {
    if (!value) return 0;
    if (/^\d+s?$/.test(value)) return parseInt(value, 10);
    const match = value.match(/^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/);
    if (!match) return 0;
    const [, h = 0, m = 0, s = 0] = match;
    return Number(h) * 3600 + Number(m) * 60 + Number(s);
  }

  function buildPlayer({ id, start }) {
    const wrapper = document.createElement("div");
    wrapper.className = "yt-embed";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "yt-facade";
    button.setAttribute("aria-label", "Reproducir video de YouTube");

    const thumb = document.createElement("img");
    thumb.src = `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
    thumb.alt = "";
    thumb.loading = "lazy";
    // Evita que el visor de imágenes abra la miniatura
    thumb.setAttribute("data-gallery-ignore", "");

    const play = document.createElement("span");
    play.className = "yt-play";
    play.setAttribute("aria-hidden", "true");
    play.innerHTML = '<i class="bi bi-play-fill"></i>';

    button.append(thumb, play);
    button.addEventListener("click", () => {
      const params = new URLSearchParams({ autoplay: "1", rel: "0" });
      if (start) params.set("start", String(start));

      const iframe = document.createElement("iframe");
      iframe.src = `https://www.youtube-nocookie.com/embed/${id}?${params}`;
      iframe.title = "Video de YouTube";
      iframe.allow =
        "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      iframe.allowFullscreen = true;

      button.replaceWith(iframe);
      iframe.focus();
    });

    wrapper.appendChild(button);
    return wrapper;
  }

  /** Reemplaza los links de YouTube de un nodo de texto por reproductores. */
  function processTextNode(node) {
    const text = node.nodeValue;
    URL_REGEX.lastIndex = 0;
    if (!URL_REGEX.test(text)) return;
    URL_REGEX.lastIndex = 0;

    const fragment = document.createDocumentFragment();
    let lastIndex = 0;
    let replaced = false;
    let match;

    while ((match = URL_REGEX.exec(text)) !== null) {
      const raw = match[0].replace(TRAILING_PUNCTUATION, "");
      const video = parseYouTubeUrl(raw);
      if (!video) continue;

      fragment.append(text.slice(lastIndex, match.index));
      fragment.append(buildPlayer(video));
      lastIndex = match.index + raw.length;
      replaced = true;
    }

    if (!replaced) return;
    fragment.append(text.slice(lastIndex));
    node.replaceWith(fragment);
  }

  function processElement(root) {
    if (root.hasAttribute("data-original-text")) return;
    root.setAttribute("data-original-text", root.textContent.trim());

    // Contenido con HTML: un <a> que apunta a YouTube se reemplaza entero,
    // si no el reproductor quedaría dentro del link
    root.querySelectorAll("a[href]").forEach((link) => {
      const video = parseYouTubeUrl(link.getAttribute("href"));
      if (video) link.replaceWith(buildPlayer(video));
    });

    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) =>
        node.parentElement.closest(SKIP_SELECTOR)
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT,
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(processTextNode);
  }

  function init() {
    document.querySelectorAll("[data-youtube-embed]").forEach(processElement);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
