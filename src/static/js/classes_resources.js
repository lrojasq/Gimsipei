// Classes and Resources Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeExpandButtons();
    initializePeriodButtons();
    initializeClassActions();
    initializeAutoCloseAlerts();
    
    // Set initial period from URL or default to 1
    const urlParams = new URLSearchParams(window.location.search);
    const currentPeriod = urlParams.get('period') || '1';
    setActivePeriod(currentPeriod);
});

// Initialize expand/collapse functionality for course rows
function initializeExpandButtons() {
    const expandButtons = document.querySelectorAll('.expand-btn');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const courseRow = this.closest('.course-row');
            const expandableRow = document.querySelector(`.expandable-row[data-course-id="${courseId}"]`);
            
            if (!expandableRow) return;
            
            // Toggle expanded state
            const isExpanded = expandableRow.classList.contains('show');
            
            if (isExpanded) {
                // Collapse
                expandableRow.classList.remove('show');
                expandableRow.style.display = 'none';
                courseRow.classList.remove('expanded');
                this.classList.remove('expanded');
            } else {
                // Expand
                expandableRow.classList.add('show');
                expandableRow.style.display = 'table-row';
                courseRow.classList.add('expanded');
                this.classList.add('expanded');
            }
        });
    });
}

// Initialize period selector buttons
function initializePeriodButtons() {
    const periodButtons = document.querySelectorAll('.period-btn');
    
    periodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            
            // Update active button
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Reload page with new period
            const url = new URL(window.location.href);
            url.searchParams.set('period', period);
            window.location.href = url.toString();
        });
    });
}

// Set active period button based on current period
function setActivePeriod(period) {
    const periodButtons = document.querySelectorAll('.period-btn');
    
    periodButtons.forEach(button => {
        if (button.getAttribute('data-period') === period.toString()) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Initialize class action buttons (edit, view resources, delete)
function initializeClassActions() {
    // Edit class buttons
    const editButtons = document.querySelectorAll('.edit-class');
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const classId = this.getAttribute('data-class-id');
            // TODO: Navigate to edit class page
            console.log('Edit class:', classId);
            showToast('Funcionalidad de edición en desarrollo', 'info');
        });
    });
    
    // View resources buttons
    const viewResourcesButtons = document.querySelectorAll('.view-resources');
    viewResourcesButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const classId = this.getAttribute('data-class-id');
            // TODO: Navigate to resources page
            console.log('View resources for class:', classId);
            showToast('Funcionalidad de recursos en desarrollo', 'info');
        });
    });
    
    // Delete class buttons
    const deleteButtons = document.querySelectorAll('.delete-class');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const classId = this.getAttribute('data-class-id');
            
            if (confirm('¿Está seguro de que desea eliminar esta clase? Esta acción no se puede deshacer.')) {
                // TODO: Implement delete functionality
                console.log('Delete class:', classId);
                showToast('Funcionalidad de eliminación en desarrollo', 'info');
            }
        });
    });
}

// Auto close alerts after 5 seconds
function initializeAutoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            // Check if Bootstrap is available
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                // Fallback: simply hide the alert
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

// Show loading overlay
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(overlay);
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Show toast notification
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
        // Fallback: show the toast manually
        toastElement.classList.add('show');
        setTimeout(() => {
            toastElement.remove();
        }, 5000);
    }
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Expand all courses
function expandAll() {
    const expandButtons = document.querySelectorAll('.expand-btn:not(.expanded)');
    expandButtons.forEach(button => button.click());
}

// Collapse all courses
function collapseAll() {
    const expandButtons = document.querySelectorAll('.expand-btn.expanded');
    expandButtons.forEach(button => button.click());
}

// Filter classes by search term
function filterClasses(searchTerm) {
    const courseRows = document.querySelectorAll('.course-row');
    const lowerSearchTerm = searchTerm.toLowerCase();
    
    courseRows.forEach(row => {
        const courseName = row.querySelector('.course-name').textContent.toLowerCase();
        
        if (courseName.includes(lowerSearchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
            // Also hide expanded row if exists
            const courseId = row.getAttribute('data-course-id');
            const expandableRow = document.querySelector(`.expandable-row[data-course-id="${courseId}"]`);
            if (expandableRow) {
                expandableRow.style.display = 'none';
                expandableRow.classList.remove('show');
            }
        }
    });
}

// Reload classes for specific period (AJAX)
async function loadClassesForPeriod(period) {
    showLoading();
    
    try {
        // Get current URL and add period parameter
        const url = new URL(window.location.href);
        url.searchParams.set('period', period);
        
        // For now, just reload the page
        // TODO: Implement AJAX loading
        window.location.href = url.toString();
    } catch (error) {
        console.error('Error loading classes:', error);
        showToast('Error al cargar las clases', 'danger');
        hideLoading();
    }
}

// Export functions for global use
window.classesResources = {
    expandAll,
    collapseAll,
    filterClasses,
    loadClassesForPeriod,
    showToast,
    showLoading,
    hideLoading
};

