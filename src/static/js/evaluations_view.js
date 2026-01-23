// Evaluations View JavaScript - Similar to classes_resources.js

document.addEventListener('DOMContentLoaded', function() {
    // Expand/collapse course rows
    const expandButtons = document.querySelectorAll('.expand-btn');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const expandableRow = document.querySelector(`.expandable-row[data-course-id="${courseId}"]`);
            const icon = this.querySelector('i');
            
            if (expandableRow) {
                if (expandableRow.style.display === 'none') {
                    if(window.screen.width < 768) {
                        expandableRow.style.display = 'table-row';
                    } else {
                        expandableRow.style.display = 'flex';
                    }
                   
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                    this.closest('.course-row').classList.add('expanded');
                } else {
                    expandableRow.style.display = 'none';
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                    this.closest('.course-row').classList.remove('expanded');
                }
            }
        });
    });
});

