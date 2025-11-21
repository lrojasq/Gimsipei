// Resources View JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializePeriodSelector();
    initializeResourceModal();
    initializeAddFirstResourceButtons();
    initializeDeleteModalListeners();
    initializeDeleteResourceModal();
});

// Period Selector Functionality
function initializePeriodSelector() {
    const periodBtns = document.querySelectorAll('.period-btn');
    const periodContents = document.querySelectorAll('.period-content');

    periodBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.getAttribute('data-period');

            // Remove active class from all buttons
            periodBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');

            // Hide all period contents
            periodContents.forEach(content => {
                content.style.display = 'none';
            });

            // Show selected period content
            const selectedContents = document.querySelectorAll(`.period-content[data-period="${period}"]`);
            selectedContents.forEach(content => {
                content.style.display = 'flex';
            });
        });
    });
}

// Resource Modal Functions
function openCreateResourceModal(subjectId, period = null) {
    const modal = document.getElementById('createResourceModal');
    if (modal) {
        modal.style.display = 'flex';
        
        // Set subject ID if available
        const subjectIdInput = document.getElementById('resource_subject_id');
        if (subjectIdInput && subjectId) {
            subjectIdInput.value = subjectId;
        }
        
        // Set period if provided
        if (period) {
            const periodSelect = document.querySelector('#createResourceModal select[name="period"]');
            if (periodSelect) {
                periodSelect.value = period;
            }
        } else {
            // Use currently active period
            const activeBtn = document.querySelector('.period-btn.active');
            if (activeBtn) {
                const periodSelect = document.querySelector('#createResourceModal select[name="period"]');
                if (periodSelect) {
                    periodSelect.value = activeBtn.getAttribute('data-period');
                }
            }
        }
    }
}

function closeCreateResourceModal() {
    const modal = document.getElementById('createResourceModal');
    if (modal) {
        modal.style.display = 'none';
        
        // Reset form
        const form = document.getElementById('createResourceForm');
        if (form) {
            form.reset();
            // Reset file name displays
            const fileNameDisplays = document.querySelectorAll('.file-name');
            fileNameDisplays.forEach(display => {
                display.textContent = '';
            });
        }
    }
}

// Initialize "Add First Resource" buttons
function initializeAddFirstResourceButtons() {
    const addFirstResourceBtns = document.querySelectorAll('.btn-add-first-resource');
    
    addFirstResourceBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            const subjectId = this.getAttribute('data-subject-id');
            openCreateResourceModal(subjectId, period);
        });
    });
}

function initializeResourceModal() {
    // Close modal when clicking outside
    const modal = document.getElementById('createResourceModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeCreateResourceModal();
            }
        });
    }

    // File input display name
    const coverImageInput = document.getElementById('resource_cover_image');
    if (coverImageInput) {
        coverImageInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : '';
            const fileNameDisplay = document.getElementById('resource_cover_image_name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        });
    }

    // Resource file input display name
    const resourceFileInput = document.getElementById('resource_file');
    if (resourceFileInput) {
        resourceFileInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : '';
            const fileNameDisplay = document.getElementById('resource_file_name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        });
    }

    // Handle ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeCreateResourceModal();
        }
    });
}

// Delete Resource Modal Functionality
function initializeDeleteResourceModal() {
    initializeDeleteButtons('.open-delete-resource-modal', function(button) {
        const resourceId = button.getAttribute('data-resource-id');
        return `/resources/delete/${resourceId}`;
    });
}

// Alert auto-dismiss
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.5s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);

