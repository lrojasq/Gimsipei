// Books View JavaScript

document.addEventListener("DOMContentLoaded", function () {
  initializeDeleteBookModal();
  initializeFileInputs();
  initializeFilter();
  initializeFormSubmit();

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
  if (title) title.textContent = "CREAR LIBRO";
  
  const bookIdInput = document.getElementById("book_id");
  if (bookIdInput) bookIdInput.value = "";

  // Clear file names
  const bookFileName = document.getElementById("book_file_name");
  const coverImageName = document.getElementById("book_cover_image_name");
  if (bookFileName) bookFileName.textContent = "";
  if (coverImageName) coverImageName.textContent = "";

  // Reset submit button
  resetSubmitButton();

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

// Initialize Delete Book Modal
function initializeDeleteBookModal() {
  const deleteButtons = document.querySelectorAll(".open-delete-book-modal");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      const bookId = this.getAttribute("data-book-id");
      const deleteUrl = `/books/${bookId}/delete`;

      showDeleteConfirmationModal(deleteUrl);
    });
  });
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

// Initialize Form Submit
function initializeFormSubmit() {
  const form = document.getElementById("createBookForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      // Prevent double submit
      if (form.dataset.submitting === "true") {
        e.preventDefault();
        return false;
      }

      // Validate required fields
      const title = document.getElementById("book_title");
      const author = document.getElementById("book_author");
      const targetAudience = document.getElementById("book_target_audience");

      if (!title || !title.value.trim()) {
        e.preventDefault();
        alert("Por favor ingrese el título del libro");
        return false;
      }

      if (!author || !author.value.trim()) {
        e.preventDefault();
        alert("Por favor ingrese el autor del libro");
        return false;
      }

      if (!targetAudience || !targetAudience.value) {
        e.preventDefault();
        alert("Por favor seleccione la audiencia del libro");
        return false;
      }

      // Form is valid, show spinner and allow submission
      form.dataset.submitting = "true";
      showSubmitSpinner();
      return true;
    });
  }
}

// Show spinner on submit button
function showSubmitSpinner() {
  const submitBtn = document.getElementById("submitBookBtn");
  if (!submitBtn) return;

  const btnText = submitBtn.querySelector(".btn-text");
  const btnSpinner = submitBtn.querySelector(".btn-spinner");

  submitBtn.disabled = true;
  if (btnText) btnText.style.display = "none";
  if (btnSpinner) btnSpinner.style.display = "inline";
}

// Reset submit button
function resetSubmitButton() {
  const submitBtn = document.getElementById("submitBookBtn");
  if (!submitBtn) return;

  const btnText = submitBtn.querySelector(".btn-text");
  const btnSpinner = submitBtn.querySelector(".btn-spinner");

  submitBtn.disabled = false;
  if (btnText) btnText.style.display = "inline";
  if (btnSpinner) btnSpinner.style.display = "none";
  
  const form = document.getElementById("createBookForm");
  if (form) form.dataset.submitting = "false";
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
    visibleBooks = visibleBooks.filter((bookLink) => {
      const bookDiv = bookLink.querySelector(".book");
      const title = bookDiv?.getAttribute("data-book-title") || "";
      const author = bookDiv?.getAttribute("data-book-author") || "";
      return title.includes(searchTerm) || author.includes(searchTerm);
    });
  }

  // Filter by genre (target_audience)
  if (filterGenero) {
    visibleBooks = visibleBooks.filter((bookLink) => {
      const bookDiv = bookLink.querySelector(".book");
      const bookAudience = bookDiv?.getAttribute("data-book-audience");
      return bookAudience === filterGenero;
    });
  }

  // Filter by grade level
  if (filterGrado) {
    visibleBooks = visibleBooks.filter((bookLink) => {
      const bookDiv = bookLink.querySelector(".book");
      const bookGrade = bookDiv?.getAttribute("data-book-grade");
      return bookGrade && bookGrade.toString() === filterGrado.toString();
    });
  }

  // Sort alphabetically
  if (filterAlfabetico) {
    visibleBooks.sort((a, b) => {
      const bookDivA = a.querySelector(".book");
      const bookDivB = b.querySelector(".book");
      const titleA = bookDivA?.getAttribute("data-book-title") || "";
      const titleB = bookDivB?.getAttribute("data-book-title") || "";
      return filterAlfabetico === "asc"
        ? titleA.localeCompare(titleB)
        : titleB.localeCompare(titleA);
    });
  }

  // Hide all books first
  books.forEach((book) => {
    book.style.display = "none";
  });

  // Show filtered books and reorder them in the DOM
  const booksGrid = document.querySelector(".books-grid");
  const searchBar = document.querySelector(".search-bar");
  
  if (booksGrid) {
    // If sorting or filtering, reorder the books in the DOM
    visibleBooks.forEach((book) => {
      book.style.display = "flex";
      // Move the book to maintain order
      booksGrid.appendChild(book);
    });
    
    // Keep search bar at the top
    if (searchBar && booksGrid.contains(searchBar)) {
      booksGrid.insertBefore(searchBar, booksGrid.firstChild);
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
