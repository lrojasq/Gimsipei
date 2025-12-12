// Subject Evaluations JavaScript - Similar to subject_classes.js

document.addEventListener('DOMContentLoaded', function() {
    // Get course and subject IDs from data attributes
    const container = document.querySelector('.container_category');
    const courseId = container ? container.getAttribute('data-course-id') : null;
    const subjectId = container ? container.getAttribute('data-subject-id') : null;
    
    // Set course and subject IDs for modals
    if (courseId && subjectId) {
        const evaluationCourseIdInput = document.getElementById('evaluation_course_id');
        const evaluationSubjectIdInput = document.getElementById('evaluation_subject_id');
        
        if (evaluationCourseIdInput) evaluationCourseIdInput.value = courseId;
        if (evaluationSubjectIdInput) evaluationSubjectIdInput.value = subjectId;
    }
    
    // Period filter functionality
    const periodButtons = document.querySelectorAll('.period-btn');
    const periodContainers = document.querySelectorAll('.period-evaluations-container');
    const evaluationPeriodSelect = document.getElementById('evaluation_period');
    
    periodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            
            // Update active button
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding period container
            periodContainers.forEach(container => {
                if (container.getAttribute('data-period') === period) {
                    container.style.display = 'flex';
                } else {
                    container.style.display = 'none';
                }
            });
            
            // Update hidden input for creating evaluations
            if (evaluationPeriodSelect) {
                evaluationPeriodSelect.value = period;
            }
        });
    });
    
    // Add evaluation button
    const addEvaluationBtn = document.getElementById('addEvaluationBtn');
    const addFirstEvaluationBtns = document.querySelectorAll('.btn-add-first-evaluation');
    
    if (addEvaluationBtn) {
        addEvaluationBtn.addEventListener('click', function() {
            openCreateEvaluationModal();
        });
    }
    
    addFirstEvaluationBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.getAttribute('data-period');
            openCreateEvaluationModal(period);
        });
    });
    
    // Edit evaluation buttons
    const editButtons = document.querySelectorAll('.btn-edit-evaluation');
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const evaluationId = this.getAttribute('data-evaluation-id');
            openEditEvaluationModal(evaluationId);
        });
    });
    
    // Initialize delete evaluation buttons using delete_modal.js
    initializeDeleteButtons('.open-delete-evaluation-modal', function(button) {
        const evaluationId = button.getAttribute('data-evaluation-id');
        return `/evaluations/${evaluationId}/delete`;
    });
    
    // File upload display for create modal
    const fileInput = document.getElementById('evaluation_cover');
    const fileName = document.getElementById('evaluation_cover_name');
    
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
    const editFileInput = document.getElementById('edit_evaluation_cover');
    const editFileName = document.getElementById('edit_evaluation_cover_name');
    
    if (editFileInput) {
        editFileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                editFileName.textContent = this.files[0].name;
            } else {
                editFileName.textContent = '';
            }
        });
    }
    
    // initializeDeleteModalListeners() ya se llama automáticamente en delete_modal.js
    
    // Initialize loading states for forms
    initializeLoadingStates();

    // ---------- Builder de preguntas para crear evaluación ----------
    const questionsContainer = document.getElementById('questionsContainer');
    const addQuestionBtn = document.getElementById('addQuestionBtn');
    const createForm = document.getElementById('createEvaluationForm');

    const MAX_QUESTIONS = 10;
    const MIN_QUESTIONS = 2;
    const MAX_OPTIONS = 4;
    let currentQuestionIndex = 0;

    const questionsNav = document.getElementById('questionsNavigation');
    const prevQuestionBtn = document.getElementById('prevQuestionBtn');
    const nextQuestionBtn = document.getElementById('nextQuestionBtn');
    const questionsStepLabel = document.getElementById('questionsStepLabel');

    function createQuestionItem(index) {
        if (!questionsContainer) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'question-item';
        wrapper.dataset.index = String(index);
        wrapper.style.border = '1px solid #eee';
        wrapper.style.borderRadius = '8px';
        wrapper.style.padding = '0.75rem 0.75rem 0.5rem';
        wrapper.style.marginBottom = '0.5rem';

        wrapper.innerHTML = `
            <div class="question-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                <span style="font-weight:600;font-size:0.9rem;">Pregunta ${index + 1}</span>
                <button type="button" class="question-remove" style="border:none;background:transparent;color:#999;font-size:1.1rem;cursor:pointer;">&times;</button>
            </div>
            <div class="form-group">
                <input type="text" class="question-text" placeholder="Escribe la pregunta">
            </div>
            <div class="form-group">
                <select class="question-type">
                    <option value="open">Respuesta abierta</option>
                    <option value="multi">Opción múltiple</option>
                </select>
            </div>
            <div class="question-options" style="display:none;">
                <div class="options-list"></div>
                <button type="button" class="add-option-btn btn-submit" style="margin-top:0.25rem;background:transparent;color:var(--evaluaciones);border:1px dashed var(--evaluaciones);padding:0.3rem 0.8rem;border-radius:999px;">
                    + Añadir opción
                </button>
                <div class="form-group" style="margin-top:0.5rem;">
                    <select class="question-answer">
                        <option value="">Seleccione la respuesta correcta</option>
                    </select>
                </div>
            </div>
        `;

        const removeBtn = wrapper.querySelector('.question-remove');
        removeBtn.addEventListener('click', () => {
            wrapper.remove();
            // Re-enumerar etiquetas
            document.querySelectorAll('#questionsContainer .question-item').forEach((item, idx) => {
                item.dataset.index = String(idx);
                const label = item.querySelector('.question-header span');
                if (label) label.textContent = `Pregunta ${idx + 1}`;
            });
            const total = document.querySelectorAll('#questionsContainer .question-item').length;
            if (currentQuestionIndex >= total) {
                currentQuestionIndex = Math.max(0, total - 1);
            }
            updateQuestionStepUI();
        });

        const typeSelect = wrapper.querySelector('.question-type');
        const optionsBlock = wrapper.querySelector('.question-options');
        const addOptionBtn = wrapper.querySelector('.add-option-btn');
        const optionsList = wrapper.querySelector('.options-list');
        const answerSelect = wrapper.querySelector('.question-answer');

        typeSelect.addEventListener('change', () => {
            if (typeSelect.value === 'multi') {
                optionsBlock.style.display = 'block';
            } else {
                optionsBlock.style.display = 'none';
                optionsList.innerHTML = '';
                answerSelect.innerHTML = '<option value=\"\">Seleccione la respuesta correcta</option>';
            }
        });

        addOptionBtn.addEventListener('click', () => {
            const currentOptions = optionsList.querySelectorAll('.option-item').length;
            if (currentOptions >= MAX_OPTIONS) {
                alert(`Cada pregunta de opción múltiple puede tener máximo ${MAX_OPTIONS} opciones.`);
                return;
            }
            const optionWrapper = document.createElement('div');
            optionWrapper.className = 'option-item';
            optionWrapper.style.display = 'flex';
            optionWrapper.style.alignItems = 'center';
            optionWrapper.style.marginBottom = '0.25rem';

            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'option-text';
            input.placeholder = 'Texto de la opción';
            input.style.flex = '1';
            input.style.marginRight = '0.25rem';

            const removeOptionBtn = document.createElement('button');
            removeOptionBtn.type = 'button';
            removeOptionBtn.textContent = '×';
            removeOptionBtn.style.border = 'none';
            removeOptionBtn.style.background = 'transparent';
            removeOptionBtn.style.color = '#999';
            removeOptionBtn.style.cursor = 'pointer';
            removeOptionBtn.style.fontSize = '1rem';

            removeOptionBtn.addEventListener('click', () => {
                optionWrapper.remove();
                rebuildAnswerOptions();
            });

            optionWrapper.appendChild(input);
            optionWrapper.appendChild(removeOptionBtn);
            optionsList.appendChild(optionWrapper);

            rebuildAnswerOptions();

            function rebuildAnswerOptions() {
                const optionInputs = optionsList.querySelectorAll('.option-text');
                answerSelect.innerHTML = '<option value=\"\">Seleccione la respuesta correcta</option>';
                optionInputs.forEach((optInput, idx) => {
                    const opt = document.createElement('option');
                    opt.value = String(idx);
                    opt.textContent = `Opción ${idx + 1}`;
                    answerSelect.appendChild(opt);
                });
            }
        });

        questionsContainer.appendChild(wrapper);
        updateQuestionStepUI();
    }

    function updateQuestionStepUI() {
        if (!questionsContainer) return;
        const items = questionsContainer.querySelectorAll('.question-item');
        const total = items.length;

        if (!questionsNav) return;

        if (total === 0) {
            questionsNav.style.display = 'none';
            return;
        }

        if (currentQuestionIndex >= total) {
            currentQuestionIndex = total - 1;
        }

        items.forEach((item, idx) => {
            item.style.display = idx === currentQuestionIndex ? 'block' : 'none';
        });

        questionsNav.style.display = 'flex';

        if (questionsStepLabel) {
            questionsStepLabel.textContent = `Pregunta ${currentQuestionIndex + 1} de ${total}`;
        }

        if (prevQuestionBtn && nextQuestionBtn) {
            prevQuestionBtn.disabled = currentQuestionIndex === 0;
            nextQuestionBtn.disabled = currentQuestionIndex === total - 1;
        }
    }

    if (addQuestionBtn && questionsContainer) {
        addQuestionBtn.addEventListener('click', () => {
            const current = questionsContainer.querySelectorAll('.question-item').length;
            if (current >= MAX_QUESTIONS) {
                alert(`Solo puedes crear hasta ${MAX_QUESTIONS} preguntas.`);
                return;
            }
            createQuestionItem(current);
            currentQuestionIndex = current; // ir a la nueva pregunta
            updateQuestionStepUI();
        });
    }

    if (prevQuestionBtn) {
        prevQuestionBtn.addEventListener('click', () => {
            const total = questionsContainer ? questionsContainer.querySelectorAll('.question-item').length : 0;
            if (total === 0) return;
            if (currentQuestionIndex > 0) {
                currentQuestionIndex -= 1;
                updateQuestionStepUI();
            }
        });
    }

    if (nextQuestionBtn) {
        nextQuestionBtn.addEventListener('click', () => {
            const total = questionsContainer ? questionsContainer.querySelectorAll('.question-item').length : 0;
            if (total === 0) return;
            if (currentQuestionIndex < total - 1) {
                currentQuestionIndex += 1;
                updateQuestionStepUI();
            }
        });
    }

    // Antes de enviar el formulario, validar y serializar preguntas a JSON
    if (createForm) {
        createForm.addEventListener('submit', function (e) {
            const items = document.querySelectorAll('#questionsContainer .question-item');
            const questions = [];
            const errors = [];

            items.forEach((item, idx) => {
                const textInput = item.querySelector('.question-text');
                const typeSelect = item.querySelector('.question-type');
                const optionsList = item.querySelectorAll('.option-text');
                const answerSelect = item.querySelector('.question-answer');

                const text = textInput ? textInput.value.trim() : '';
                const qtype = typeSelect ? typeSelect.value : 'open';

                if (!text) {
                    return; // ignorar preguntas vacías
                }

                const q = {
                    text: text,
                    type: qtype,
                    options: {},
                    answer: ''
                };

                if (qtype === 'multi') {
                    const optionValues = [];
                    optionsList.forEach((optInput) => {
                        const val = optInput.value.trim();
                        if (val) optionValues.push(val);
                    });

                    if (optionValues.length < 2) {
                        errors.push(`La pregunta ${idx + 1} debe tener al menos 2 opciones.`);
                    }
                    if (optionValues.length > MAX_OPTIONS) {
                        errors.push(`La pregunta ${idx + 1} no puede tener más de ${MAX_OPTIONS} opciones.`);
                    }

                    const answerIndex = answerSelect && answerSelect.value !== '' ? parseInt(answerSelect.value, 10) : -1;
                    if (answerIndex < 0 || answerIndex >= optionValues.length) {
                        errors.push(`La pregunta ${idx + 1} de opción múltiple debe tener una respuesta correcta seleccionada.`);
                    }

                    optionValues.forEach((val, index) => {
                        const letter = String.fromCharCode(65 + index); // A, B, C...
                        q.options[letter] = val;
                        if (index === answerIndex) {
                            q.answer = letter;
                        }
                    });
                }

                questions.push(q);
            });

            if (questions.length < MIN_QUESTIONS) {
                errors.push(`La evaluación debe tener al menos ${MIN_QUESTIONS} preguntas.`);
            }

            if (errors.length > 0) {
                // Mostrar errores sin dejar el botón en estado de carga
                alert(errors.join('\n'));
                e.preventDefault();
                return;
            }

            const hidden = document.getElementById('evaluation_questions_json');
            if (hidden) {
                hidden.value = JSON.stringify(questions);
            }

            // Si todo está bien, activar estado de carga en el botón submit
            const submitBtn = this.querySelector('button[type=\"submit\"]');
            if (submitBtn) {
                showLoadingState(submitBtn, 'Guardando...');
            }
        });
    }
});

// Loading States Functions
function showLoadingState(button, loadingText = 'Procesando...') {
    if (!button) return;
    
    button.disabled = true;
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
}

function hideLoadingState(button) {
    if (!button) return;
    
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
        button.removeAttribute('data-original-text');
    }
    button.disabled = false;
}

// Initialize loading states for edit and delete forms
// (el formulario de creación maneja su propio estado de carga
//  después de validar las preguntas)
function initializeLoadingStates() {
    // Edit evaluation form
    const editForm = document.getElementById('editEvaluationForm');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn, 'Actualizando...');
            }
        });
    }
    
    // Delete confirmation form
    const deleteForm = document.getElementById('deleteConfirmationForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn, 'Eliminando...');
            }
        });
    }
}

// Open create evaluation modal
function openCreateEvaluationModal(period = null) {
    const modal = document.getElementById('createEvaluationModal');
    const evaluationPeriodSelect = document.querySelector('#createEvaluationModal select[name="period"]');
    
    // Reset form
    document.getElementById('createEvaluationForm').reset();
    document.getElementById('evaluation_cover_name').textContent = '';
    
    // Set period if provided
    if (period && evaluationPeriodSelect) {
        evaluationPeriodSelect.value = period;
    } else {
        // Use currently active period
        const activeBtn = document.querySelector('.period-btn.active');
        if (activeBtn && evaluationPeriodSelect) {
            evaluationPeriodSelect.value = activeBtn.getAttribute('data-period');
        }
    }
    
    modal.style.display = 'flex';
}

// Close create evaluation modal
function closeCreateEvaluationModal() {
    const modal = document.getElementById('createEvaluationModal');
    modal.style.display = 'none';
}

// Open edit evaluation modal
function openEditEvaluationModal(evaluationId) {
    const modal = document.getElementById('editEvaluationModal');
    const form = document.getElementById('editEvaluationForm');
    
    if (!modal || !form) {
        console.error('Edit modal or form not found');
        return;
    }
    
    // Set form action
    form.action = `/evaluations/${evaluationId}/edit`;
    
    // Get data from server
    fetch(`/evaluations/${evaluationId}/get`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error al cargar los datos de la evaluación: ' + data.error);
                return;
            }
            
            // Populate form fields
            document.getElementById('edit_evaluation_id').value = evaluationId;
            document.getElementById('edit_evaluation_title').value = data.title || '';
            document.getElementById('edit_evaluation_description').value = data.description || '';
            document.getElementById('edit_evaluation_period').value = data.period || '';
            
            // Get course_id and subject_id from page data attributes
            const container = document.querySelector('.container_category');
            const courseId = data.course_id || (container ? container.getAttribute('data-course-id') : '');
            const subjectId = data.subject_id || (container ? container.getAttribute('data-subject-id') : '');
            document.getElementById('edit_evaluation_course_id').value = courseId;
            document.getElementById('edit_evaluation_subject_id').value = subjectId;
            
            // Show current cover image if exists
            const currentCoverPreview = document.getElementById('current_evaluation_cover_preview');
            const currentCoverImage = document.getElementById('current_evaluation_cover_image');
            
            if (data.cover_image) {
                currentCoverImage.src = data.cover_image;
                currentCoverPreview.style.display = 'block';
            } else {
                currentCoverPreview.style.display = 'none';
            }
            
            // Reset file input
            document.getElementById('edit_evaluation_cover').value = '';
            document.getElementById('edit_evaluation_cover_name').textContent = '';
            
            // Show modal
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Error loading evaluation data:', error);
            alert('Error al cargar los datos de la evaluación');
        });
}

// Close edit evaluation modal
function closeEditEvaluationModal() {
    const modal = document.getElementById('editEvaluationModal');
    modal.style.display = 'none';
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    const createModal = document.getElementById('createEvaluationModal');
    const editModal = document.getElementById('editEvaluationModal');
    
    // Check if click is on modal background (not on modal content)
    if (event.target === createModal) {
        closeCreateEvaluationModal();
    }
    
    if (event.target === editModal) {
        closeEditEvaluationModal();
    }
    
    // Delete modal is handled by delete_modal.js
});

// Close modals with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeCreateEvaluationModal();
        closeEditEvaluationModal();
        // Delete modal ESC handling is done by delete_modal.js
    }
});

