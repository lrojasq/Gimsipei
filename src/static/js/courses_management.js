// Courses Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAutoCloseAlerts();
    initializeAccordion();
    initializeDeleteSubjectModal();
    initializeCreateCourseModal();
    initializeCreateSubjectModal();
    initializeEditSubjectModal();
});

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

// Show Loading State
function showLoadingState(button) {
    // Prevent double-application
    if (button.classList.contains('loading')) return;

    button.classList.add('loading');
    button.disabled = true;

    // Store original text only once
    if (!button.getAttribute('data-original-text')) {
        button.setAttribute('data-original-text', button.innerHTML);
    }

    // Don't inject an inline spinner icon here,
    // The CSS `.btn.loading::after` already renders a spinner.
    button.innerHTML = 'Procesando...';
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


// Delete Subject Modal 
function initializeDeleteSubjectModal() {
    initializeDeleteButtons('.open-delete-subject-modal', function(button) {
        const courseId = button.getAttribute('data-course-id');
        const subjectId = button.getAttribute('data-subject-id');
        const teacherId = button.getAttribute('data-teacher-id');
        return `/courses/${courseId}/subjects/${subjectId}/${teacherId}/remove`;
    });
}

// Initialize Create Course Modal
function initializeCreateCourseModal() {
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
                
                const submitBtn = form.querySelector('button[type="submit"]');
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
            // prevent double submit
            if (form.dataset.submitting === '1') {
                e.preventDefault();
                return false;
            }

            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return false;
            }
            
            // Mostrar loading
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
            form.dataset.submitting = '1';

            // Force paint: submit on next tick so the spinner is visible
            e.preventDefault();
            setTimeout(() => form.submit(), 0);
        }, false);
}

// Initialize Create Subject Modal
function initializeCreateSubjectModal() {
    const modal = document.getElementById('subjectModal');
    const openModalBtns = document.querySelectorAll('.open-create-subject-modal, .add-subject-btn');
    const closeModalBtns = modal ? modal.querySelectorAll('.close-modal') : [];
    const form = document.getElementById('subjectForm');
    
    if (!modal || !form) {
        return;
    }
        
        // Abrir modal desde los botones "AÑADIR" de materias
        openModalBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const courseId = this.getAttribute('data-course-id');
                
                // Configurar modo crear
                document.getElementById('subjectModalTitle').textContent = 'Crear materia';
                document.getElementById('teacherLabel').textContent = 'Profesor';
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.textContent = 'Guardar';
                const redirectToInput = document.getElementById('redirectToInput');
                if (redirectToInput) redirectToInput.value = 'courses_management';
                
                // Restaurar la acción original del formulario
                form.action = '/subjects/create';
                
                // Mostrar campo de selección de materia y ocultar input de edición
                const subjectNameField = document.getElementById('subjectNameField');
                if (subjectNameField) {
                    subjectNameField.style.display = 'block';
                    
                    // Mostrar el select
                    const subjectSelect = document.querySelector('#subject-name');
                    if (subjectSelect) {
                        subjectSelect.style.display = 'block';
                        subjectSelect.setAttribute('required', 'required');
                    }
                    
                    // Ocultar el input de edición si existe
                    const subjectInput = document.getElementById('subject-name-edit');
                    if (subjectInput) {
                        subjectInput.style.display = 'none';
                        subjectInput.removeAttribute('required');
                    }
                }
                
                // Resetear formulario
                form.reset();
                form.classList.remove('was-validated');
                
                // Actualizar el course_id en el formulario
                const courseIdInput = document.getElementById('courseIdInput');
                if (courseIdInput && courseId) {
                    courseIdInput.value = courseId;
                }
                
                // Limpiar subject_id para modo crear
                const subjectIdInput = document.getElementById('subjectIdInput');
                if (subjectIdInput) {
                    subjectIdInput.value = '';
                }
                
                // Resetear select de profesores
                const teacherSelect = document.getElementById('teacher_id');
                if (teacherSelect) {
                    teacherSelect.name = 'teacher_id';
                    teacherSelect.value = '';
                    teacherSelect.removeAttribute('disabled');
                    teacherSelect.parentElement.style.display = 'block';
                    
                    Array.from(teacherSelect.options).forEach(opt => {
                        opt.disabled = false;
                        opt.textContent = opt.textContent.replace(' (Actual)', '');
                    });
                }
                
                modal.classList.add('show');
                modal.style.display = 'flex';
                modal.removeAttribute('aria-hidden');
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
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
            // prevent double submit
            if (form.dataset.submitting === '1') {
                e.preventDefault();
                return false;
            }

            // Validar formulario
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return false;
            }
            
            // Verificar que el course_id exista antes de enviar (usando el ID correcto)
            const courseIdInput = document.getElementById('courseIdInput');
            
            if (!courseIdInput || !courseIdInput.value) {
                // Si no hay course_id, no permitir el envío
                e.preventDefault();
                alert('Error: No se pudo identificar el curso. Por favor, intente nuevamente.');
                return false;
            }
            
            // Mostrar loading
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
            form.dataset.submitting = '1';

            // Force paint: submit on next tick so the spinner is visible
            e.preventDefault();
            setTimeout(() => form.submit(), 0);
            return false;
        }, false);
}

// Initialize Edit Subject Modal
function initializeEditSubjectModal() {
    const modal = document.getElementById('subjectModal');
    const form = document.getElementById('subjectForm');
    const editButtons = document.querySelectorAll('.open-edit-subject-modal');

    if (!modal || !form) {
        return;
    }

        editButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();

                const courseId = this.getAttribute('data-course-id');
                const subjectId = this.getAttribute('data-subject-id');
                const subjectName = this.getAttribute('data-subject-name');
                const teacherId = this.getAttribute('data-teacher-id');

                // Resetear primero
                form.reset();
                form.classList.remove('was-validated');

                // Configurar modo editar
                document.getElementById('subjectModalTitle').textContent = 'Editar materia';
                document.getElementById('teacherLabel').textContent = 'Profesor';
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.textContent = 'Actualizar';

                const redirectToInput = document.getElementById('redirectToInput');
                if (redirectToInput) redirectToInput.value = 'courses_management';

                // Ruta de edición de materia
                form.action = `/subjects/${subjectId}/edit`;

                // Set hidden inputs
                const courseIdInput = document.getElementById('courseIdInput');
                if (courseIdInput) courseIdInput.value = courseId || '';

                const subjectIdInput = document.getElementById('subjectIdInput');
                if (subjectIdInput) subjectIdInput.value = subjectId || '';

                // Convertir el select de materia en un input text para edición
                const subjectNameField = document.getElementById('subjectNameField');
                if (subjectNameField) {
                    // Ocultar el select
                    const subjectSelect = document.getElementById('subject-name');
                    if (subjectSelect) {
                        subjectSelect.style.display = 'none';
                        subjectSelect.removeAttribute('required');
                    }
                    
                    // Verificar si ya existe un input de texto para edición
                    let subjectInput = document.getElementById('subject-name-edit');
                    if (!subjectInput) {
                        // Crear input de texto si no existe
                        subjectInput = document.createElement('input');
                        subjectInput.type = 'text';
                        subjectInput.className = 'form-control';
                        subjectInput.id = 'subject-name-edit';
                        subjectInput.name = 'name';
                        subjectInput.required = true;
                        subjectNameField.appendChild(subjectInput);
                    }
                    
                    subjectInput.style.display = 'block';
                    subjectInput.value = subjectName || '';
                }

                // Preseleccionar profesor
                const teacherSelect = document.getElementById('teacher_id');
                if (teacherSelect && teacherId) {
                    teacherSelect.value = teacherId;
                }

                // Mostrar modal
                modal.classList.add('show');
                modal.style.display = 'flex';
                modal.removeAttribute('aria-hidden');
                modal.setAttribute('aria-modal', 'true');
                modal.setAttribute('role', 'dialog');
            });
        });
}
