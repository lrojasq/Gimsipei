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
    
    // Mostrar modal
    modal.classList.add('show');
    modal.style.display = 'flex';
    modal.removeAttribute('aria-hidden');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('role', 'dialog');
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
    setTimeout(function() {
        const deleteButtons = document.querySelectorAll('.delete-student');
        
        // Abrir modal desde los botones de eliminar
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const studentId = this.getAttribute('data-student-id');
                
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
                
                // Mostrar modal de confirmación con la URL
                showDeleteConfirmationModal(deleteUrl);
            });
        });
    }, 100);
}

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

// Initialize View Links (Tareas y Evaluaciones) - Solo para estilos
function initializeViewLinks() {
    // Los enlaces ahora son directos en HTML, solo necesitamos asegurar estilos
    const viewLinks = document.querySelectorAll('.view-link-btn');
    
    viewLinks.forEach(link => {
        // Asegurar que los enlaces tengan el estilo correcto
        if (!link.classList.contains('view-link-btn')) {
            link.classList.add('view-link-btn');
        }
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
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    } else {
        // Fallback: mostrar el toast manualmente
        toastElement.classList.add('show');
    }
    
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

