// Resources View JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializePeriodSelector();
    initializeResourceModal();
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
            const selectedContent = document.querySelector(`.period-content[data-period="${period}"]`);
            if (selectedContent) {
                selectedContent.style.display = 'grid';
            }
        });
    });
}

// Resource Modal Functions
function openCreateResourceModal(subjectId) {
    const modal = document.getElementById('createResourceModal');
    if (modal) {
        modal.style.display = 'flex';
        
        // Set subject ID if available
        const subjectIdInput = document.getElementById('resource_subject_id');
        if (subjectIdInput && subjectId) {
            subjectIdInput.value = subjectId;
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
        }
    }
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

    // Handle ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeCreateResourceModal();
        }
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

