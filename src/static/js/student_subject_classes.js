/**
 * Student Subject Classes View
 * Maneja la funcionalidad de cambio entre periodos y marcado de clases como vistas
 */

document.addEventListener('DOMContentLoaded', function () {
    const periodButtons = document.querySelectorAll('.period-btn');
    const periodContainers = document.querySelectorAll('.period-classes-container');

    // Cambio entre períodos
    periodButtons.forEach(button => {
        button.addEventListener('click', function () {
            const period = this.getAttribute('data-period');

            // Actualizar botones activos
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Mostrar/ocultar contenedores de periodo con animación
            periodContainers.forEach(container => {
                if (container.getAttribute('data-period') === period) {
                    container.style.display = 'flex';
                    // Trigger reflow para que la animación funcione
                    void container.offsetWidth;
                } else {
                    container.style.display = 'none';
                }
            });
        });
    });

    // Botones de marcar como vista/no vista
    const viewedButtons = document.querySelectorAll('.btn-mark-viewed');
    const notViewedButtons = document.querySelectorAll('.btn-mark-not-viewed');

    // Marcar como vista
    viewedButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation();
            const classId = this.getAttribute('data-class-id');
            const classCard = this.closest('.exam.class');
            
            // Marcar como vista en el servidor
            markClassAsViewed(classId, true, classCard);
        });
    });

    // Marcar como no vista
    notViewedButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation();
            const classId = this.getAttribute('data-class-id');
            const classCard = this.closest('.exam.class');
            
            // Marcar como no vista en el servidor
            markClassAsViewed(classId, false, classCard);
        });
    });

    /**
     * Marca una clase como vista o no vista
     * @param {string} classId - ID de la clase
     * @param {boolean} viewed - true si se marca como vista, false si no
     * @param {HTMLElement} classCard - Elemento de la card de la clase
     */
    function markClassAsViewed(classId, viewed, classCard) {
        const courseId = document.querySelector('.student-subject-view').getAttribute('data-course-id');
        const subjectId = document.querySelector('.student-subject-view').getAttribute('data-subject-id');

        // Deshabilitar botones mientras se procesa
        const viewedBtn = classCard.querySelector('.btn-mark-viewed');
        const notViewedBtn = classCard.querySelector('.btn-mark-not-viewed');
        viewedBtn.disabled = true;
        notViewedBtn.disabled = true;

        fetch(`/classes/student/mark-viewed`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                class_id: parseInt(classId),
                course_id: parseInt(courseId),
                subject_id: parseInt(subjectId),
                viewed: viewed
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Actualizar los botones
                if (viewed) {
                    viewedBtn.classList.add('active');
                    notViewedBtn.classList.remove('active');
                } else {
                    viewedBtn.classList.remove('active');
                    notViewedBtn.classList.add('active');
                }

                // Actualizar la barra de progreso
                updateProgressBar();
            } else {
                alert('Error al actualizar el estado de la clase: ' + (data.error || 'Error desconocido'));
            }
        })
        .catch(error => {
            alert('Error al conectar con el servidor. Por favor, verifica tu conexión.');
        })
        .finally(() => {
            // Rehabilitar botones
            viewedBtn.disabled = false;
            notViewedBtn.disabled = false;
        });
    }

    /**
     * Actualiza la barra de progreso de clases vistas
     */
    function updateProgressBar() {
        const courseId = document.querySelector('.student-subject-view').getAttribute('data-course-id');
        const subjectId = document.querySelector('.student-subject-view').getAttribute('data-subject-id');

        fetch(`/classes/student/progress/${courseId}/${subjectId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const progressBar = document.querySelector('.progress-bar-fill');
                    const progressText = document.querySelector('.progress-text');
                    
                    if (progressBar) {
                        progressBar.style.width = data.percentage + '%';
                    }
                    
                    if (progressText) {
                        progressText.textContent = `${data.viewed} de ${data.total} clases vistas`;
                    }
                }
            })
            .catch(error => {
                // Error silencioso - no mostrar al usuario
            });
    }
});
