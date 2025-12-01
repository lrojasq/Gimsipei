/**
 * Student Evaluations Teacher View - JavaScript
 * Handles subject row expansion and evaluation actions
 */

// Variables globales para modal de editar nota
let currentEditSubmissionId = null;
let currentEditScoreElement = null;

document.addEventListener("DOMContentLoaded", function () {
  initializeSubjectExpansion();
  initializeResetModal();
  initializeDeleteSubmission();
  initializeEditScoreModal();
});

/**
 * Initialize subject row expansion/collapse
 */
function initializeSubjectExpansion() {
  const subjectRows = document.querySelectorAll(".subject-row");

  subjectRows.forEach((row) => {
    row.addEventListener("click", function () {
      const subjectId = this.dataset.subjectId;
      const contentRows = document.querySelectorAll(
        `.subject-content-row[data-subject-id="${subjectId}"]`
      );
      const isExpanded = this.classList.contains("expanded");

      if (isExpanded) {
        // Collapse
        this.classList.remove("expanded");
        contentRows.forEach((contentRow) => {
          contentRow.style.display = "none";
        });
      } else {
        // Expand
        this.classList.add("expanded");
        contentRows.forEach((contentRow) => {
          contentRow.style.display = "table-row";
        });
      }
    });
  });
}

/**
 * Initialize reset evaluation modal
 */
function initializeResetModal() {
  const modal = document.getElementById("resetEvaluationModal");
  const closeBtn = document.getElementById("closeResetModal");
  const cancelBtn = document.getElementById("cancelResetBtn");
  const form = document.getElementById("resetEvaluationForm");
  const confirmBtn = document.getElementById("confirmResetBtn");

  if (!modal) return;

  // Reset buttons
  document.querySelectorAll(".reset-evaluation").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();

      const submissionId = this.dataset.submissionId;
      const evalTitle = this.dataset.evaluationTitle;
      const studentName = this.dataset.studentName;

      document.getElementById("resetEvalTitle").textContent = evalTitle;
      document.getElementById("resetStudentName").textContent = studentName;

      // Set form action
      form.action = `/evaluations/submission/${submissionId}/reset`;

      modal.style.display = "flex";
    });
  });

  // Close modal
  function closeModal() {
    modal.style.display = "none";
    // Reset button state
    const btnText = confirmBtn.querySelector(".btn-text");
    const btnSpinner = confirmBtn.querySelector(".btn-spinner");
    if (btnText) btnText.style.display = "inline-flex";
    if (btnSpinner) btnSpinner.style.display = "none";
    confirmBtn.disabled = false;
  }

  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal.style.display === "flex") {
      closeModal();
    }
  });

  // Form submission with spinner
  form.addEventListener("submit", function () {
    const btnText = confirmBtn.querySelector(".btn-text");
    const btnSpinner = confirmBtn.querySelector(".btn-spinner");

    if (btnText) btnText.style.display = "none";
    if (btnSpinner) btnSpinner.style.display = "inline-flex";
    confirmBtn.disabled = true;
  });
}

/**
 * Initialize delete submission functionality
 */
function initializeDeleteSubmission() {
  document.querySelectorAll(".delete-evaluation-submission").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();

      const submissionId = this.dataset.submissionId;
      const evalTitle = this.dataset.evaluationTitle;
      const deleteUrl = `/evaluations/submission/${submissionId}/delete`;

      // Actualizar el mensaje del modal
      const modalTitle = document.querySelector(
        "#deleteConfirmationModal .delete-title"
      );
      if (modalTitle) {
        modalTitle.textContent = `¿Está seguro que desea eliminar el envío de "${evalTitle}"?`;
      }

      // Usar la función del modal de eliminación
      if (typeof showDeleteConfirmationModal === "function") {
        showDeleteConfirmationModal(deleteUrl);
      } else {
        // Fallback: simple confirm
        if (
          confirm(
            `¿Está seguro que desea eliminar el envío de la evaluación "${evalTitle}"?`
          )
        ) {
          const form = document.createElement("form");
          form.method = "POST";
          form.action = deleteUrl;
          document.body.appendChild(form);
          form.submit();
        }
      }
    });
  });
}

/**
 * Initialize edit score modal
 */
function initializeEditScoreModal() {
  const modal = document.getElementById("editScoreModal");
  if (!modal) return;

  const scoreInput = document.getElementById("editScoreInput");

  // Enter key to save
  if (scoreInput) {
    scoreInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        saveEditScore();
      }
    });
  }

  // Close on backdrop click
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeEditScoreModal();
    }
  });

  // Close on escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal.style.display === "flex") {
      closeEditScoreModal();
    }
  });
}

/**
 * Open edit score modal
 */
function openEditScoreModal(element) {
  const modal = document.getElementById("editScoreModal");
  if (!modal) {
    console.error("Modal editScoreModal no encontrado");
    return;
  }

  currentEditSubmissionId = element.dataset.submissionId;
  currentEditScoreElement = element;

  const evalTitle = element.dataset.evaluationTitle;
  const studentName = element.dataset.studentName;
  const currentScore = element.dataset.currentScore;

  document.getElementById("editScoreEvalTitle").textContent = evalTitle;
  document.getElementById("editScoreStudentName").textContent = studentName;

  const scoreInput = document.getElementById("editScoreInput");
  scoreInput.value = currentScore;

  // Mostrar modal
  modal.style.display = "flex";

  // Focus input
  setTimeout(() => {
    scoreInput.focus();
    scoreInput.select();
  }, 100);
}

/**
 * Close edit score modal
 */
function closeEditScoreModal() {
  const modal = document.getElementById("editScoreModal");
  if (modal) {
    modal.style.display = "none";
  }

  // Reset button state
  const saveBtn = document.getElementById("saveEditScoreBtn");
  if (saveBtn) {
    const btnText = saveBtn.querySelector(".btn-text");
    const btnSpinner = saveBtn.querySelector(".btn-spinner");
    if (btnText) btnText.style.display = "inline-flex";
    if (btnSpinner) btnSpinner.style.display = "none";
    saveBtn.disabled = false;
  }

  currentEditSubmissionId = null;
  currentEditScoreElement = null;
}

/**
 * Save edited score
 */
async function saveEditScore() {
  const scoreInput = document.getElementById("editScoreInput");
  const saveBtn = document.getElementById("saveEditScoreBtn");

  if (!scoreInput || !saveBtn || !currentEditSubmissionId) return;

  const newScore = parseFloat(scoreInput.value);

  // Validate
  if (isNaN(newScore) || newScore < 0 || newScore > 5) {
    alert("Por favor ingrese una nota válida entre 0.0 y 5.0");
    scoreInput.focus();
    return;
  }

  // Show loading
  const btnText = saveBtn.querySelector(".btn-text");
  const btnSpinner = saveBtn.querySelector(".btn-spinner");
  if (btnText) btnText.style.display = "none";
  if (btnSpinner) btnSpinner.style.display = "inline-flex";
  saveBtn.disabled = true;

  try {
    const response = await fetch(
      `/evaluations/submission/${currentEditSubmissionId}/update-score`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ score: newScore }),
      }
    );

    const data = await response.json();

    if (response.ok && data.success) {
      // Update displayed score
      if (currentEditScoreElement) {
        // Update the text (first child text node)
        const scoreText = currentEditScoreElement.childNodes[0];
        if (scoreText.nodeType === Node.TEXT_NODE) {
          scoreText.textContent = newScore.toFixed(1) + " ";
        } else {
          // Fallback: replace the whole content
          const editIcon =
            currentEditScoreElement.querySelector(".score-edit-icon");
          currentEditScoreElement.innerHTML = "";
          currentEditScoreElement.appendChild(
            document.createTextNode(newScore.toFixed(1) + " ")
          );
          if (editIcon) currentEditScoreElement.appendChild(editIcon);
          else {
            const icon = document.createElement("i");
            icon.className = "fas fa-edit score-edit-icon";
            currentEditScoreElement.appendChild(icon);
          }
        }
        // Update data attribute
        currentEditScoreElement.dataset.currentScore = newScore;
      }

      closeEditScoreModal();
      showToast("Nota actualizada correctamente", "success");
    } else {
      alert(data.error || "Error al actualizar la nota");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error de conexión al actualizar la nota");
  } finally {
    if (btnText) btnText.style.display = "inline-flex";
    if (btnSpinner) btnSpinner.style.display = "none";
    saveBtn.disabled = false;
  }
}

/**
 * Simple toast notification
 */
function showToast(message, type = "info") {
  // Remove existing
  const existing = document.querySelector(".toast-notification");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = `toast-notification toast-${type}`;
  toast.innerHTML = `
    <i class="fas fa-${
      type === "success" ? "check-circle" : "info-circle"
    }"></i>
    <span>${message}</span>
  `;

  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: ${type === "success" ? "#28a745" : "#17a2b8"};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    z-index: 1100;
    animation: slideInRight 0.3s ease;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideOutRight 0.3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Add animation styles
const toastStyle = document.createElement("style");
toastStyle.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(toastStyle);
