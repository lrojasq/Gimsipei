/**
 * Student Take Evaluation - JavaScript Module
 * Handles evaluation form submission with spinner, validation and confirmation modal
 */

document.addEventListener("DOMContentLoaded", function () {
  initializeEvaluationForm();
  initializeConfirmationModal();
});

/**
 * Initialize the evaluation form
 */
function initializeEvaluationForm() {
  const form = document.getElementById("evaluationForm");
  const submitBtn = document.getElementById("submitEvaluationBtn");

  if (!form || !submitBtn) return;

  // Handle form submission - show confirmation modal first
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Prevent double submission
    if (form.dataset.submitting === "true") {
      return;
    }

    // Validate form before showing modal
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    // Show confirmation modal
    showConfirmationModal();
  });
}

/**
 * Initialize confirmation modal events
 */
function initializeConfirmationModal() {
  const modal = document.getElementById("confirmationModal");
  const cancelBtn = document.getElementById("cancelModalBtn");
  const confirmBtn = document.getElementById("confirmModalBtn");

  if (!modal) return;

  // Cancel button - close modal
  if (cancelBtn) {
    cancelBtn.addEventListener("click", function () {
      closeConfirmationModal();
    });
  }

  // Confirm button - submit the form
  if (confirmBtn) {
    confirmBtn.addEventListener("click", function () {
      submitEvaluation();
    });
  }

  // Close modal on overlay click
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeConfirmationModal();
    }
  });

  // Close modal on Escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modal.classList.contains("show")) {
      closeConfirmationModal();
    }
  });
}

/**
 * Show the confirmation modal
 */
function showConfirmationModal() {
  const modal = document.getElementById("confirmationModal");
  if (modal) {
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
  }
}

/**
 * Close the confirmation modal
 */
function closeConfirmationModal() {
  const modal = document.getElementById("confirmationModal");
  if (modal) {
    modal.classList.remove("show");
    document.body.style.overflow = "";
  }
}

/**
 * Submit the evaluation form
 */
function submitEvaluation() {
  const form = document.getElementById("evaluationForm");
  const submitBtn = document.getElementById("submitEvaluationBtn");

  if (!form) return;

  // Close modal
  closeConfirmationModal();

  // Mark as submitting
  form.dataset.submitting = "true";

  // Show spinner
  showSubmitSpinner(submitBtn);

  // Submit the form
  form.submit();
}

/**
 * Show spinner on submit button
 */
function showSubmitSpinner(btn) {
  if (!btn) return;

  const btnText = btn.querySelector(".btn-text");
  const btnSpinner = btn.querySelector(".btn-spinner");

  btn.disabled = true;
  btn.classList.add("loading");

  if (btnText) btnText.style.display = "none";
  if (btnSpinner) btnSpinner.style.display = "inline-flex";
}

/**
 * Reset submit button to original state
 */
function resetSubmitButton(btn) {
  if (!btn) return;

  const btnText = btn.querySelector(".btn-text");
  const btnSpinner = btn.querySelector(".btn-spinner");
  const form = document.getElementById("evaluationForm");

  btn.disabled = false;
  btn.classList.remove("loading");

  if (btnText) btnText.style.display = "inline-flex";
  if (btnSpinner) btnSpinner.style.display = "none";

  if (form) delete form.dataset.submitting;
}

// Export functions for global access if needed
window.showSubmitSpinner = showSubmitSpinner;
window.resetSubmitButton = resetSubmitButton;
window.showConfirmationModal = showConfirmationModal;
window.closeConfirmationModal = closeConfirmationModal;
