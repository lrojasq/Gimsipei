/**
 * Grades View - JavaScript
 * Maneja la lógica de calificaciones: cálculo automático y guardado
 */

document.addEventListener("DOMContentLoaded", function () {
  const saveBtn = document.getElementById("saveGradesBtn");
  const saveModal = document.getElementById("saveConfirmationModal");
  const successModal = document.getElementById("successModal");
  const confirmSaveBtn = document.getElementById("confirmSaveBtn");
  const successOkBtn = document.getElementById("successOkBtn");

  // Función para calcular la nota final automáticamente
  function calculateFinalGrade(gradeDiv) {
    const tasksInput = gradeDiv.querySelector('[data-field="tasks_grade"]');
    const assignmentsInput = gradeDiv.querySelector(
      '[data-field="assignments_grade"]'
    );
    const evaluationsInput = gradeDiv.querySelector(
      '[data-field="evaluations_grade"]'
    );
    const finalInput = gradeDiv.querySelector('[data-field="final_grade"]');

    const tasks = parseFloat(tasksInput.value) || 0;
    const assignments = parseFloat(assignmentsInput.value) || 0;
    const evaluations = parseFloat(evaluationsInput.value) || 0;

    // Contar cuántos valores hay para el promedio
    let count = 0;
    let sum = 0;

    if (tasksInput.value.trim() !== "") {
      sum += tasks;
      count++;
    }
    if (assignmentsInput.value.trim() !== "") {
      sum += assignments;
      count++;
    }
    if (evaluationsInput.value.trim() !== "") {
      sum += evaluations;
      count++;
    }

    if (count > 0) {
      const average = (sum / count).toFixed(1);
      finalInput.value = average;
    } else {
      finalInput.value = "";
    }
  }

  // Agregar listeners a los inputs para cálculo automático
  document.querySelectorAll(".grade[data-subject-id]").forEach((gradeDiv) => {
    const inputs = gradeDiv.querySelectorAll(".grade-input:not(.grade-final)");
    inputs.forEach((input) => {
      input.addEventListener("input", () => calculateFinalGrade(gradeDiv));
      input.addEventListener("change", () => calculateFinalGrade(gradeDiv));
    });

    // Hacer el campo de nota final readonly
    const finalInput = gradeDiv.querySelector(".grade-final");
    if (finalInput) {
      finalInput.readOnly = true;
    }

    // Recalcular la nota final al cargar la página
    calculateFinalGrade(gradeDiv);
  });

  // Abrir modal de confirmación
  if (saveBtn) {
    saveBtn.addEventListener("click", function () {
      saveModal.style.display = "flex";
    });
  }

  // Cerrar modal de confirmación
  document.querySelectorAll(".close-modal-save").forEach((el) => {
    el.addEventListener("click", function () {
      saveModal.style.display = "none";
    });
  });

  // Cerrar modal de éxito
  document.querySelectorAll(".close-modal-success").forEach((el) => {
    el.addEventListener("click", function () {
      successModal.style.display = "none";
      location.reload();
    });
  });

  if (successOkBtn) {
    successOkBtn.addEventListener("click", function () {
      successModal.style.display = "none";
      location.reload();
    });
  }

  // Confirmar guardado
  if (confirmSaveBtn) {
    confirmSaveBtn.addEventListener("click", async function () {
      const grades = [];
      const courseId = window.gradesConfig.courseId;
      const studentId = window.gradesConfig.studentId;
      const period = window.gradesConfig.period;

      // Recopilar todas las calificaciones
      document
        .querySelectorAll(".grade[data-subject-id]")
        .forEach((gradeDiv) => {
          const subjectId = gradeDiv.dataset.subjectId;
          const gradeData = {
            subject_id: parseInt(subjectId),
            period: period,
            tasks_grade: null,
            assignments_grade: null,
            evaluations_grade: null,
          };

          gradeDiv.querySelectorAll(".grade-input").forEach((input) => {
            const field = input.dataset.field;
            // Solo recopilar los 3 componentes, no el final
            if (field !== "final_grade") {
              const value = input.value.trim();
              if (value !== "") {
                gradeData[field] = parseFloat(value);
              }
            }
          });

          grades.push(gradeData);
        });

      // Mostrar spinner
      confirmSaveBtn.disabled = true;
      confirmSaveBtn.querySelector(".btn-text").style.display = "none";
      confirmSaveBtn.querySelector(".btn-spinner").style.display = "inline";

      try {
        for (const grade of grades) {
          const response = await fetch(
            `/grades/api/course/${courseId}/student/${studentId}/subject/${grade.subject_id}`,
            {
              method: "PUT",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                period: grade.period,
                tasks_grade: grade.tasks_grade,
                assignments_grade: grade.assignments_grade,
                evaluations_grade: grade.evaluations_grade,
              }),
            }
          );

          if (!response.ok) {
            throw new Error("Error al guardar calificaciones");
          }
        }

        // Cerrar modal de confirmación y mostrar modal de éxito
        saveModal.style.display = "none";
        successModal.style.display = "flex";
      } catch (error) {
        console.error("Error:", error);
        alert("Error al guardar las calificaciones");
      } finally {
        confirmSaveBtn.disabled = false;
        confirmSaveBtn.querySelector(".btn-text").style.display = "inline";
        confirmSaveBtn.querySelector(".btn-spinner").style.display = "none";
      }
    });
  }
});
