// Classes and Resources Management JavaScript

// Initialize expand/collapse functionality for course rows
function initializeExpandButtons() {
    const expandButtons = document.querySelectorAll('.expand-btn');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const courseRow = this.closest('.course-row');
            const expandableRow = document.querySelector(`.expandable-row[data-course-id="${courseId}"]`);
            const icon = this.querySelector('i');
            
            if (!expandableRow) return;
            
            // Toggle expanded state
            const isExpanded = expandableRow.classList.contains('show');
            
            if (isExpanded) {
                // Collapse
                expandableRow.classList.remove('show');
                expandableRow.style.display = 'none';
                courseRow.classList.remove('expanded');
                if (icon) {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                }
            } else {
                // Expand
                expandableRow.classList.add('show');
                expandableRow.style.display = 'table-row';
                courseRow.classList.add('expanded');
                if (icon) {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                }
            }
        });
    });
}

// Period functionality removed - no longer needed

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

// Period loading functionality removed - no longer needed

// Initialize add class/resource buttons
function initializeAddButtons() {
    // Add Class buttons
    const addClassButtons = document.querySelectorAll('.add-class-btn');
    addClassButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const subjectId = this.getAttribute('data-subject-id');
            const subjectName = this.getAttribute('data-subject-name');
            openCreateClassModal(courseId, subjectId, subjectName);
        });
    });
    
    // Add Resource buttons
    const addResourceButtons = document.querySelectorAll('.add-resource-btn');
    addResourceButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const subjectId = this.getAttribute('data-subject-id');
            const subjectName = this.getAttribute('data-subject-name');
            openCreateResourceModal(courseId, subjectId, subjectName);
        });
    });
}

// Open Create Class Modal
function openCreateClassModal(courseId, subjectId, subjectName) {
    const modal = document.getElementById('createClassModal');
    
    // Set hidden fields
    document.getElementById('class_course_id').value = courseId;
    document.getElementById('class_subject_id').value = subjectId;
    
    // Show modal
    modal.style.display = 'flex';
    
    // Reset form
    document.getElementById('createClassForm').reset();
    document.getElementById('class_cover_name').textContent = '';
}

// Close Create Class Modal
function closeCreateClassModal() {
    const modal = document.getElementById('createClassModal');
    modal.style.display = 'none';
    document.getElementById('createClassForm').reset();
    document.getElementById('class_cover_name').textContent = '';
}

// Open Create Resource Modal
function openCreateResourceModal(courseId, subjectId, subjectName) {
    const modal = document.getElementById('createResourceModal');
    
    // Set hidden fields
    document.getElementById('resource_course_id').value = courseId;
    document.getElementById('resource_subject_id').value = subjectId;
    
    // Show modal
    modal.style.display = 'flex';
    
    // Reset form
    document.getElementById('createResourceForm').reset();
    document.getElementById('resource_file_name').textContent = '';
}

// Close Create Resource Modal
function closeCreateResourceModal() {
    const modal = document.getElementById('createResourceModal');
    modal.style.display = 'none';
    document.getElementById('createResourceForm').reset();
    document.getElementById('resource_file_name').textContent = '';
}

// Handle file input changes
function initializeFileInputs() {
    // Class cover image
    const classCoverInput = document.getElementById('class_cover');
    if (classCoverInput) {
        classCoverInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : '';
            document.getElementById('class_cover_name').textContent = fileName;
        });
    }
    
    // Resource file
    const resourceFileInput = document.getElementById('resource_file');
    if (resourceFileInput) {
        resourceFileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : '';
            document.getElementById('resource_file_name').textContent = fileName;
        });
    }
}

// Close modal when clicking outside
function initializeModalBackgroundClose() {
    document.getElementById('createClassModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeCreateClassModal();
        }
    });
    
    document.getElementById('createResourceModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeCreateResourceModal();
        }
    });
}

// Update the main DOMContentLoaded to include new initializations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeExpandButtons();
    initializeClassActions();
    initializeAutoCloseAlerts();
    initializeAddButtons();
    initializeFileInputs();
    initializeModalBackgroundClose();
});

// Make functions globally available
window.openCreateClassModal = openCreateClassModal;
window.closeCreateClassModal = closeCreateClassModal;
window.openCreateResourceModal = openCreateResourceModal;
window.closeCreateResourceModal = closeCreateResourceModal;

// Export functions for global use
window.classesResources = {
    expandAll,
    collapseAll,
    filterClasses,
    showToast,
    showLoading,
    hideLoading,
    openCreateClassModal,
    closeCreateClassModal,
    openCreateResourceModal,
    closeCreateResourceModal
};

