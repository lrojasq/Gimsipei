// Class Detail - Teacher View JavaScript

document.addEventListener("DOMContentLoaded", function () {
  initializeFileUploads();
  initializeForms();
});

// File Upload Previews
function initializeFileUploads() {
  // Content Image
  const contentImageInput = document.getElementById("content_image");
  const contentImageName = document.getElementById("content_image_name");

  if (contentImageInput && contentImageName) {
    contentImageInput.addEventListener("change", function (e) {
      if (this.files && this.files[0]) {
        contentImageName.textContent = this.files[0].name;
      } else {
        contentImageName.textContent = "";
      }
    });
  }
}

// Initialize Forms
function initializeForms() {
  const contentForm = document.getElementById("contentForm");
  const assignmentForm = document.getElementById("assignmentForm");

  if (contentForm) {
    contentForm.addEventListener("submit", function (e) {
      const contentId = document.getElementById("content_id").value;
      const submitBtn = document.getElementById("contentSubmitBtn");

      this.action = contentId
        ? `/classes/content/update/${contentId}`
        : "/classes/content/create";

      // Show spinner and disable button
      if (submitBtn) {
        const originalContent = submitBtn.innerHTML;
        submitBtn.innerHTML =
          '<i class="fas fa-spinner fa-spin"></i> GUARDANDO...';
        submitBtn.disabled = true;

        // Re-enable if form submission fails (backup)
        setTimeout(() => {
          if (submitBtn.disabled) {
            submitBtn.innerHTML = originalContent;
            submitBtn.disabled = false;
          }
        }, 10000);
      }
    });
  }

  if (assignmentForm) {
    assignmentForm.addEventListener("submit", function (e) {
      const submitBtn = document.getElementById("assignmentSubmitBtn");
      const assignmentId = document.getElementById("assignment_id").value;

      // Update form action based on whether we're creating or updating
      this.action = assignmentId
        ? `/classes/assignment/update/${assignmentId}`
        : "/classes/assignment/create";

      // Show spinner and disable button
      if (submitBtn) {
        const originalContent = submitBtn.innerHTML;
        const buttonText = assignmentId ? "ACTUALIZANDO..." : "CREANDO...";
        submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${buttonText}`;
        submitBtn.disabled = true;

        // Re-enable if form submission fails (backup)
        setTimeout(() => {
          if (submitBtn.disabled) {
            submitBtn.innerHTML = originalContent;
            submitBtn.disabled = false;
          }
        }, 10000);
      }
    });
  }
}

// Content Modal Functions
function openAddContentModal() {
  const modal = document.getElementById("contentModal");
  const modalTitle = document.getElementById("contentModalTitle");
  const form = document.getElementById("contentForm");
  const currentImagePreview = document.getElementById("current_image_preview");

  if (modal && modalTitle && form) {
    modalTitle.textContent = "AGREGAR CONTENIDO";
    form.reset();
    document.getElementById("content_id").value = "";
    document.getElementById("content_image_name").textContent = "";

    // Hide image preview when adding new content
    if (currentImagePreview) {
      currentImagePreview.style.display = "none";
    }

    modal.style.display = "flex";
  }
}

function editContent(contentId) {
  // Get content data from the page
  const contentCard = document.querySelector(
    `[data-content-id="${contentId}"]`
  );

  if (contentCard) {
    const modal = document.getElementById("contentModal");
    const modalTitle = document.getElementById("contentModalTitle");
    const form = document.getElementById("contentForm");

    if (modal && modalTitle && form) {
      modalTitle.textContent = "EDITAR CONTENIDO";

      // Fill form with existing data
      const titleElement = contentCard.querySelector(".content-item-header h4");
      const textElement = contentCard.querySelector(".content-item-text");
      const imageElement = contentCard.querySelector(".content-item-image img");

      // Set section title
      if (titleElement) {
        const titleText = titleElement.textContent.trim();
        // Check if it's not the default "Contenido X" text
        if (!titleText.startsWith("Contenido ")) {
          document.getElementById("section_title").value = titleText;
        } else {
          document.getElementById("section_title").value = "";
        }
      }

      // Set content text
      if (textElement) {
        document.getElementById("content_text").value =
          textElement.textContent.trim();
      }

      // Show current image if exists
      const currentImagePreview = document.getElementById(
        "current_image_preview"
      );
      const currentImageDisplay = document.getElementById(
        "current_image_display"
      );

      if (imageElement && currentImagePreview && currentImageDisplay) {
        currentImageDisplay.src = imageElement.src;
        currentImagePreview.style.display = "block";
      } else if (currentImagePreview) {
        currentImagePreview.style.display = "none";
      }

      document.getElementById("content_id").value = contentId;
      modal.style.display = "flex";
    }
  }
}

function closeContentModal() {
  const modal = document.getElementById("contentModal");
  const currentImagePreview = document.getElementById("current_image_preview");
  const form = document.getElementById("contentForm");

  if (modal) {
    modal.style.display = "none";
  }

  // Reset form and hide image preview
  if (form) {
    form.reset();
  }

  if (currentImagePreview) {
    currentImagePreview.style.display = "none";
  }
}

function deleteContent(contentId) {
  // Open delete confirmation modal
  const modal = document.getElementById("deleteConfirmationModal");
  const form = document.getElementById("deleteConfirmationForm");

  if (modal && form) {
    // Set the form action to delete this specific content
    form.action = `/classes/content/delete/${contentId}`;

    // Show the modal
    modal.setAttribute("aria-hidden", "false");
    modal.style.display = "flex";
  }
}

// Close delete modal
function closeDeleteModal() {
  const modal = document.getElementById("deleteConfirmationModal");
  if (modal) {
    modal.setAttribute("aria-hidden", "true");
    modal.style.display = "none";
  }
}

// Assignment Modal Functions
function openAddAssignmentModal() {
  const modal = document.getElementById("assignmentModal");
  const form = document.getElementById("assignmentForm");

  if (modal && form) {
    form.reset();

    // Clear assignment_id for new assignment
    document.getElementById("assignment_id").value = "";

    // Reset form action to create
    form.action = "/classes/assignment/create";

    // Reset modal title
    const modalTitle = modal.querySelector(".modal-header h3");
    if (modalTitle) {
      modalTitle.textContent = "CREAR TAREA";
    }

    modal.style.display = "flex";
  }
}

function closeAssignmentModal() {
  const modal = document.getElementById("assignmentModal");
  if (modal) {
    modal.style.display = "none";
  }
}

function editAssignment(assignmentId) {
  // Get assignment data from the page
  const assignmentCard = document.querySelector(
    `[data-assignment-id="${assignmentId}"]`
  );

  if (assignmentCard) {
    const modal = document.getElementById("assignmentModal");
    const form = document.getElementById("assignmentForm");

    if (modal && form) {
      // Set assignment_id for update
      document.getElementById("assignment_id").value = assignmentId;

      // Get assignment data
      const titleElement = assignmentCard.querySelector(".task-item-header h4");
      const descriptionElement = assignmentCard.querySelector(
        ".task-item-description"
      );
      const metaElements = assignmentCard.querySelectorAll(
        ".task-item-meta span"
      );

      // Fill form with existing data
      if (titleElement) {
        document.getElementById("assignment_title").value =
          titleElement.textContent.trim();
      }

      if (descriptionElement) {
        document.getElementById("assignment_description").value =
          descriptionElement.textContent.trim();
      } else {
        document.getElementById("assignment_description").value = "";
      }

      // Extract due date and max score from meta elements
      metaElements.forEach((span) => {
        const text = span.textContent;
        if (text.includes("Fecha límite:")) {
          const dateStr = text.split("Fecha límite:")[1].trim();
          // Convert to datetime-local format (YYYY-MM-DDTHH:MM)
          document.getElementById("due_date").value = dateStr + "T00:00";
        }
        if (text.includes("Puntaje máximo:")) {
          const score = text.split("Puntaje máximo:")[1].trim();
          document.getElementById("max_score").value = score;
        }
      });

      // Change form action to update
      form.action = `/classes/assignment/update/${assignmentId}`;

      // Change modal title
      const modalTitle = modal.querySelector(".modal-header h3");
      if (modalTitle) {
        modalTitle.textContent = "EDITAR TAREA";
      }

      modal.style.display = "flex";
    }
  }
}

function deleteAssignment(assignmentId) {
  // Open delete confirmation modal
  const modal = document.getElementById("deleteConfirmationModal");
  const form = document.getElementById("deleteConfirmationForm");

  if (modal && form) {
    // Set the form action to delete this specific assignment
    form.action = `/classes/assignment/delete/${assignmentId}`;

    // Show the modal
    modal.setAttribute("aria-hidden", "false");
    modal.style.display = "flex";
  }
}

// Close modals on outside click
window.addEventListener("click", function (event) {
  const contentModal = document.getElementById("contentModal");
  const assignmentModal = document.getElementById("assignmentModal");
  const deleteModal = document.getElementById("deleteConfirmationModal");

  if (event.target === contentModal) {
    closeContentModal();
  }

  if (event.target === assignmentModal) {
    closeAssignmentModal();
  }

  if (
    event.target === deleteModal ||
    event.target.classList.contains("close-modal")
  ) {
    closeDeleteModal();
  }
});

// Handle close modal buttons
document.addEventListener("DOMContentLoaded", function () {
  const closeButtons = document.querySelectorAll(".close-modal");
  closeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      closeDeleteModal();
    });
  });
});

// Notification Function
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${
              type === "success"
                ? "check-circle"
                : type === "error"
                ? "exclamation-circle"
                : "info-circle"
            }"></i>
            <span>${message}</span>
        </div>
    `;

  // Add styles if not already present
  if (!document.getElementById("notification-styles")) {
    const style = document.createElement("style");
    style.id = "notification-styles";
    style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 10000;
                animation: slideIn 0.3s ease;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .notification-success {
                background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            }
            .notification-error {
                background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
            }
            .notification-info {
                background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(100px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
        `;
    document.head.appendChild(style);
  }

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideIn 0.3s ease reverse";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Export functions for global access
window.openAddContentModal = openAddContentModal;
window.editContent = editContent;
window.closeContentModal = closeContentModal;
window.deleteContent = deleteContent;
window.closeDeleteModal = closeDeleteModal;
window.openAddAssignmentModal = openAddAssignmentModal;
window.closeAssignmentModal = closeAssignmentModal;
window.editAssignment = editAssignment;
window.deleteAssignment = deleteAssignment;
