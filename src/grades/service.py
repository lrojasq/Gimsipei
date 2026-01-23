from typing import List, Optional, Tuple

from ..database.database import SessionLocal
from ..models.assignment import Assignment
from ..models.assignment_submission import AssignmentSubmission
from ..models.class_model import ClassModel
from ..models.course import Course
from ..models.course_student import CourseStudent
from ..models.course_subject import CourseSubject
from ..models.evaluation import Evaluation
from ..models.evaluation_submission import EvaluationSubmission
from ..models.grade import Grade
from ..models.subject import Subject
from ..models.user import User
from src.courses.service import COURSE_NAME_ORDER


def grade_to_dict(grade: Grade) -> dict:
    """Convertir objeto Grade a diccionario"""
    return {
        "id": grade.id,
        "student_id": grade.student_id,
        "course_id": grade.course_id,
        "subject_id": grade.subject_id,
        "period": grade.period,
        "tasks_grade": grade.tasks_grade,
        "assignments_grade": grade.assignments_grade,
        "evaluations_grade": grade.evaluations_grade,
        "final_grade": grade.final_grade,
    }


def get_courses_with_students_service(
    teacher_id: int,
) -> Tuple[Optional[List[dict]], int]:
    """
    Obtener todos los cursos del sistema junto con los estudiantes de cada curso.
    Para profesores, muestra todos los cursos existentes.
    """
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        if not courses:
            return [], 200
        result = []
        for course in courses:
            # Obtener estudiantes del curso
            enrollments = (
                db.query(CourseStudent)
                .filter(CourseStudent.course_id == course.id)
                .all()
            )

            students = []
            for enrollment in enrollments:
                student = (
                    db.query(User).filter(User.id == enrollment.student_id).first()
                )
                if student:
                    students.append(
                        {
                            "id": student.id,
                            "full_name": student.full_name,
                            "document": student.document,
                        }
                    )

            result.append(
                {
                    "id": course.id,
                    "name": course.name,
                    "academic_year": course.academic_year,
                    "students": students,
                }
            )
        # Ordenar los cursos
        result.sort(key=lambda c: COURSE_NAME_ORDER.get(c["name"], 999))
        return result, 200
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"error": f"Error al obtener cursos: {str(e)}"}, 500
    finally:
        db.close()


def get_student_grades_service(
    student_id: int, course_id: int, period: Optional[int] = None
) -> Tuple[Optional[dict], int]:
    """
    Obtener las calificaciones de un estudiante en un curso,
    organizadas por materia y periodo.
    También calcula las calificaciones basándose en evaluaciones y tareas.
    """
    db = SessionLocal()
    try:
        # Verificar que el estudiante existe y está inscrito en el curso
        enrollment = (
            db.query(CourseStudent)
            .filter(CourseStudent.student_id == student_id)
            .filter(CourseStudent.course_id == course_id)
            .first()
        )

        if not enrollment:
            return {"error": "Estudiante no inscrito en el curso"}, 404

        student = db.query(User).filter(User.id == student_id).first()
        course = db.query(Course).filter(Course.id == course_id).first()

        if not student or not course:
            return {"error": "Estudiante o curso no encontrado"}, 404

        # Obtener las materias del curso
        course_subjects = (
            db.query(CourseSubject)
            .filter(CourseSubject.course_id == course_id)
            .filter(CourseSubject.is_active.is_(True))
            .all()
        )

        subjects_grades = []
        for cs in course_subjects:
            subject = db.query(Subject).filter(Subject.id == cs.subject_id).first()
            if not subject:
                continue

            subject_data = {"id": subject.id, "name": subject.name, "periods": {}}

            # Obtener calificaciones para cada periodo (1-4)
            periods_to_check = [period] if period else [1, 2, 3, 4]

            for p in periods_to_check:
                # Buscar calificación existente
                grade = (
                    db.query(Grade)
                    .filter(Grade.student_id == student_id)
                    .filter(Grade.course_id == course_id)
                    .filter(Grade.subject_id == subject.id)
                    .filter(Grade.period == p)
                    .first()
                )

                # Calcular calificación de evaluaciones para este periodo
                eval_grade = calculate_evaluation_grade(
                    db, student_id, course_id, subject.id, p
                )

                # Calcular calificación de tareas para este periodo
                task_grade = calculate_task_grade(
                    db, student_id, course_id, subject.id, p
                )

                if grade:
                    subject_data["periods"][p] = {
                        "tasks_grade": grade.tasks_grade or task_grade,
                        "assignments_grade": grade.assignments_grade,
                        "evaluations_grade": grade.evaluations_grade or eval_grade,
                        "final_grade": grade.final_grade,
                        "calculated_eval_grade": eval_grade,
                        "calculated_task_grade": task_grade,
                    }
                else:
                    # Crear registro de calificación si hay datos calculados
                    final = None
                    if eval_grade is not None or task_grade is not None:
                        grades_list = [
                            g for g in [eval_grade, task_grade] if g is not None
                        ]
                        final = (
                            sum(grades_list) / len(grades_list) if grades_list else None
                        )

                    subject_data["periods"][p] = {
                        "tasks_grade": task_grade,
                        "assignments_grade": None,
                        "evaluations_grade": eval_grade,
                        "final_grade": final,
                        "calculated_eval_grade": eval_grade,
                        "calculated_task_grade": task_grade,
                    }

            subjects_grades.append(subject_data)

        result = {
            "student": {
                "id": student.id,
                "full_name": student.full_name,
                "document": student.document,
            },
            "course": {
                "id": course.id,
                "name": course.name,
            },
            "subjects": subjects_grades,
        }

        return result, 200
    except Exception as e:
        return {"error": f"Error al obtener calificaciones: {str(e)}"}, 500
    finally:
        db.close()


def get_student_global_grades_service(
    student_id: int, course_id: int
) -> Tuple[Optional[dict], int]:
    """
    Obtener las calificaciones globales de un estudiante en un curso,
    mostrando todas las materias con sus notas por periodo y nota global.
    """
    db = SessionLocal()
    try:
        # Verificar que el estudiante existe y está inscrito en el curso
        enrollment = (
            db.query(CourseStudent)
            .filter(CourseStudent.student_id == student_id)
            .filter(CourseStudent.course_id == course_id)
            .first()
        )

        if not enrollment:
            return {"error": "Estudiante no inscrito en el curso"}, 404

        student = db.query(User).filter(User.id == student_id).first()
        course = db.query(Course).filter(Course.id == course_id).first()

        if not student or not course:
            return {"error": "Estudiante o curso no encontrado"}, 404

        # Obtener las materias del curso
        course_subjects = (
            db.query(CourseSubject)
            .filter(CourseSubject.course_id == course_id)
            .filter(CourseSubject.is_active.is_(True))
            .all()
        )

        subjects_global = []
        for cs in course_subjects:
            subject = db.query(Subject).filter(Subject.id == cs.subject_id).first()
            if not subject:
                continue

            subject_data = {
                "id": subject.id,
                "name": subject.name,
                "period_1": None,
                "period_2": None,
                "period_3": None,
                "period_4": None,
                "global_grade": None,
            }

            period_grades = []
            for p in [1, 2, 3, 4]:
                # Buscar calificación existente
                grade = (
                    db.query(Grade)
                    .filter(Grade.student_id == student_id)
                    .filter(Grade.course_id == course_id)
                    .filter(Grade.subject_id == subject.id)
                    .filter(Grade.period == p)
                    .first()
                )

                if grade and grade.final_grade is not None:
                    subject_data[f"period_{p}"] = grade.final_grade
                    period_grades.append(grade.final_grade)
                else:
                    # Calcular basado en evaluaciones y tareas
                    eval_grade = calculate_evaluation_grade(
                        db, student_id, course_id, subject.id, p
                    )
                    task_grade = calculate_task_grade(
                        db, student_id, course_id, subject.id, p
                    )

                    grades_list = [g for g in [eval_grade, task_grade] if g is not None]
                    if grades_list:
                        final = sum(grades_list) / len(grades_list)
                        subject_data[f"period_{p}"] = round(final, 1)
                        period_grades.append(final)

            # Calcular nota global (promedio de los periodos)
            if period_grades:
                subject_data["global_grade"] = round(
                    sum(period_grades) / len(period_grades), 1
                )

            subjects_global.append(subject_data)

        result = {
            "student": {
                "id": student.id,
                "full_name": student.full_name,
                "document": student.document,
            },
            "course": {
                "id": course.id,
                "name": course.name,
            },
            "subjects": subjects_global,
        }

        return result, 200
    except Exception as e:
        return {"error": f"Error al obtener calificaciones globales: {str(e)}"}, 500
    finally:
        db.close()


def calculate_evaluation_grade(
    db, student_id: int, course_id: int, subject_id: int, period: int
) -> Optional[float]:
    """Calcular la calificación promedio de evaluaciones para un periodo"""
    try:
        # Obtener evaluaciones del periodo
        evaluations = (
            db.query(Evaluation)
            .filter(Evaluation.course_id == course_id)
            .filter(Evaluation.subject_id == subject_id)
            .filter(Evaluation.period == period)
            .all()
        )

        if not evaluations:
            return None

        scores = []
        for evaluation in evaluations:
            submission = (
                db.query(EvaluationSubmission)
                .filter(EvaluationSubmission.evaluation_id == evaluation.id)
                .filter(EvaluationSubmission.student_id == student_id)
                .filter(EvaluationSubmission.is_completed.is_(True))
                .first()
            )
            if submission and submission.score is not None:
                scores.append(submission.score)

        if scores:
            return round(sum(scores) / len(scores), 1)
        return None
    except Exception:
        return None


def calculate_task_grade(
    db, student_id: int, course_id: int, subject_id: int, period: int
) -> Optional[float]:
    """Calcular la calificación promedio de tareas para un periodo"""
    try:
        # Obtener clases del curso, materia y periodo
        classes = (
            db.query(ClassModel)
            .filter(ClassModel.course_id == course_id)
            .filter(ClassModel.subject_id == subject_id)
            .filter(ClassModel.period == period)
            .all()
        )

        if not classes:
            return None

        # Obtener todas las tareas de esas clases
        class_ids = [c.id for c in classes]
        assignments = (
            db.query(Assignment)
            .filter(Assignment.class_id.in_(class_ids))
            .filter(Assignment.is_active.is_(True))
            .all()
        )

        if not assignments:
            return None

        scores = []
        for assignment in assignments:
            submission = (
                db.query(AssignmentSubmission)
                .filter(AssignmentSubmission.assignment_id == assignment.id)
                .filter(AssignmentSubmission.student_id == student_id)
                .first()
            )
            if submission and submission.score is not None:
                # Normalizar la calificación a escala de 0-5
                normalized_score = (
                    submission.score / (assignment.max_score or 100)
                ) * 5
                scores.append(normalized_score)

        if scores:
            return round(sum(scores) / len(scores), 1)
        return None
    except Exception:
        return None


def calculate_final_from_components(
    tasks_grade: Optional[float],
    assignments_grade: Optional[float],
    evaluations_grade: Optional[float],
) -> Optional[float]:
    """
    Calcular la nota final basándose en los 3 componentes.
    Fórmula: (tareas + trabajos + evaluaciones) / cantidad_de_componentes_con_valor
    """
    grades = []
    if tasks_grade is not None:
        grades.append(tasks_grade)
    if assignments_grade is not None:
        grades.append(assignments_grade)
    if evaluations_grade is not None:
        grades.append(evaluations_grade)

    if grades:
        return round(sum(grades) / len(grades), 1)
    return None


def update_grade_service(
    student_id: int, course_id: int, subject_id: int, period: int, data: dict
) -> Tuple[Optional[dict], int]:
    """
    Actualizar o crear una calificación.
    El final_grade SIEMPRE se calcula automáticamente basándose en los 3 componentes.
    """
    db = SessionLocal()
    try:
        # Buscar calificación existente
        grade = (
            db.query(Grade)
            .filter(Grade.student_id == student_id)
            .filter(Grade.course_id == course_id)
            .filter(Grade.subject_id == subject_id)
            .filter(Grade.period == period)
            .first()
        )

        # Obtener valores de los componentes
        tasks = None
        assignments = None
        evaluations = None

        if grade:
            # Actualizar calificación existente - partir de valores actuales
            tasks = grade.tasks_grade
            assignments = grade.assignments_grade
            evaluations = grade.evaluations_grade

            # Actualizar con los nuevos valores que vengan en data
            if "tasks_grade" in data and data["tasks_grade"] is not None:
                tasks = float(data["tasks_grade"])
                grade.tasks_grade = tasks
            if "assignments_grade" in data and data["assignments_grade"] is not None:
                assignments = float(data["assignments_grade"])
                grade.assignments_grade = assignments
            if "evaluations_grade" in data and data["evaluations_grade"] is not None:
                evaluations = float(data["evaluations_grade"])
                grade.evaluations_grade = evaluations

            # Calcular final_grade automáticamente
            grade.final_grade = calculate_final_from_components(
                tasks, assignments, evaluations
            )
        else:
            # Crear nueva calificación
            tasks = float(data.get("tasks_grade")) if data.get("tasks_grade") else None
            assignments = (
                float(data.get("assignments_grade"))
                if data.get("assignments_grade")
                else None
            )
            evaluations = (
                float(data.get("evaluations_grade"))
                if data.get("evaluations_grade")
                else None
            )

            # Calcular final_grade automáticamente
            final = calculate_final_from_components(tasks, assignments, evaluations)

            grade = Grade(
                student_id=student_id,
                course_id=course_id,
                subject_id=subject_id,
                period=period,
                tasks_grade=tasks,
                assignments_grade=assignments,
                evaluations_grade=evaluations,
                final_grade=final,
            )
            db.add(grade)

        db.commit()
        db.refresh(grade)

        return {
            "message": "Calificación actualizada exitosamente",
            "grade": grade_to_dict(grade),
        }, 200
    except Exception as e:
        db.rollback()
        return {"error": f"Error al actualizar calificación: {str(e)}"}, 500
    finally:
        db.close()


def calculate_final_grade_service(
    student_id: int, course_id: int, subject_id: int, period: int
) -> Tuple[Optional[dict], int]:
    """Calcular y guardar la nota final del periodo"""
    db = SessionLocal()
    try:
        # Buscar calificación existente
        grade = (
            db.query(Grade)
            .filter(Grade.student_id == student_id)
            .filter(Grade.course_id == course_id)
            .filter(Grade.subject_id == subject_id)
            .filter(Grade.period == period)
            .first()
        )

        # Calcular componentes
        eval_grade = calculate_evaluation_grade(
            db, student_id, course_id, subject_id, period
        )
        task_grade = calculate_task_grade(db, student_id, course_id, subject_id, period)

        grades_to_avg = []
        if eval_grade is not None:
            grades_to_avg.append(eval_grade)
        if task_grade is not None:
            grades_to_avg.append(task_grade)
        if grade and grade.assignments_grade is not None:
            grades_to_avg.append(grade.assignments_grade)

        final_grade = None
        if grades_to_avg:
            final_grade = round(sum(grades_to_avg) / len(grades_to_avg), 1)

        if grade:
            grade.evaluations_grade = eval_grade
            grade.tasks_grade = task_grade
            grade.final_grade = final_grade
        else:
            grade = Grade(
                student_id=student_id,
                course_id=course_id,
                subject_id=subject_id,
                period=period,
                tasks_grade=task_grade,
                evaluations_grade=eval_grade,
                final_grade=final_grade,
            )
            db.add(grade)

        db.commit()
        db.refresh(grade)

        return {
            "message": "Nota final calculada exitosamente",
            "grade": grade_to_dict(grade),
        }, 200
    except Exception as e:
        db.rollback()
        return {"error": f"Error al calcular nota final: {str(e)}"}, 500
    finally:
        db.close()
