// Student Tasks JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAccordion();
    initializeDownloadLinks();
    initializeDeleteButtons();
    initializeAutoCloseAlerts();
});

// Initialize Accordion (Expand/Collapse Subjects)
function initializeAccordion() {
    const subjectRows = document.querySelectorAll('.subject-row');
    
    subjectRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // No expandir si se hace clic en un botón o enlace dentro
            if (e.target.closest('.download-link') || e.target.closest('.delete-class-btn')) {
                return;
            }
            
            const subjectId = this.getAttribute('data-subject-id');
            // Obtener todas las filas de clases de esta materia
            const contentRows = document.querySelectorAll(
                `.subject-content-row[data-subject-id="${subjectId}"]`
            );
            const toggleIcon = this.querySelector('.toggle-subject');
            
            if (contentRows.length > 0) {
                const isExpanded = this.classList.contains('expanded');
                
                if (isExpanded) {
                    // Colapsar - ocultar todas las filas de clases
                    contentRows.forEach(contentRow => {
                        contentRow.style.display = 'none';
                    });
                    this.classList.remove('expanded');
                    if (toggleIcon) {
                        toggleIcon.style.transform = 'rotate(0deg)';
                    }
                } else {
                    // Expandir - mostrar todas las filas de clases
                    contentRows.forEach(contentRow => {
                        contentRow.style.display = 'table-row';
                    });
                    this.classList.add('expanded');
                    if (toggleIcon) {
                        toggleIcon.style.transform = 'rotate(180deg)';
                    }
                }
            }
        });
    });
}

// Initialize Download Links
function initializeDownloadLinks() {
    const downloadLinks = document.querySelectorAll('.download-link');
    
    downloadLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Evitar que se expanda/colapse la asignatura
            
            const classId = this.getAttribute('data-class-id');
            
            // Por ahora, solo mostrar un mensaje
            // TODO: Implementar la funcionalidad de descarga
            alert(`Funcionalidad de descarga para clase ID: ${classId} - En desarrollo`);
        });
    });
}

// Initialize Delete Buttons
function initializeDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-class-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Evitar que se expanda/colapse la asignatura
            
            const classId = this.getAttribute('data-class-id');
            const className = this.getAttribute('data-class-title');
            
            // Confirmar eliminación
            if (confirm(`¿Está seguro que desea eliminar la clase "${className}"?`)) {
                // TODO: Implementar la funcionalidad de eliminación
                // Por ahora, solo mostrar un mensaje
                alert(`Funcionalidad de eliminación para clase ID: ${classId} - En desarrollo`);
            }
        });
    });
}

// Auto Close Alerts
function initializeAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

