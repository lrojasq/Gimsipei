// Create Student JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeAutoCloseAlerts();
    initializeLoadingStates();
    initializePasswordToggle();
});

// Form Validation
function initializeFormValidation() {
    const form = document.querySelector('.form-admin');
    
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            // Show loading state
            const submitBtn = form.querySelector('.btn-admin');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
        }
        form.classList.add('was-validated');
    });
    
    // Real-time validation
    const inputs = form.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
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

// Password Toggle Functionality
function initializePasswordToggle() {
    const passwordField = document.getElementById('password');
    const toggleButton = document.getElementById('togglePassword');
    
    if (passwordField && toggleButton) {
        toggleButton.addEventListener('click', function() {
            const toggleIcon = document.getElementById('toggleIcon');
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                if (toggleIcon) {
                    toggleIcon.classList.remove('fa-eye');
                    toggleIcon.classList.add('fa-eye-slash');
                }
            } else {
                passwordField.type = 'password';
                if (toggleIcon) {
                    toggleIcon.classList.remove('fa-eye-slash');
                    toggleIcon.classList.add('fa-eye');
                }
            }
        });
    }
}

// Auto Close Alerts
function initializeAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        }, 5000);
    });
}

// Loading States
function initializeLoadingStates() {
    const form = document.querySelector('.form-admin');
    
    if (form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('.btn-admin');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
            }
        });
    }
}

function showLoadingState(button) {
    if (button) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
    }
}

function hideLoadingState(button) {
    if (button && button.dataset.originalText) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
        delete button.dataset.originalText;
    }
}

// Document validation
function validateDocument(documentValue) {
    // Validar que el documento solo contenga números y tenga al menos 5 dígitos
    const documentRegex = /^\d{5,}$/;
    return documentRegex.test(documentValue);
}

// Username validation
function validateUsername(username) {
    // Validar que el username tenga al menos 3 caracteres y solo letras, números y guiones bajos
    const usernameRegex = /^[a-zA-Z0-9_]{3,}$/;
    return usernameRegex.test(username);
}

// Add custom validation to document field
document.addEventListener('DOMContentLoaded', function() {
    const documentField = document.getElementById('document');
    if (documentField) {
        documentField.addEventListener('blur', function() {
            if (this.value && !validateDocument(this.value)) {
                this.setCustomValidity('El documento debe contener solo números y tener al menos 5 dígitos');
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                if (this.value) {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                }
            }
        });
    }
    
    // Add custom validation to username field
    const usernameField = document.getElementById('username');
    if (usernameField) {
        usernameField.addEventListener('blur', function() {
            if (this.value && !validateUsername(this.value)) {
                this.setCustomValidity('El usuario debe tener al menos 3 caracteres y solo puede contener letras, números y guiones bajos');
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                if (this.value) {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                }
            }
        });
    }
});

