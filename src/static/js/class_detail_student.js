// Class Detail - Student View JavaScript

document.addEventListener("DOMContentLoaded", function () {
  initializeFileUpload();
  initializeMarkAsViewed();
  initializeSubmitForm();
  initializeScrollIndicator();
});

// File Upload Preview
function initializeFileUpload() {
  const fileInput = document.getElementById("submission_file");
  const fileName = document.getElementById("submission_file_name");

  if (fileInput && fileName) {
    fileInput.addEventListener("change", function (e) {
      if (this.files && this.files[0]) {
        fileName.textContent = this.files[0].name;
      } else {
        fileName.textContent = "";
      }
    });
  }
}

// Mark as Viewed
function initializeMarkAsViewed() {
  const buttonsMarkViewed = document.querySelectorAll(".btn-mark-viewed");

  buttonsMarkViewed.forEach((btnMarkViewed) => {
    const classId = btnMarkViewed.getAttribute("data-class-id");
    const container = document.querySelector(".class-detail-view");
    const courseId = container
      ? container.getAttribute("data-course-id")
      : null;
    const subjectId = container
      ? container.getAttribute("data-subject-id")
      : null;

    btnMarkViewed.addEventListener("click", function () {
      if (classId) {
        markClassAsViewed(classId, courseId, subjectId, this);
      } else {
        console.error("Missing classId");
      }
    });
  });
}

async function markClassAsViewed(classId, courseId, subjectId, button) {
  try {
    // Deshabilitar botón mientras procesa
    if (button) {
      button.disabled = true;
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    }

    // Si faltan IDs (modo prueba/quemado), simular éxito
    if (!courseId || !subjectId) {
      if (button) {
        button.innerHTML = '<i class="fas fa-check"></i> VISTA';
        button.classList.add("viewed");
      }
      return;
    }

    const response = await fetch("/classes/student/mark-viewed", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        class_id: parseInt(classId),
        course_id: parseInt(courseId),
        subject_id: parseInt(subjectId),
        viewed: true,
      }),
    });

    // Si retorna 401/403, quizás necesita token en header
    if (response.status === 401 || response.status === 422) {
      const token = localStorage.getItem("access_token");
      if (token) {
        // Reintentar con token si existe
        const retryResponse = await fetch("/classes/student/mark-viewed", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            class_id: parseInt(classId),
            course_id: parseInt(courseId),
            subject_id: parseInt(subjectId),
            viewed: true,
          }),
        });
        const retryData = await retryResponse.json();
        if (retryData.success) {
          if (button) {
            button.innerHTML = '<i class="fas fa-check"></i> VISTA';
            button.classList.add("viewed");
          }
          return;
        }
      }
    }

    const data = await response.json();

    if (data.success) {
      if (button) {
        button.innerHTML = '<i class="fas fa-check"></i> VISTA';
        button.classList.add("viewed");
      }
    } else {
      if (button) {
        button.disabled = false;
        button.innerHTML = "MARCAR COMO VISTA";
      }
    }
  } catch (error) {
    console.error("Error:", error);
    if (button) {
      button.disabled = false;
      button.innerHTML = "MARCAR COMO VISTA";
    }
  }
}

// Initialize Submit Form with Spinner
function initializeSubmitForm() {
  const form = document.getElementById("submitAssignmentForm");
  const btnSubmit = form ? form.querySelector(".btn-submit") : null;

  if (form && btnSubmit) {
    form.addEventListener("submit", function (e) {
      const assignmentId = document.getElementById("assignment_id").value;

      // Si es un ID dummy (0 o vacío), prevenir envío real y simular
      if (!assignmentId || assignmentId === "0" || assignmentId === "null") {
        e.preventDefault();

        // Simular proceso de carga
        btnSubmit.classList.add("loading");
        btnSubmit.disabled = true;
        const originalText = btnSubmit.innerHTML;
        btnSubmit.innerHTML = '<div class="spinner"></div> Enviando...';

        setTimeout(() => {
          closeSubmitModal();
          btnSubmit.classList.remove("loading");
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = originalText;
        }, 1500);
        return;
      }

      // Si es real, mostrar spinner pero dejar que el form haga submit (o usar fetch)
      // Como el form tiene action="/...", hará reload. Para mostrar spinner antes:
      btnSubmit.classList.add("loading");
      btnSubmit.disabled = true;
      // Nota: si deshabilitas el botón submit, el form podría no enviarse dependiendo del navegador
      // Mejor cambiar solo estilo y texto, y prevenir doble click con flag
      if (form.dataset.submitting === "true") {
        e.preventDefault();
        return;
      }
      form.dataset.submitting = "true";

      // Insertar spinner
      const icon = btnSubmit.querySelector("i");
      if (icon) icon.style.display = "none";

      const spinner = document.createElement("div");
      spinner.className = "spinner";
      spinner.style.display = "inline-block";
      btnSubmit.insertBefore(spinner, btnSubmit.firstChild);
    });
  }
}

// Scroll Indicator Logic
function initializeScrollIndicator() {
  const mainContent = document.querySelector(".main-content");
  const progressBar = document.querySelector(".scroll-progress");

  if (mainContent && progressBar) {
    mainContent.addEventListener("scroll", function () {
      const scrollTop = mainContent.scrollTop;
      const scrollHeight = mainContent.scrollHeight - mainContent.clientHeight;
      const scrollPercent = (scrollTop / scrollHeight) * 100;

      // Ajustar la posición top de la barra (que tiene altura fija 30%)
      // El rango de movimiento es 0% a 70% (100% - 30%)
      const maxTop = 70;
      const currentTop = (scrollPercent / 100) * maxTop;

      progressBar.style.top = `${currentTop}%`;
    });
  }
}

// Modal Functions
function openSubmitModal(assignmentId, assignmentTitle) {
  const modal = document.getElementById("submitAssignmentModal");
  const assignmentIdInput = document.getElementById("assignment_id");
  const assignmentTitleLabel = document.getElementById(
    "assignment_title_label"
  );

  if (modal) {
    if (assignmentIdInput) assignmentIdInput.value = assignmentId || 0;
    if (assignmentTitleLabel)
      assignmentTitleLabel.textContent = assignmentTitle || "Entrega de Tarea";

    modal.style.display = "flex";

    // Reset form
    const form = document.getElementById("submitAssignmentForm");
    if (form) {
      form.reset();
      delete form.dataset.submitting;
      const btn = form.querySelector(".btn-submit");
      if (btn) {
        btn.disabled = false;
        btn.classList.remove("loading");
        // Restaurar icono si se ocultó
        const icon = btn.querySelector("i");
        if (icon) icon.style.display = "inline-block";
        // Quitar spinner si quedó
        const spinner = btn.querySelector(".spinner");
        if (spinner) spinner.remove();
      }
    }
    const fileName = document.getElementById("submission_file_name");
    if (fileName) fileName.textContent = "";
  }
}

function closeSubmitModal() {
  const modal = document.getElementById("submitAssignmentModal");
  if (modal) {
    modal.style.display = "none";
  }
}

// Close modal on outside click
window.addEventListener("click", function (event) {
  const modal = document.getElementById("submitAssignmentModal");
  if (event.target === modal) {
    closeSubmitModal();
  }
});

// Notification Function
// Notificaciones deshabilitadas por requerimiento: no mostrar mensajes al usuario.
function showNotification() {
  return;
}

// Export functions for global access
window.openSubmitModal = openSubmitModal;
window.closeSubmitModal = closeSubmitModal;
