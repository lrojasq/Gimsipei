// Courses Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeAutoCloseAlerts();
    initializeLoadingStates();
    initializeAccordion();
    initializeDeleteSubjectModal();
});

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
        const inputs = form.querySelectorAll('input[required], select[required]');
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

// (Removed) Delete modal setup: server actions are handled via HTML forms

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

// Accordion Functionality
function initializeAccordion() {
    const table = document.getElementById('accordionSubjects');
    if (!table) return;

    table.querySelectorAll('.toggle-arrow').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const row = this.closest('tr');
            const courseId = row.getAttribute('data-course-id');
            const list = document.getElementById(`subjects-${courseId}`);
            const arrow = this.querySelector('.arrow');

            // toggle arrow
            setTimeout(() => {
                const expanded = list.classList.contains('show');
                arrow.style.transform = expanded ? 'rotate(0deg)' : 'rotate(180deg)';
            }, 250);
        });
    });
}

// (Removed) Client-side rendering of subjects

// Tabs Functionality
function initializeTabs() {
    const tabTriggers = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    tabTriggers.forEach(trigger => {
        trigger.addEventListener('shown.bs.tab', function(event) {
            const target = event.target.getAttribute('data-bs-target');
            const tabPane = document.querySelector(target);
            
            if (tabPane) {
                // Add animation to tab content
                tabPane.style.opacity = '0';
                tabPane.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    tabPane.style.transition = 'all 0.3s ease';
                    tabPane.style.opacity = '1';
                    tabPane.style.transform = 'translateY(0)';
                }, 50);
            }
        });
    });
}

// Toast Notifications
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

// Keep only UI helpers available if needed globally
// Delete Subject Modal Functionality
function initializeDeleteSubjectModal() {
    const deleteModal = document.getElementById('deleteSubjectModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const subjectNameElement = document.getElementById('subjectName');
    const teacherNameElement = document.getElementById('teacherName');
    
    if (!deleteModal || !confirmDeleteBtn || !subjectNameElement || !teacherNameElement) {
        return; // Exit if elements don't exist
    }
    
    let currentSubjectId = null;
    let currentCourseId = null;
    
    // Handle click on delete buttons
    document.querySelectorAll('[data-bs-target="#deleteSubjectModal"]').forEach(button => {
        button.addEventListener('click', function() {
            currentSubjectId = this.getAttribute('data-subject-id');
            currentCourseId = this.getAttribute('data-course-id');
            const subjectName = this.getAttribute('data-subject-name');
            const teacherName = this.getAttribute('data-teacher-name');
            
            // Update information in the modal
            subjectNameElement.textContent = subjectName;
            teacherNameElement.textContent = teacherName;
        });
    });
    
    // Handle confirmation of deletion
    confirmDeleteBtn.addEventListener('click', function() {
        if (currentSubjectId && currentCourseId) {
            // Create temporary form to submit the deletion
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/subjects/${currentSubjectId}/delete?course_id=${currentCourseId}`;
            
            // Add CSRF token if exists
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken.getAttribute('content');
                form.appendChild(csrfInput);
            }
            
            document.body.appendChild(form);
            form.submit();
        }
    });
    
    // Clear data when modal is closed
    deleteModal.addEventListener('hidden.bs.modal', function() {
        currentSubjectId = null;
        currentCourseId = null;
        subjectNameElement.textContent = '';
        teacherNameElement.textContent = '';
    });
}

window.coursesManagement = {
    showToast,
    showLoadingState,
    hideLoadingState,
    initializeDeleteSubjectModal
};
