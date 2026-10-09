// Resources View JavaScript

document.addEventListener("DOMContentLoaded", function () {
  initializePeriodSelector();
  initializeResourceModal();
  initializeAddFirstResourceButtons();
  initializeDeleteResourceModal();
  initializeLoadingStates();
});

async function loadAvailableClassesForResourceModal() {
  const courseId = document.getElementById("resource_course_id")?.value;
  const subjectId = document.getElementById("resource_subject_id")?.value;
  const period = document.querySelector(
    '#createResourceModal select[name="period"]',
  )?.value;

  const classSelect = document.getElementById("resource_class_number");
  const submitBtn = document.querySelector(
    '#createResourceForm button[type="submit"]',
  );
  if (!classSelect || !submitBtn) return;

  // Reset UI state
  classSelect.innerHTML = '<option value="">CARGANDO CLASES...</option>';
  classSelect.disabled = true;
  submitBtn.disabled = true;

  if (!courseId || !subjectId || !period) {
    classSelect.innerHTML = '<option value="">SELECCIONA UN PERIODO</option>';
    return;
  }

  try {
    const response = await fetch(
      `/resources/api/classes?course_id=${encodeURIComponent(courseId)}&subject_id=${encodeURIComponent(subjectId)}&period=${encodeURIComponent(period)}`,
      {
        method: "GET",
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      },
    );

    const payload = await response.json();
    const items = payload?.data?.items || [];

    if (!response.ok || payload?.success === false) {
      classSelect.innerHTML =
        '<option value="">ERROR AL CARGAR CLASES</option>';
      return;
    }

    if (!items.length) {
      classSelect.innerHTML =
        '<option value="">NO HAY CLASES EN ESTE PERIODO</option>';
      return;
    }

    classSelect.innerHTML = '<option value="">SELECCIONA UNA CLASE</option>';
    items.forEach((item) => {
      const opt = document.createElement("option");
      // El backend de create_resource espera el "número de clase" (class_number), no el id.
      opt.value = String(item.class_number);
      opt.textContent = `CLASE ${item.class_number}${item.title ? ` - ${item.title}` : ""}`;
      classSelect.appendChild(opt);
    });

    classSelect.disabled = false;
    submitBtn.disabled = false;
  } catch (e) {
    classSelect.innerHTML = '<option value="">ERROR AL CARGAR CLASES</option>';
  }
}

// Period Selector Functionality
function initializePeriodSelector() {
  const periodBtns = document.querySelectorAll(".period-btn");
  const periodContents = document.querySelectorAll(".period-content");

  periodBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const period = this.getAttribute("data-period");

      // Remove active class from all buttons
      periodBtns.forEach((b) => b.classList.remove("active"));

      // Add active class to clicked button
      this.classList.add("active");

      // Hide all period contents
      periodContents.forEach((content) => {
        content.style.display = "none";
      });

      // Show selected period content
      const selectedContents = document.querySelectorAll(
        `.period-content[data-period="${period}"]`,
      );
      selectedContents.forEach((content) => {
        content.style.display = "flex";
      });
    });
  });
}

// Resource Modal Functions
function openCreateResourceModal(subjectId = null, period = null) {
  const modal = document.getElementById("createResourceModal");
  if (!modal) return;

  modal.style.display = "flex";

  // Obtener datos del primer subject-section visible si no se pasaron
  const subjectSection = subjectId
    ? document.querySelector(`.subject-section[data-subject-id="${subjectId}"]`)
    : document.querySelector(".subject-section");

  if (subjectSection) {
    const courseId = subjectSection.getAttribute("data-course-id");
    const actualSubjectId =
      subjectId || subjectSection.getAttribute("data-subject-id");

    // Configurar campos ocultos
    const courseIdInput = document.getElementById("resource_course_id");
    const subjectIdInput = document.getElementById("resource_subject_id");

    if (courseIdInput) courseIdInput.value = courseId || "";
    if (subjectIdInput) subjectIdInput.value = actualSubjectId || "";
  }

  // Configurar periodo
  const periodSelect = document.querySelector(
    '#createResourceModal select[name="period"]',
  );
  if (periodSelect) {
    periodSelect.value =
      period ||
      document
        .querySelector(".period-btn.active")
        ?.getAttribute("data-period") ||
      "";
  }

  // Cargar clases disponibles para el periodo/curso/materia
  loadAvailableClassesForResourceModal();
}

function closeCreateResourceModal() {
  const modal = document.getElementById("createResourceModal");
  if (!modal) return;

  modal.style.display = "none";

  const form = document.getElementById("createResourceForm");
  if (form) {
    form.reset();
    document.querySelectorAll(".file-name").forEach((display) => {
      display.textContent = "";
    });
  }

  // Reset select state
  const classSelect = document.getElementById("resource_class_number");
  const submitBtn = document.querySelector(
    '#createResourceForm button[type="submit"]',
  );
  if (classSelect) {
    classSelect.innerHTML = '<option value="">SELECCIONA UNA CLASE</option>';
    classSelect.disabled = true;
  }
  if (submitBtn) submitBtn.disabled = false;
}

// Initialize "Add First Resource" buttons
function initializeAddFirstResourceButtons() {
  document.querySelectorAll(".btn-add-first-resource").forEach((btn) => {
    btn.addEventListener("click", function () {
      openCreateResourceModal(
        this.getAttribute("data-subject-id"),
        this.getAttribute("data-period"),
      );
    });
  });
}

function initializeResourceModal() {
  const modal = document.getElementById("createResourceModal");
  if (!modal) return;

  // Close modal when clicking outside
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeCreateResourceModal();
    }
  });

  // File input display names
  const coverImageInput = document.getElementById("resource_cover_image");
  const resourceFileInput = document.getElementById("resource_file");
  const periodSelect = document.querySelector(
    '#createResourceModal select[name="period"]',
  );

  if (coverImageInput) {
    coverImageInput.addEventListener("change", function () {
      const fileNameDisplay = document.getElementById(
        "resource_cover_image_name",
      );
      if (fileNameDisplay) {
        fileNameDisplay.textContent = this.files[0]?.name || "";
      }
    });
  }

  if (resourceFileInput) {
    resourceFileInput.addEventListener("change", function () {
      const fileNameDisplay = document.getElementById("resource_file_name");
      if (fileNameDisplay) {
        fileNameDisplay.textContent = this.files[0]?.name || "";
      }
    });
  }

  if (periodSelect) {
    periodSelect.addEventListener("change", function () {
      loadAvailableClassesForResourceModal();
    });
  }

  // Handle ESC key to close modal
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeCreateResourceModal();
    }
  });
}

// Delete Resource Modal Functionality
function initializeDeleteResourceModal() {
  initializeDeleteButtons(".open-delete-resource-modal", function (button) {
    const resourceId = button.getAttribute("data-resource-id");
    return `/resources/${resourceId}/delete`;
  });
}

// Loading States Functions
function showLoadingState(button, loadingText = "Procesando...") {
  if (!button) return;

  button.disabled = true;
  button.setAttribute("data-original-text", button.innerHTML);
  button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
}

function hideLoadingState(button) {
  if (!button) return;

  const originalText = button.getAttribute("data-original-text");
  if (originalText) {
    button.innerHTML = originalText;
    button.removeAttribute("data-original-text");
  }
  button.disabled = false;
}

// Initialize loading states for create and delete forms
function initializeLoadingStates() {
  const createForm = document.getElementById("createResourceForm");
  const deleteForm = document.getElementById("deleteConfirmationForm");

  if (createForm) {
    createForm.addEventListener("submit", function () {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn) showLoadingState(submitBtn, "Guardando...");
    });
  }

  if (deleteForm) {
    deleteForm.addEventListener("submit", function () {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn) showLoadingState(submitBtn, "Eliminando...");
    });
  }
}

// Alert auto-dismiss
setTimeout(function () {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    alert.style.transition = "opacity 0.5s ease";
    alert.style.opacity = "0";
    setTimeout(() => alert.remove(), 500);
  });
}, 5000);
