// Courses Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    initializeAutoCloseAlerts();
    initializeLoadingStates();
    initializeAccordion();
    // initializeDeleteModalListeners() ya se llama automáticamente en delete_modal.js
    initializeDeleteSubjectModal();
    initializeCreateCourseModal();
    initializeCreateSubjectModal();
    initializeEditSubjectModal();
});

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        // EXCLUIR los formularios de modales - se manejan separadamente
        if (form.id === 'createCourseForm' || form.id === 'createSubjectForm' || form.id === 'editSubjectForm') {
            return; // No agregar validación a estos formularios
        }
        
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                form.classList.add('was-validated');
            } else {
                // Show loading state
                const submitBtn = form.querySelector('#submitBtn');
                if (submitBtn) {
                    showLoadingState(submitBtn);
                }
            }
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
            // Verificar si Bootstrap está disponible
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
            } else {
                // Fallback: simplemente ocultar el alert
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.click();
                } else {
                    alert.style.display = 'none';
                }
            }
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
    // New accordion for the current courses list layout
    const courseItems = document.querySelectorAll('.list-cursos > li');
    if (!courseItems.length) return;

    courseItems.forEach((item, index) => {
        const header = item.querySelector('.grado');
        const content = item.querySelector('.content-materias');
        const icon = header ? header.querySelector('i.fas') : null;

        if (!header || !content) return;

        // Initial state: all collapsed by default
        content.style.display = 'none';
        if (icon) { icon.classList.remove('fa-chevron-up'); icon.classList.add('fa-chevron-down'); }

        header.addEventListener('click', function() {
            const isVisible = content.style.display !== 'none';
            if (isVisible) {
                content.style.display = 'none';
                if (icon) { icon.classList.remove('fa-chevron-up'); icon.classList.add('fa-chevron-down'); }
                        } else {
                content.style.display = 'flex';
                if (icon) { icon.classList.remove('fa-chevron-down'); icon.classList.add('fa-chevron-up'); }
            }
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
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    } else {
        // Fallback: mostrar el toast manualmente
        toastElement.style.display = 'block';
        setTimeout(() => {
            toastElement.style.opacity = '0';
            setTimeout(() => toastElement.remove(), 300);
        }, 3000);
    }
    
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

// Delete Subject Modal 
function initializeDeleteSubjectModal() {
    initializeDeleteButtons('.open-delete-subject-modal', function(button) {
        const courseId = button.getAttribute('data-course-id');
        const subjectId = button.getAttribute('data-subject-id');
        const teacherId = button.getAttribute('data-teacher-id');
        return `/courses/${courseId}/subjects/${subjectId}/${teacherId}/remove`;
    });
}

// Función global para cerrar modales (legacy - mantener para compatibilidad)
const closeModalGlobal =()=>{
    const btns = document.querySelectorAll(".close-modal");
    const modal = document.querySelector(".modal");
    btns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (modal) {
                modal.classList.remove('show');
                modal.setAttribute('aria-hidden', 'true');
            }
        });
    });
}

window.onload = () => closeModalGlobal();

// Initialize Create Course Modal
function initializeCreateCourseModal() {
    setTimeout(function() {
        const modal = document.getElementById('createCourseModal');
        const openModalBtn = document.getElementById('openCreateCourseModal');
        const closeModalBtns = document.querySelectorAll('.close-modal');
        const form = document.getElementById('createCourseForm');
        
        if (!modal || !form) return;
        
        // Abrir modal
        if (openModalBtn) {
            openModalBtn.addEventListener('click', function(e) {
                e.preventDefault();
                modal.classList.add('show');
                modal.style.display = 'flex';
                modal.removeAttribute('aria-hidden'); // Quitar aria-hidden para accesibilidad
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
                
                if (form) {
                    form.reset();
                    form.classList.remove('was-validated');
                    const inputs = form.querySelectorAll('.is-invalid, .is-valid');
                    inputs.forEach(input => {
                        input.classList.remove('is-invalid', 'is-valid');
                    });
                }
                
                const submitBtn = form.querySelector('#submitBtn');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.removeAttribute('disabled');
                }
            });
        }
        
        // Función para cerrar el modal
        function closeModal() {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
            
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
                const inputs = form.querySelectorAll('.is-invalid, .is-valid');
                inputs.forEach(input => {
                    input.classList.remove('is-invalid', 'is-valid');
                });
            }
        }
        
        // Cerrar modal
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });
        
        // Cerrar modal al hacer clic en bg-back
        const bgBack = modal.querySelector('.bg-back');
        if (bgBack) {
            bgBack.addEventListener('click', closeModal);
        }
        
        // Manejar el submit del formulario
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return false;
            }
            
            // Mostrar loading
            const submitBtn = form.querySelector('#submitBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
            }
        }, false);
    }, 100);
}

// Initialize Create Subject Modal
function initializeCreateSubjectModal() {
    setTimeout(function() {
        const modal = document.getElementById('createSubjectModal');
        const openModalBtns = document.querySelectorAll('.open-create-subject-modal');
        const closeModalBtns = modal ? modal.querySelectorAll('.close-modal') : [];
        const form = document.getElementById('createSubjectForm');
        
        if (!modal || !form) return;
        
        // Abrir modal desde los botones "AÑADIR" de materias
        openModalBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const courseId = this.getAttribute('data-course-id');
                
                // Actualizar el course_id en el formulario
                const courseIdInput = form.querySelector('#subjectCourseId');
                if (courseIdInput && courseId) {
                    courseIdInput.value = courseId;
                } else if (courseId) {
                    // Si no existe el input, crearlo
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'course_id';
                    hiddenInput.id = 'subjectCourseId';
                    hiddenInput.value = courseId;
                    form.appendChild(hiddenInput);
                }
                
                modal.classList.add('show');
                modal.style.display = 'flex';
                modal.removeAttribute('aria-hidden');
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
                
                if (form) {
                    form.reset();
                    // Restaurar el course_id después del reset
                    if (courseId) {
                        const courseIdInput = form.querySelector('#subjectCourseId');
                        if (courseIdInput) {
                            courseIdInput.value = courseId;
                        } else {
                            const hiddenInput = document.createElement('input');
                            hiddenInput.type = 'hidden';
                            hiddenInput.name = 'course_id';
                            hiddenInput.id = 'subjectCourseId';
                            hiddenInput.value = courseId;
                            form.appendChild(hiddenInput);
                        }
                    }
                    form.classList.remove('was-validated');
                    const inputs = form.querySelectorAll('.is-invalid, .is-valid');
                    inputs.forEach(input => {
                        input.classList.remove('is-invalid', 'is-valid');
                    });
                }
                
                const submitBtn = form.querySelector('#submitSubjectBtn');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.removeAttribute('disabled');
                }
            });
        });
        
        // Función para cerrar el modal
        function closeModal() {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
            
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
                const inputs = form.querySelectorAll('.is-invalid, .is-valid');
                inputs.forEach(input => {
                    input.classList.remove('is-invalid', 'is-valid');
                });
            }
        }
        
        // Cerrar modal
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });
        
        // Cerrar modal al hacer clic en bg-back
        const bgBack = modal.querySelector('.bg-back');
        if (bgBack) {
            bgBack.addEventListener('click', closeModal);
        }
        
        // Manejar el submit del formulario
        form.addEventListener('submit', function(e) {
            // Validar formulario
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return false;
            }
            
            // Asegurarse de que el course_id esté presente
            const courseIdInput = form.querySelector('#subjectCourseId');
            if (!courseIdInput || !courseIdInput.value) {
                // Si no hay course_id, no permitir el envío
                e.preventDefault();
                alert('Error: No se pudo identificar el curso. Por favor, intente nuevamente.');
                return false;
            }
            
            // Mostrar loading
            const submitBtn = form.querySelector('#submitSubjectBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
            }
            
            // Permitir que el formulario se envíe normalmente
            return true;
        }, false);
    }, 100);
}

// Initialize Edit Subject Modal
function initializeEditSubjectModal() {
    setTimeout(function() {
        const modal = document.getElementById('editSubjectModal');
        const openModalBtns = document.querySelectorAll('.open-edit-subject-modal');
        const closeModalBtns = modal ? modal.querySelectorAll('.close-modal') : [];
        const form = document.getElementById('editSubjectForm');
        
        if (!modal || !form) return;
        
        // Abrir modal desde los botones "Editar"
        openModalBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const subjectId = this.getAttribute('data-subject-id');
                const subjectName = this.getAttribute('data-subject-name');
                
                // Actualizar el formulario con los datos de la materia
                const subjectIdInput = form.querySelector('#editSubjectId');
                if (subjectIdInput) {
                    subjectIdInput.value = subjectId;
                }
                
                // Actualizar la acción del formulario
                form.action = `/subjects/${subjectId}/edit`;
                
                // Seleccionar la materia actual en el select
                const subjectSelect = form.querySelector('#edit-subject-name');
                if (subjectSelect) {
                    // Buscar la opción que coincida con el nombre de la materia
                    const options = subjectSelect.querySelectorAll('option');
                    options.forEach(option => {
                        if (option.value === subjectName) {
                            option.selected = true;
                        } else {
                            option.selected = false;
                        }
                    });
                }
                
                modal.classList.add('show');
                modal.style.display = 'flex';
                modal.removeAttribute('aria-hidden');
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
                
                if (form) {
                    form.classList.remove('was-validated');
                    const inputs = form.querySelectorAll('.is-invalid, .is-valid');
                    inputs.forEach(input => {
                        input.classList.remove('is-invalid', 'is-valid');
                    });
                }
                
                const submitBtn = form.querySelector('#submitEditSubjectBtn');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.removeAttribute('disabled');
                }
            });
        });
        
        // Función para cerrar el modal
        function closeModal() {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
            
            if (form) {
                form.reset();
                form.classList.remove('was-validated');
                const inputs = form.querySelectorAll('.is-invalid, .is-valid');
                inputs.forEach(input => {
                    input.classList.remove('is-invalid', 'is-valid');
                });
            }
        }
        
        // Cerrar modal
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', closeModal);
        });
        
        // Cerrar modal al hacer clic en bg-back
        const bgBack = modal.querySelector('.bg-back');
        if (bgBack) {
            bgBack.addEventListener('click', closeModal);
        }
        
        // Manejar el submit del formulario
        form.addEventListener('submit', function(e) {
            // Validar formulario
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return false;
            }
            
            // Mostrar loading
            const submitBtn = form.querySelector('#submitEditSubjectBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
            }
            
            // Permitir que el formulario se envíe normalmente
            return true;
        }, false);
    }, 100);
}

// Delete modal functions are now in delete_modal.js

window.coursesManagement = {
    showToast,
    showLoadingState,
    hideLoadingState,
    initializeDeleteSubjectModal,
    initializeCreateCourseModal,
    initializeCreateSubjectModal,
    initializeEditSubjectModal,
    showDeleteConfirmationModal
};
