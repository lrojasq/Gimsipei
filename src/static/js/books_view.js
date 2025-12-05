// Books View JavaScript

document.addEventListener("DOMContentLoaded", function () {
  initializeDeleteBookModal();
  initializeEditBookModal();
  initializeFileInputs();
  initializeFilter();
  initializeDeleteModalListeners();

  // Add book button
  const addBookBtn = document.getElementById("addBookBtn");
  if (addBookBtn) {
    addBookBtn.addEventListener("click", function (e) {
      e.preventDefault();
      openCreateBookModal();
    });
  }

  // Add first book button
  const addFirstBookBtn = document.querySelector(".btn-add-first-book");
  if (addFirstBookBtn) {
    addFirstBookBtn.addEventListener("click", function (e) {
      e.preventDefault();
      openCreateBookModal();
    });
  }
});

// Open Create Book Modal
function openCreateBookModal() {
  const modal = document.getElementById("createBookModal");
  const form = document.getElementById("createBookForm");
  const title = document.getElementById("bookModalTitle");

  if (!modal || !form) return;

  // Reset form
  form.reset();
  form.action = "/books/create";
  title.textContent = "CREAR LIBRO";
  document.getElementById("book_id").value = "";

  // Clear file names
  document.getElementById("book_file_name").textContent = "";
  document.getElementById("book_cover_image_name").textContent = "";

  // Show modal
  modal.style.display = "flex";
}

// Close Create Book Modal
function closeCreateBookModal() {
  const modal = document.getElementById("createBookModal");
  if (modal) {
    modal.style.display = "none";
  }
}

// Initialize Edit Book Modal - Removed as per design requirements
function initializeEditBookModal() {
  // Edit functionality removed per design requirements
}

// Initialize Delete Book Modal
function initializeDeleteBookModal() {
  setTimeout(function () {
    const deleteButtons = document.querySelectorAll(".open-delete-book-modal");

    deleteButtons.forEach((button) => {
      button.addEventListener("click", function (e) {
        e.preventDefault();
        const bookId = this.getAttribute("data-book-id");
        const deleteUrl = `/books/${bookId}/delete`;

        showDeleteConfirmationModal(deleteUrl);
      });
    });
  }, 100);
}

// Initialize File Inputs
function initializeFileInputs() {
  // Book file input
  const bookFileInput = document.getElementById("book_file");
  if (bookFileInput) {
    bookFileInput.addEventListener("change", function () {
      const fileName = this.files[0] ? this.files[0].name : "";
      document.getElementById("book_file_name").textContent = fileName;
    });
  }

  // Cover image input
  const coverImageInput = document.getElementById("book_cover_image");
  if (coverImageInput) {
    coverImageInput.addEventListener("change", function () {
      const fileName = this.files[0] ? this.files[0].name : "";
      document.getElementById("book_cover_image_name").textContent = fileName;
    });
  }
}

// Initialize Filter
function initializeFilter() {
  const filterAlfabetico = document.getElementById("filter_alfabetico");
  const filterGenero = document.getElementById("filter_genero");
  const filterGrado = document.getElementById("filter_grado");
  const removeFiltersBtn = document.getElementById("removeFiltersBtn");

  if (filterAlfabetico) {
    filterAlfabetico.addEventListener("change", applyFilters);
  }

  if (filterGenero) {
    filterGenero.addEventListener("change", applyFilters);
  }

  if (filterGrado) {
    filterGrado.addEventListener("change", applyFilters);
  }

  if (removeFiltersBtn) {
    removeFiltersBtn.addEventListener("click", function () {
      if (filterAlfabetico) filterAlfabetico.value = "";
      if (filterGenero) filterGenero.value = "";
      if (filterGrado) filterGrado.value = "";
      const searchInput = document.getElementById("searchBooks");
      if (searchInput) searchInput.value = "";
      applyFilters();
    });
  }

  // Search functionality
  const searchInput = document.getElementById("searchBooks");
  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
}

// Apply Filters
function applyFilters() {
  const books = document.querySelectorAll(".book-link");
  const filterAlfabetico =
    document.getElementById("filter_alfabetico")?.value || "";
  const filterGenero = document.getElementById("filter_genero")?.value || "";
  const filterGrado = document.getElementById("filter_grado")?.value || "";
  const searchTerm =
    document.getElementById("searchBooks")?.value.toLowerCase() || "";

  let visibleBooks = Array.from(books);

  // Filter by search term
  if (searchTerm) {
    visibleBooks = visibleBooks.filter((book) => {
      const title = book.getAttribute("data-book-title") || "";
      const author = book.getAttribute("data-book-author") || "";
      return title.includes(searchTerm) || author.includes(searchTerm);
    });
  }

  // Filter by genre (target_audience)
  if (filterGenero) {
    visibleBooks = visibleBooks.filter((book) => {
      return book.getAttribute("data-book-audience") === filterGenero;
    });
  }

  // Filter by grade level
  if (filterGrado) {
    visibleBooks = visibleBooks.filter((book) => {
      return book.getAttribute("data-book-grade") === filterGrado;
    });
  }

  // Sort alphabetically
  if (filterAlfabetico) {
    visibleBooks.sort((a, b) => {
      const titleA = a.getAttribute("data-book-title") || "";
      const titleB = b.getAttribute("data-book-title") || "";
      if (filterAlfabetico === "asc") {
        return titleA.localeCompare(titleB);
      } else {
        return titleB.localeCompare(titleA);
      }
    });
  }

  // Hide all books first
  books.forEach((book) => {
    book.style.display = "none";
  });

  // Show filtered books
  visibleBooks.forEach((book) => {
    book.style.display = "flex";
  });

  // Reorder books in DOM if sorted
  if (filterAlfabetico && visibleBooks.length > 0) {
    const booksGrid = document.querySelector(".books-grid");
    if (booksGrid) {
      visibleBooks.forEach((book) => {
        booksGrid.appendChild(book);
      });
    }
  }
}

// Close modal when clicking outside
document.addEventListener("click", function (e) {
  const modal = document.getElementById("createBookModal");
  if (modal && e.target === modal) {
    closeCreateBookModal();
  }
});

// Close modal with Escape key
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    closeCreateBookModal();
  }
});
