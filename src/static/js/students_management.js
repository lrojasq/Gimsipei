// Students Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeDeleteModalListeners();
    initializeDeleteModal();
    initializeAutoCloseAlerts();
    initializeCreateStudentButton();
    initializeViewLinks();
});

// Función genérica para mostrar modal de confirmación de eliminación
function showDeleteConfirmationModal(actionUrl) {
    const modal = document.getElementById('deleteConfirmationModal');
    const form = document.getElementById('deleteConfirmationForm');
    
    if (!modal || !form) {
        console.error('Modal o formulario de confirmación no encontrado');
        return;
    }
    
    // Establecer la acción del formulario
    form.action = actionUrl;
    
    // Usar Bootstrap Modal si está disponible
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    } else {
        // Fallback si Bootstrap no está disponible
        modal.classList.add('show');
        modal.style.display = 'flex';
        modal.removeAttribute('aria-hidden');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('role', 'dialog');
    }
}

// Inicializar listeners del modal (cerrar)
function initializeDeleteModalListeners() {
    setTimeout(function() {
        const modal = document.getElementById('deleteConfirmationModal');
        if (!modal) return;
        
        const closeModalBtns = modal.querySelectorAll('.close-modal');
        const bgBack = modal.querySelector('.bg-back');
        
        // Función para cerrar el modal
        function closeModal() {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
        }
        
        // Listeners para los botones de cerrar
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeModal();
            });
        });
            
        // Listener para el fondo
        if (bgBack) {
            bgBack.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeModal();
            });
        }
    }, 200);
}

// Delete Student Modal Functionality
function initializeDeleteModal() {
    // La funcionalidad de eliminar ahora se maneja en el event listener global
    // para soportar tanto botones <a> como <button>
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

// Initialize Create Student Button
function initializeCreateStudentButton() {
    const createBtn = document.getElementById('createStudentBtn');
    if (createBtn) {
        createBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Obtener el course_id de la URL actual
            const urlParts = window.location.pathname.split('/');
            const courseIdIndex = urlParts.indexOf('courses');
            const courseId = courseIdIndex !== -1 && urlParts[courseIdIndex + 1] ? urlParts[courseIdIndex + 1] : null;
            
            if (courseId) {
                // Redirigir a la página de crear estudiante con el course_id
                window.location.href = `/users/courses/${courseId}/students/create`;
            } else {
                console.error('No se pudo obtener el ID del curso');
            }
        });
    }
}

// Initialize View Links (Tareas y Evaluaciones)
function initializeViewLinks() {
    const viewLinks = document.querySelectorAll('.view-link-btn');
    
    viewLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            // Obtener el course_id y student_id
            const urlParts = window.location.pathname.split('/');
            const courseIdIndex = urlParts.indexOf('courses');
            const courseId = courseIdIndex !== -1 && urlParts[courseIdIndex + 1] ? urlParts[courseIdIndex + 1] : null;
            
            const studentId = this.getAttribute('data-student-id');
            
            // Determinar si es Tareas o Evaluaciones basado en el atributo data-type
            const linkType = this.getAttribute('data-type');
            
            if (courseId && studentId) {
                if (linkType === 'tasks') {
                    // Redirigir a vista de tareas del estudiante
                    window.location.href = `/users/courses/${courseId}/students/${studentId}/tasks`;
                } else if (linkType === 'evaluations') {
                    // Redirigir a vista de evaluaciones del estudiante
                    window.location.href = `/users/courses/${courseId}/students/${studentId}/evaluations`;
                } else {
                    // Por ahora, solo mostrar un mensaje
                    alert('Funcionalidad en desarrollo');
                }
            } else {
                console.error('No se pudo obtener el ID del curso o estudiante');
                // Por ahora, solo mostrar un mensaje
                alert('Funcionalidad en desarrollo');
            }
        });
    });
}

// Edit Student Functionality
document.addEventListener('click', function(e) {
    if (e.target.closest('.edit-student')) {
        e.preventDefault();
        const editBtn = e.target.closest('.edit-student');
        const studentId = editBtn.getAttribute('data-student-id');
        
        // Obtener el course_id de la URL actual
        const urlParts = window.location.pathname.split('/');
        const courseIdIndex = urlParts.indexOf('courses');
        const courseId = courseIdIndex !== -1 && urlParts[courseIdIndex + 1] ? urlParts[courseIdIndex + 1] : null;
        
        if (courseId && studentId) {
            // Redirigir a la página de editar estudiante
            window.location.href = `/users/courses/${courseId}/students/${studentId}/edit`;
        } else {
            console.error('No se pudo obtener el ID del curso o estudiante');
            alert('Error al obtener la información del estudiante');
        }
    }
    
    // Handle delete button clicks
    if (e.target.closest('.delete-student')) {
        e.preventDefault();
        const deleteBtn = e.target.closest('.delete-student');
        const studentId = deleteBtn.getAttribute('data-student-id');
        const studentName = deleteBtn.getAttribute('data-student-name');
        
        // Obtener el course_id de la URL actual
        const urlParts = window.location.pathname.split('/');
        const courseIdIndex = urlParts.indexOf('courses');
        const courseId = courseIdIndex !== -1 && urlParts[courseIdIndex + 1] ? urlParts[courseIdIndex + 1] : null;
        
        if (!courseId) {
            console.error('No se pudo obtener el ID del curso');
            return;
        }
        
        // Construir la URL de eliminación
        const deleteUrl = `/users/courses/${courseId}/students/${studentId}/delete`;
        
        // Actualizar el mensaje del modal si existe
        const modal = document.getElementById('deleteConfirmationModal');
        if (modal) {
            const modalBody = modal.querySelector('.modal-body p');
            if (modalBody && studentName) {
                modalBody.textContent = `¿Está seguro que desea eliminar a ${studentName} de este curso? Esta operación es irreversible.`;
            }
        }
        
        // Mostrar modal de confirmación con la URL
        showDeleteConfirmationModal(deleteUrl);
    }
});

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
window.studentsManagement = {
    showDeleteConfirmationModal,
    showToast
};

