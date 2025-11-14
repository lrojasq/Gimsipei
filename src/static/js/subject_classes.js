// Subject Classes JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get course and subject IDs from data attributes
    const container = document.querySelector('.container_category');
    const courseId = container ? container.getAttribute('data-course-id') : null;
    const subjectId = container ? container.getAttribute('data-subject-id') : null;
    
    // Set course and subject IDs for modals
    if (courseId && subjectId) {
        const classCourseIdInput = document.getElementById('class_course_id');
        const classSubjectIdInput = document.getElementById('class_subject_id');
        
        if (classCourseIdInput) classCourseIdInput.value = courseId;
        if (classSubjectIdInput) classSubjectIdInput.value = subjectId;
    }
    
    // Period filter functionality
    const periodButtons = document.querySelectorAll('.period-btn');
    const periodContainers = document.querySelectorAll('.period-classes-container');
    const classPeriodInput = document.getElementById('class_period');
    
    periodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            
            // Update active button
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding period container
            periodContainers.forEach(container => {
                if (container.getAttribute('data-period') === period) {
                    container.style.display = 'block';
                } else {
                    container.style.display = 'none';
                }
            });
            
            // Update hidden input for creating classes
            if (classPeriodInput) {
                classPeriodInput.value = period;
            }
        });
    });
    
    // Add class button
    const addClassBtn = document.getElementById('addClassBtn');
    const addFirstClassBtns = document.querySelectorAll('.btn-add-first-class');
    
    if (addClassBtn) {
        addClassBtn.addEventListener('click', function() {
            openCreateClassModal();
        });
    }
    
    addFirstClassBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            openCreateClassModal(period);
        });
    });
    
    // Edit class buttons
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const classId = this.getAttribute('data-class-id');
            openEditClassModal(classId);
        });
    });
    
    // Delete class buttons
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const classId = this.getAttribute('data-class-id');
            openDeleteConfirmationModal(classId);
        });
    });
    
    // File upload display for create modal
    const fileInput = document.getElementById('class_cover');
    const fileName = document.getElementById('class_cover_name');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileName.textContent = this.files[0].name;
            } else {
                fileName.textContent = '';
            }
        });
    }
    
    // File upload display for edit modal
    const editFileInput = document.getElementById('edit_class_cover');
    const editFileName = document.getElementById('edit_class_cover_name');
    
    if (editFileInput) {
        editFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                editFileName.textContent = this.files[0].name;
            } else {
                editFileName.textContent = '';
            }
        });
    }
});

// Open create class modal
function openCreateClassModal(period = null) {
    const modal = document.getElementById('createClassModal');
    const classPeriodSelect = document.querySelector('#createClassModal select[name="period"]');
    
    // Reset form
    document.getElementById('createClassForm').reset();
    document.getElementById('class_cover_name').textContent = '';
    
    // Set period if provided
    if (period && classPeriodSelect) {
        classPeriodSelect.value = period;
    } else {
        // Use currently active period
        const activeBtn = document.querySelector('.period-btn.active');
        if (activeBtn && classPeriodSelect) {
            classPeriodSelect.value = activeBtn.getAttribute('data-period');
        }
    }
    
    modal.style.display = 'flex';
}

// Close create class modal
function closeCreateClassModal() {
    const modal = document.getElementById('createClassModal');
    modal.style.display = 'none';
}

// Open edit class modal
function openEditClassModal(classId) {
    const modal = document.getElementById('editClassModal');
    const form = document.getElementById('editClassForm');
    
    // Find the class card
    const classCard = document.querySelector(`[data-class-id="${classId}"]`).closest('.class-card');
    
    if (!classCard) {
        console.error('Class card not found');
        return;
    }
    
    // Extract class data from the card
    const classNumber = classCard.querySelector('.class-title').textContent.replace('Clase ', '');
    const title = classCard.querySelector('.class-description-title').textContent;
    const description = classCard.querySelector('.class-description').textContent;
    const coverImage = classCard.querySelector('.class-image');
    
    // Get the current period from the visible container
    const activePeriod = document.querySelector('.period-btn.active').getAttribute('data-period');
    
    // Populate form
    document.getElementById('edit_class_id').value = classId;
    document.getElementById('edit_class_number').value = classNumber;
    document.getElementById('edit_class_title').value = title;
    document.getElementById('edit_class_description').value = description;
    document.getElementById('edit_class_period').value = activePeriod;
    
    // Get course_id and subject_id from the page data attributes
    const container = document.querySelector('.container_category');
    const courseId = container ? container.getAttribute('data-course-id') : '';
    const subjectId = container ? container.getAttribute('data-subject-id') : '';
    document.getElementById('edit_class_course_id').value = courseId;
    document.getElementById('edit_class_subject_id').value = subjectId;
    
    // Set form action
    form.action = `/classes/update/${classId}`;
    
    // Show current cover if exists
    const currentCoverPreview = document.getElementById('current_cover_preview');
    const currentCoverImage = document.getElementById('current_cover_image');
    
    if (coverImage && !classCard.querySelector('.default-image')) {
        currentCoverImage.src = coverImage.src;
        currentCoverPreview.style.display = 'block';
    } else {
        currentCoverPreview.style.display = 'none';
    }
    
    // Reset file input
    document.getElementById('edit_class_cover').value = '';
    document.getElementById('edit_class_cover_name').textContent = '';
    
    modal.style.display = 'flex';
}

// Close edit class modal
function closeEditClassModal() {
    const modal = document.getElementById('editClassModal');
    modal.style.display = 'none';
}

// Open delete confirmation modal
function openDeleteConfirmationModal(classId) {
    const modal = document.getElementById('deleteConfirmationModal');
    const form = document.getElementById('deleteConfirmationForm');
    
    // Set form action
    form.action = `/classes/delete/${classId}`;
    
    // Show modal
    modal.setAttribute('aria-hidden', 'false');
    modal.style.display = 'flex';
}

// Close delete confirmation modal
function closeDeleteModal() {
    const modal = document.getElementById('deleteConfirmationModal');
    modal.setAttribute('aria-hidden', 'true');
    modal.style.display = 'none';
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    const createModal = document.getElementById('createClassModal');
    const editModal = document.getElementById('editClassModal');
    const deleteModal = document.getElementById('deleteConfirmationModal');
    
    if (event.target === createModal) {
        closeCreateClassModal();
    }
    
    if (event.target === editModal) {
        closeEditClassModal();
    }
    
    if (event.target === deleteModal || event.target.classList.contains('close-modal')) {
        closeDeleteModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeCreateClassModal();
        closeEditClassModal();
        closeDeleteModal();
    }
});
