// Book Reader - ePub Viewer
document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const bookViewer = document.getElementById("bookViewer");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const prevPageBtn = document.getElementById("prevPage");
  const nextPageBtn = document.getElementById("nextPage");
  const pageInfo = document.getElementById("pageInfo");
  const fontSizeDecrease = document.getElementById("fontSizeDecrease");
  const fontSizeIncrease = document.getElementById("fontSizeIncrease");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");

  // Get book configuration from data attributes
  const bookConfig = {
    fileUrl: bookViewer.dataset.fileUrl,
    bookId: bookViewer.dataset.bookId,
    title: bookViewer.dataset.bookTitle,
  };

  // Variables
  let book = null;
  let rendition = null;
  let currentFontSize = 100;

  // Initialize book
  function initBook() {
    if (!bookConfig.fileUrl) {
      showError("No se encontró el archivo del libro");
      return;
    }

    book = ePub(bookConfig.fileUrl);

    rendition = book.renderTo(bookViewer, {
      width: "100%",
      height: "100%",
      spread: "auto",
      flow: "paginated",
    });

    // Display the book
    rendition
      .display()
      .then(() => {
        hideLoading();
        updatePageInfo();
      })
      .catch((err) => {
        console.error("Error displaying book:", err);
        showError("Error al cargar el libro");
      });

    // Event listeners for rendition
    rendition.on("relocated", function (location) {
      updateProgress(location);
      updatePageInfo();
      saveReadingPosition(location);
    });

    rendition.on("rendered", function () {
      updatePageInfo();
    });

    // Restore reading position
    restoreReadingPosition();

    // Keyboard navigation
    document.addEventListener("keydown", handleKeyboard);
  }

  // Navigation functions
  function nextPage() {
    if (rendition) {
      rendition.next();
    }
  }

  function prevPage() {
    if (rendition) {
      rendition.prev();
    }
  }

  // Update page info
  function updatePageInfo() {
    if (rendition && rendition.location) {
      const location = rendition.location;
      if (location.start) {
        const current = location.start.displayed.page;
        const total = location.start.displayed.total;
        pageInfo.textContent = `Página ${current} de ${total}`;
      }
    }
  }

  // Update progress bar
  function updateProgress(location) {
    if (book && location) {
      const percentage = book.locations.percentageFromCfi(location.start.cfi);
      const percent = Math.round(percentage * 100);
      progressBar.style.width = percent + "%";
      progressText.textContent = percent + "%";
    }
  }

  // Generate locations for progress
  function generateLocations() {
    book.ready
      .then(() => {
        return book.locations.generate(1024);
      })
      .then(() => {
        console.log("Locations generated");
      });
  }

  // Font size controls
  function changeFontSize(delta) {
    currentFontSize += delta;
    currentFontSize = Math.max(50, Math.min(200, currentFontSize));
    rendition.themes.fontSize(currentFontSize + "%");
  }

  // Keyboard navigation
  function handleKeyboard(e) {
    switch (e.key) {
      case "ArrowLeft":
        prevPage();
        break;
      case "ArrowRight":
        nextPage();
        break;
    }
  }

  // Save/Restore reading position
  function saveReadingPosition(location) {
    if (location && location.start) {
      const key = "book_position_" + bookConfig.bookId;
      localStorage.setItem(key, location.start.cfi);
    }
  }

  function restoreReadingPosition() {
    const key = "book_position_" + bookConfig.bookId;
    const cfi = localStorage.getItem(key);
    if (cfi && rendition) {
      rendition.display(cfi);
    }
  }

  // Loading/Error handling
  function hideLoading() {
    loadingOverlay.classList.add("hidden");
    generateLocations();
  }

  function showError(message) {
    loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-exclamation-triangle" style="color: #ff6b6b;"></i>
                <p>${message}</p>
                <a href="${window.location.origin}/books" class="back-btn" style="margin-top: 1rem; display: inline-block;">
                    <i class="fas fa-arrow-left"></i> Volver a Libros
                </a>
            </div>
        `;
  }

  // Event listeners
  prevPageBtn.addEventListener("click", prevPage);
  nextPageBtn.addEventListener("click", nextPage);
  fontSizeDecrease.addEventListener("click", () => changeFontSize(-10));
  fontSizeIncrease.addEventListener("click", () => changeFontSize(10));

  // Touch/Swipe support for mobile
  let touchStartX = 0;
  let touchEndX = 0;

  bookViewer.addEventListener(
    "touchstart",
    function (e) {
      touchStartX = e.changedTouches[0].screenX;
    },
    false
  );

  bookViewer.addEventListener(
    "touchend",
    function (e) {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    },
    false
  );

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        nextPage();
      } else {
        prevPage();
      }
    }
  }

  // Initialize
  initBook();
});
