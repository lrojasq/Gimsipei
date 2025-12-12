// Subject Classes JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Get course and subject IDs from data attributes
  const container = document.querySelector(".container_category");
  const courseId = container ? container.getAttribute("data-course-id") : null;
  const subjectId = container
    ? container.getAttribute("data-subject-id")
    : null;

  // Set course and subject IDs for modals
  if (courseId && subjectId) {
    const classCourseIdInput = document.getElementById("class_course_id");
    const classSubjectIdInput = document.getElementById("class_subject_id");

    if (classCourseIdInput) classCourseIdInput.value = courseId;
    if (classSubjectIdInput) classSubjectIdInput.value = subjectId;
  }

  // Period filter functionality
  const periodButtons = document.querySelectorAll(".period-btn");
  const periodContainers = document.querySelectorAll(
    ".period-classes-container"
  );
  const classPeriodInput = document.getElementById("class_period");

  periodButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const period = this.getAttribute("data-period");

      // Update active button
      periodButtons.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      // Show corresponding period container
      periodContainers.forEach((container) => {
        if (container.getAttribute("data-period") === period) {
          container.style.display = "block";
        } else {
          container.style.display = "none";
        }
      });

      // Update hidden input for creating classes
      if (classPeriodInput) {
        classPeriodInput.value = period;
      }
    });
  });

  // Add class button
  const addClassBtn = document.getElementById("addClassBtn");
  const addFirstClassBtns = document.querySelectorAll(".btn-add-first-class");

  if (addClassBtn) {
    addClassBtn.addEventListener("click", function () {
      openCreateClassModal();
    });
  }

  addFirstClassBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const period = this.getAttribute("data-period");
      openCreateClassModal(period);
    });
  });

  // Edit class buttons
  const editButtons = document.querySelectorAll(".btn-edit");
  editButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const classId = this.getAttribute("data-class-id");
      openEditClassModal(classId);
    });
  });

  // Initialize delete class buttons using delete_modal.js
  initializeDeleteButtons(".open-delete-class-modal", function (button) {
    const classId = button.getAttribute("data-class-id");
    return `/classes/delete/${classId}`;
  });

  // File upload display for create modal
  const fileInput = document.getElementById("class_cover");
  const fileName = document.getElementById("class_cover_name");

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        fileName.textContent = this.files[0].name;
      } else {
        fileName.textContent = "";
      }
    });
  }

  // File upload display for edit modal
  const editFileInput = document.getElementById("edit_class_cover");
  const editFileName = document.getElementById("edit_class_cover_name");

  if (editFileInput) {
    editFileInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        editFileName.textContent = this.files[0].name;
      } else {
        editFileName.textContent = "";
      }
    });
  }

  // initializeDeleteModalListeners() ya se llama automáticamente en delete_modal.js

  // Initialize loading states for forms
  initializeLoadingStates();
});

// Loading States Functions
function showLoadingState(button, loadingText = "Procesando...") {
  if (!button) return;

  button.disabled = true;
  const originalText = button.innerHTML;
  button.setAttribute("data-original-text", originalText);
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

// Initialize loading states for create and edit forms
function initializeLoadingStates() {
  // Create class form
  const createForm = document.getElementById("createClassForm");
  if (createForm) {
    createForm.addEventListener("submit", function (e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn) {
        showLoadingState(submitBtn, "Guardando...");
      }
    });
  }

// Edit and delete forms
["editClassForm", "deleteConfirmationForm"].forEach((formId) => {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener("submit", function (e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const loadingText = formId === "editClassForm" ? "Actualizando..." : "Eliminando...";
                showLoadingState(submitBtn, loadingText);
            }
        });
    }
});
}

// Open create class modal
function openCreateClassModal(period = null) {
  const modal = document.getElementById("createClassModal");
  const classPeriodSelect = document.querySelector(
    '#createClassModal select[name="period"]'
  );

  // Reset form
  document.getElementById("createClassForm").reset();
  document.getElementById("class_cover_name").textContent = "";

  // Set period if provided
  if (period && classPeriodSelect) {
    classPeriodSelect.value = period;
  } else {
    // Use currently active period
    const activeBtn = document.querySelector(".period-btn.active");
    if (activeBtn && classPeriodSelect) {
      classPeriodSelect.value = activeBtn.getAttribute("data-period");
    }
  }

  modal.style.display = "flex";
}

// Close create class modal
function closeCreateClassModal() {
  const modal = document.getElementById("createClassModal");
  modal.style.display = "none";
}

// Open edit class modal
function openEditClassModal(classId) {
  const modal = document.getElementById("editClassModal");
  const form = document.getElementById("editClassForm");

  if (!modal || !form) {
    console.error("Edit modal or form not found");
    return;
  }

  // Set form action
  form.action = `/classes/update/${classId}`;

  // Get data from server (Python handles the logic)
  fetch(`/classes/get/${classId}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Error al cargar los datos de la clase: " + data.error);
        return;
      }

      // Populate form fields
      document.getElementById("edit_class_id").value = classId;
      document.getElementById("edit_class_number").value =
        data.class_number || "";
      document.getElementById("edit_class_title").value = data.title || "";
      document.getElementById("edit_class_description").value =
        data.description || "";
      document.getElementById("edit_class_period").value = data.period || "";

      // Get course_id and subject_id from page data attributes
      const container = document.querySelector(".container_category");
      const courseId =
        data.course_id ||
        (container ? container.getAttribute("data-course-id") : "");
      const subjectId =
        data.subject_id ||
        (container ? container.getAttribute("data-subject-id") : "");
      document.getElementById("edit_class_course_id").value = courseId;
      document.getElementById("edit_class_subject_id").value = subjectId;

      // Show current cover image if exists
      const currentCoverPreview = document.getElementById(
        "current_cover_preview"
      );
      const currentCoverImage = document.getElementById("current_cover_image");

      if (data.cover_image) {
        currentCoverImage.src = data.cover_image;
        currentCoverPreview.style.display = "block";
      } else {
        currentCoverPreview.style.display = "none";
      }

      // Reset file input
      document.getElementById("edit_class_cover").value = "";
      document.getElementById("edit_class_cover_name").textContent = "";

      // Show modal
      modal.style.display = "flex";
    })
    .catch((error) => {
      console.error("Error loading class data:", error);
      alert("Error al cargar los datos de la clase");
    });
}

// Close edit class modal
function closeEditClassModal() {
  const modal = document.getElementById("editClassModal");
  modal.style.display = "none";
}

// Close modals when clicking outside
document.addEventListener("click", function (event) {
  const createModal = document.getElementById("createClassModal");
  const editModal = document.getElementById("editClassModal");

  // Check if click is on modal background (not on modal content)
  if (event.target === createModal) {
    closeCreateClassModal();
  }

  if (event.target === editModal) {
    closeEditClassModal();
  }

  // Delete modal is handled by delete_modal.js
});

// Close modals with Escape key
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    closeCreateClassModal();
    closeEditClassModal();
    // Delete modal ESC handling is done by delete_modal.js
  }
});
