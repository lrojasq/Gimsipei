/**
 * Función genérica para mostrar modal de confirmación de eliminación
 * @param {string} actionUrl - URL donde se enviará el formulario de eliminación
 */
function showDeleteConfirmationModal(actionUrl) {
  const modal = document.getElementById("deleteConfirmationModal");
  const form = document.getElementById("deleteConfirmationForm");

  if (!modal || !form) {
    console.error("Modal o formulario de confirmación no encontrado");
    return;
  }

  // Establecer la acción del formulario
  form.action = actionUrl;

  // Resetear el estado del botón
  resetDeleteButton();

  // Mostrar modal
  modal.classList.add("show");
  modal.style.display = "flex";
  modal.removeAttribute("aria-hidden");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("role", "dialog");
}

/**
 * Función para resetear el botón de eliminar a su estado original
 */
function resetDeleteButton() {
  const deleteBtn = document.querySelector(
    "#deleteConfirmationForm .btn-delete"
  );
  if (!deleteBtn) return;

  const btnText = deleteBtn.querySelector(".btn-text");
  const btnSpinner = deleteBtn.querySelector(".btn-spinner");

  deleteBtn.disabled = false;
  if (btnText) btnText.style.display = "inline";
  if (btnSpinner) btnSpinner.style.display = "none";
}

/**
 * Función para mostrar el spinner en el botón de eliminar
 */
function showDeleteSpinner() {
  const deleteBtn = document.querySelector(
    "#deleteConfirmationForm .btn-delete"
  );
  if (!deleteBtn) return;

  const btnText = deleteBtn.querySelector(".btn-text");
  const btnSpinner = deleteBtn.querySelector(".btn-spinner");

  deleteBtn.disabled = true;
  if (btnText) btnText.style.display = "none";
  if (btnSpinner) btnSpinner.style.display = "inline";
}

/**
 * Función para cerrar el modal de confirmación
 */
function closeDeleteModal() {
  const modal = document.getElementById("deleteConfirmationModal");
  if (!modal) return;

  modal.classList.remove("show");
  modal.style.display = "none";
  modal.setAttribute("aria-hidden", "true");
  modal.removeAttribute("aria-modal");
  modal.removeAttribute("role");

  // Resetear el botón al cerrar
  resetDeleteButton();
}

/**
 * Inicializar listeners del modal (cerrar)
 * Esta función debe llamarse una vez cuando se carga la página
 */
function initializeDeleteModalListeners() {
  setTimeout(function () {
    const modal = document.getElementById("deleteConfirmationModal");
    const form = document.getElementById("deleteConfirmationForm");
    if (!modal) return;

    const closeModalBtns = modal.querySelectorAll(".close-modal");
    const bgBack = modal.querySelector(".bg-back");

    // Listener para el submit del formulario (mostrar spinner)
    if (form) {
      form.addEventListener("submit", function (e) {
        // Prevenir doble submit
        if (form.dataset.submitting === "true") {
          e.preventDefault();
          return;
        }
        form.dataset.submitting = "true";
        showDeleteSpinner();
      });
    }

    // Listeners para los botones de cerrar
    closeModalBtns.forEach((btn) => {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        closeDeleteModal();
      });
    });

    // Listener para el fondo
    if (bgBack) {
      bgBack.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        closeDeleteModal();
      });
    }

    // Listener para la tecla ESC
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.style.display === "flex") {
        closeDeleteModal();
      }
    });
  }, 200);
}

/**
 * Inicializar botones de eliminación con clase específica
 * @param {string} buttonSelector - Selector CSS para los botones de eliminar (ej: '.open-delete-resource-modal')
 * @param {function} getDeleteUrl - Función que recibe el elemento del botón y retorna la URL de eliminación
 */
function initializeDeleteButtons(buttonSelector, getDeleteUrl) {
  setTimeout(function () {
    const deleteButtons = document.querySelectorAll(buttonSelector);

    deleteButtons.forEach((button) => {
      button.addEventListener("click", function (e) {
        e.preventDefault();
        const deleteUrl = getDeleteUrl(this);

        if (deleteUrl) {
          showDeleteConfirmationModal(deleteUrl);
        }
      });
    });
  }, 100);
}
