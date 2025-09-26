// Teachers Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializePasswordToggle();
    initializeFormValidation();
    initializeDeleteModal();
    initializeAutoCloseAlerts();
    initializeLoadingStates();
});

// Password Toggle Functionality
function initializePasswordToggle() {
    const toggleButtons = document.querySelectorAll('#togglePassword');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = document.getElementById('password');
            const toggleIcon = document.getElementById('toggleIcon');
            
            if (passwordField && toggleIcon) {
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    toggleIcon.classList.remove('fa-eye');
                    toggleIcon.classList.add('fa-eye-slash');
                } else {
                    passwordField.type = 'password';
                    toggleIcon.classList.remove('fa-eye-slash');
                    toggleIcon.classList.add('fa-eye');
                }
            }
        });
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Show loading state
                const submitBtn = form.querySelector('#submitBtn');
                if (submitBtn) {
                    showLoadingState(submitBtn);
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateField(this);
            });
            
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

// Field Validation
function validateField(field) {
    if (field.checkValidity()) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
}

// Delete Modal Functionality
function initializeDeleteModal() {
    const deleteModal = document.getElementById('deleteModal');
    const deleteForm = document.getElementById('deleteForm');
    
    if (deleteModal && deleteForm) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const teacherId = button.getAttribute('data-teacher-id');
            const teacherName = button.getAttribute('data-teacher-name');
            
            // Update modal content
            const modalTitle = deleteModal.querySelector('#deleteModalLabel');
            if (modalTitle) {
                modalTitle.textContent = `¿Está seguro que desea eliminar a ${teacherName}?`;
            }
            
            // Update form action
            deleteForm.action = `/users/teachers/${teacherId}/delete`;
        });
    }
}

// Auto Close Alerts
function initializeAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Loading States
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('#submitBtn');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
        });
    });
}

// Show Loading State
function showLoadingState(button) {
    button.classList.add('loading');
    button.disabled = true;
    
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
    
    // Store original text for potential restoration
    button.setAttribute('data-original-text', originalText);
}

// Hide Loading State
function hideLoadingState(button) {
    button.classList.remove('loading');
    button.disabled = false;
    
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
    }
}

// Confirmation Dialog Enhancement
function showConfirmationDialog(title, message, confirmText, cancelText, onConfirm) {
    // Create modal dynamically
    const modalHtml = `
        <div class="modal fade" id="confirmationModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center p-4">
                        <div class="delete-icon mb-3">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <h5 class="modal-title mb-3">${title}</h5>
                        <p class="text-muted mb-4">${message}</p>
                        <div class="d-flex gap-3 justify-content-center">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                ${cancelText}
                            </button>
                            <button type="button" class="btn btn-danger" id="confirmAction">
                                ${confirmText}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('confirmationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('confirmationModal'));
    modal.show();
    
    // Handle confirm action
    document.getElementById('confirmAction').addEventListener('click', function() {
        modal.hide();
        if (onConfirm) {
            onConfirm();
        }
    });
    
    // Clean up modal when hidden
    document.getElementById('confirmationModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Enhanced Delete Confirmation
function confirmDelete(teacherId, teacherName) {
    showConfirmationDialog(
        'Eliminar Docente',
        `¿Está seguro que desea eliminar a ${teacherName}? Esta operación es irreversible.`,
        'Eliminar',
        'Cancelar',
        function() {
            // Submit delete form
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/users/teachers/${teacherId}/delete`;
            document.body.appendChild(form);
            form.submit();
        }
    );
}

// Form Enhancement
function enhanceForm(form) {
    // Add real-time validation
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
    
    // Add submit enhancement
    form.addEventListener('submit', function(event) {
        const submitBtn = form.querySelector('#submitBtn');
        if (submitBtn && form.checkValidity()) {
            showLoadingState(submitBtn);
        }
    });
}

// Initialize all forms
function initializeAllForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        enhanceForm(form);
    });
}

// Utility Functions
function showToast(message, type = 'info') {
    // Create toast element
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Add to toast container
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Show toast
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Export functions for global use
window.teachersManagement = {
    showConfirmationDialog,
    confirmDelete,
    showToast,
    showLoadingState,
    hideLoadingState
};
