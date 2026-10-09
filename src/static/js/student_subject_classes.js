/**
 * Student Subject Classes View
 * Maneja la funcionalidad de cambio entre periodos y marcado de clases como vistas
 */

document.addEventListener('DOMContentLoaded', function () {
    // Al volver con "Atrás" (bfcache), refrescar solo progreso + estados sin recargar la página completa.
    window.addEventListener('pageshow', function (event) {
        const navEntry = performance.getEntriesByType && performance.getEntriesByType('navigation')
            ? performance.getEntriesByType('navigation')[0]
            : null;
        const isBackForward = event.persisted || (navEntry && navEntry.type === 'back_forward');
        if (isBackForward) {
            refreshViewedState();
        }
    });

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

                // Mantener UI siempre sincronizada: refrescar progreso + ids vistos (sin recargar página)
                refreshViewedState();
            } else {
                // Error silencioso - no mostrar al usuario
            }
        })
        .catch(error => {
            // Error silencioso - no mostrar al usuario
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
                    document.querySelectorAll('.progress-bar-fill').forEach(progressBar => {
                        progressBar.style.width = data.percentage + '%';
                    });

                    document.querySelectorAll('.progress-text').forEach(progressText => {
                        progressText.textContent = `${data.viewed} de ${data.total} clases vistas`;
                    });
                }
            })
            .catch(error => {
                // Error silencioso - no mostrar al usuario
            });
    }

    /**
     * Refresca estados de botones (vista/no vista) y la barra de progreso sin recargar toda la página.
     */
    function refreshViewedState() {
        const root = document.querySelector('.student-subject-view');
        if (!root) return;

        const courseId = root.getAttribute('data-course-id');
        const subjectId = root.getAttribute('data-subject-id');
        if (!courseId || !subjectId) return;

        // Actualizar barra (conteo + %)
        updateProgressBar();

        // Actualizar íconos por clase
        fetch(`/classes/student/viewed-classes/${courseId}/${subjectId}`)
            .then(r => r.json())
            .then(data => {
                if (!data || !data.success) return;
                const viewedSet = new Set((data.viewed_class_ids || []).map(String));

                document.querySelectorAll('.exam.class').forEach(card => {
                    const classId = card.getAttribute('data-class-id');
                    const viewedBtn = card.querySelector('.btn-mark-viewed');
                    const notViewedBtn = card.querySelector('.btn-mark-not-viewed');
                    if (!classId || !viewedBtn || !notViewedBtn) return;

                    if (viewedSet.has(String(classId))) {
                        viewedBtn.classList.add('active');
                        notViewedBtn.classList.remove('active');
                    } else {
                        viewedBtn.classList.remove('active');
                        notViewedBtn.classList.add('active');
                    }
                });
            })
            .catch(() => {
                // Error silencioso
            });
    }
});
