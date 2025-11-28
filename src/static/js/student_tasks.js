// Student Tasks JavaScript - Simple UI/UX handling

document.addEventListener("DOMContentLoaded", function () {
  // Inicializar listeners del modal
  initializeDeleteModalListeners();

  // Inicializar expand/collapse de materias
  initializeAccordion();

  // Inicializar botones de eliminar asignaciones
  initializeDeleteAssignmentButtons();

  // Auto cerrar alertas
  initializeAutoCloseAlerts();
});

/**
 * Expandir/Contraer filas de clases por materia
 */
function initializeAccordion() {
  const subjectRows = document.querySelectorAll(".subject-row");

  subjectRows.forEach((row) => {
    row.addEventListener("click", function (e) {
      // No expandir si se hace clic en un botón o enlace dentro
      if (
        e.target.closest(".download-link") ||
        e.target.closest(".delete-assignment")
      ) {
        return;
      }

      const subjectId = this.getAttribute("data-subject-id");
      // Obtener todas las filas de clases de esta materia
      const contentRows = document.querySelectorAll(
        `.subject-content-row[data-subject-id="${subjectId}"]`
      );

      if (contentRows.length > 0) {
        const isExpanded = this.classList.contains("expanded");

        if (isExpanded) {
          // Colapsar - ocultar todas las filas de clases
          contentRows.forEach((contentRow) => {
            contentRow.style.display = "none";
          });
          this.classList.remove("expanded");
        } else {
          // Expandir - mostrar todas las filas de clases
          contentRows.forEach((contentRow) => {
            contentRow.style.display = "table-row";
          });
          this.classList.add("expanded");
        }
      }
    });
  });
}

/**
 * Inicializar botones de eliminar asignaciones
 */
function initializeDeleteAssignmentButtons() {
  initializeDeleteButtons(".delete-assignment", function (button) {
    const assignmentId = button.getAttribute("data-assignment-id");

    // Obtener course_id y student_id de la URL actual
    const urlParts = window.location.pathname.split("/");
    const courseIdIndex = urlParts.indexOf("courses");
    const courseId =
      courseIdIndex !== -1 && urlParts[courseIdIndex + 1]
        ? urlParts[courseIdIndex + 1]
        : null;
    const studentIdIndex = urlParts.indexOf("students");
    const studentId =
      studentIdIndex !== -1 && urlParts[studentIdIndex + 1]
        ? urlParts[studentIdIndex + 1]
        : null;

    if (!courseId || !studentId) {
      console.error("No se pudo obtener los IDs del curso o estudiante");
      return null;
    }

    return `/courses/api/${courseId}/students/${studentId}/assignments/${assignmentId}/delete`;
  });
}

/**
 * Auto cerrar alertas después de 5 segundos
 */
function initializeAutoCloseAlerts() {
  const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");

  alerts.forEach((alert) => {
    setTimeout(() => {
      if (typeof bootstrap !== "undefined" && bootstrap.Alert) {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } else {
        const closeBtn = alert.querySelector(".btn-close");
        if (closeBtn) {
          closeBtn.click();
        } else {
          alert.style.display = "none";
        }
      }
    }, 5000);
  });
}
