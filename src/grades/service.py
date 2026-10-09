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
) -> tuple[list[dict] | None, int]:
    """
    Obtener todos los cursos del sistema junto con los estudiantes de cada curso.
    Para profesores, muestra todos los cursos existentes.

    Single-query implementation: one LEFT OUTER JOIN fetches
    (course, course_student, user) tuples, then we group by course
    in Python. Was previously 1 + N + M queries (one for the
    course list, one per course for enrollments, one per
    enrollment for the student user). With 12 courses and 100+
    enrollments that was 115+ round-trips per request.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(Course, CourseStudent, User)
            .outerjoin(CourseStudent, CourseStudent.course_id == Course.id)
            .outerjoin(User, User.id == CourseStudent.student_id)
            .order_by(Course.name.desc())
            .all()
        )

        # Preserve the course ordering from the ORDER BY above, and
        # collect one students[] per course.
        course_order: list[int] = []
        courses_by_id: dict[int, dict] = {}
        for course, _enrollment, student in rows:
            if course.id not in courses_by_id:
                course_order.append(course.id)
                courses_by_id[course.id] = {
                    "id": course.id,
                    "name": course.name,
                    "academic_year": course.academic_year,
                    "students": [],
                }
            if student is not None:
                courses_by_id[course.id]["students"].append(
                    {
                        "id": student.id,
                        "full_name": student.full_name,
                        "document": student.document,
                    }
                )

        for course in courses_by_id.values():
            course["students"].sort(key=lambda s: s["full_name"] or "")

        return [courses_by_id[cid] for cid in course_order], 200
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"error": f"Error al obtener cursos: {str(e)}"}, 500
    finally:
        db.close()


def get_student_grades_service(
    student_id: int, course_id: int, period: int | None = None
) -> tuple[dict | None, int]:
    """
    Obtener las calificaciones de un estudiante en un curso,
    organizadas por materia y periodo.
    También calcula las calificaciones basándose en evaluaciones y tareas.

    Single-query implementation: one bulk fetch replaces the previous
    N+1 (1 query for enrollment, 1 per course_subject for the
    subject, 1 per (course_subject, period) for the grade, plus
    N per evaluation and assignment via the two helpers). Was
    ~50-100 queries per request; now 4.
    """
    db = SessionLocal()
    try:
        # One query: enrollment, student, course
        row = (
            db.query(CourseStudent, User, Course)
            .join(User, User.id == CourseStudent.student_id)
            .join(Course, Course.id == CourseStudent.course_id)
            .filter(CourseStudent.student_id == student_id)
            .filter(CourseStudent.course_id == course_id)
            .first()
        )
        if not row:
            return {"error": "Estudiante no inscrito en el curso"}, 404
        _enrollment, student, course = row
        if not student or not course:
            return {"error": "Estudiante o curso no encontrado"}, 404

        # One query: course_subjects + subjects
        subject_rows = (
            db.query(Subject)
            .join(CourseSubject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.course_id == course_id)
            .filter(CourseSubject.is_active.is_(True))
            .order_by(Subject.name)
            .all()
        )
        subject_ids = [s.id for s in subject_rows]

        # One query: all grades for this (student, course) in one shot
        period_filter = [period] if period else [1, 2, 3, 4]
        grade_rows = (
            db.query(Grade)
            .filter(Grade.student_id == student_id)
            .filter(Grade.course_id == course_id)
            .filter(Grade.subject_id.in_(subject_ids))
            .filter(Grade.period.in_(period_filter))
            .all()
        )
        grades_by_subject_period: dict[tuple[int, int], Grade] = {
            (g.subject_id, g.period): g for g in grade_rows
        }

        # One query: all evaluations + submissions for (course, subject_ids, periods)
        eval_sub_rows = (
            db.query(Evaluation, EvaluationSubmission)
            .outerjoin(
                EvaluationSubmission,
                (EvaluationSubmission.evaluation_id == Evaluation.id)
                & (EvaluationSubmission.student_id == student_id)
                & EvaluationSubmission.is_completed.is_(True),
            )
            .filter(Evaluation.course_id == course_id)
            .filter(Evaluation.subject_id.in_(subject_ids))
            .filter(Evaluation.period.in_(period_filter))
            .all()
        )
        # Group by (subject_id, period): list of scores from completed submissions
        eval_scores: dict[tuple[int, int], list[float]] = {}
        for ev, sub in eval_sub_rows:
            if sub is not None and sub.score is not None:
                eval_scores.setdefault((ev.subject_id, ev.period), []).append(sub.score)

        # One query: classes + assignments + submissions for (course, subject_ids, periods)
        class_assignment_sub_rows = (
            db.query(ClassModel, Assignment, AssignmentSubmission)
            .join(Assignment, Assignment.class_id == ClassModel.id)
            .outerjoin(
                AssignmentSubmission,
                (AssignmentSubmission.assignment_id == Assignment.id)
                & (AssignmentSubmission.student_id == student_id),
            )
            .filter(ClassModel.course_id == course_id)
            .filter(ClassModel.subject_id.in_(subject_ids))
            .filter(ClassModel.period.in_(period_filter))
            .filter(Assignment.is_active.is_(True))
            .all()
        )
        # Group by (subject_id, period): list of normalized scores
        task_scores: dict[tuple[int, int], list[float]] = {}
        for _cls, asg, sub in class_assignment_sub_rows:
            if sub is not None and sub.score is not None:
                max_score = asg.max_score or 100
                normalized = (sub.score / max_score) * 5
                task_scores.setdefault((_cls.subject_id, _cls.period), []).append(
                    normalized
                )

        def avg_or_none(values: list[float]) -> float | None:
            return round(sum(values) / len(values), 1) if values else None

        # Build the response
        subjects_grades = []
        for subject in subject_rows:
            subject_data = {"id": subject.id, "name": subject.name, "periods": {}}
            for p in period_filter:
                grade = grades_by_subject_period.get((subject.id, p))
                eval_grade = avg_or_none(eval_scores.get((subject.id, p), []))
                task_grade = avg_or_none(task_scores.get((subject.id, p), []))

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

        return (
            {
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
            },
            200,
        )
    except Exception as e:
        return {"error": f"Error al obtener calificaciones: {str(e)}"}, 500
    finally:
        db.close()


def get_student_global_grades_service(
    student_id: int, course_id: int
) -> tuple[dict | None, int]:
    """
    Obtener las calificaciones globales de un estudiante en un curso,
    mostrando todas las materias con sus notas por periodo y nota global.

    Single-query implementation (5 bulk queries) — was previously
    1 + N + N*4 + N*4*(1+N) + N*4*(1+1+N) ~ 30-150 queries per
    request. Same pattern as get_student_grades_service.
    """
    db = SessionLocal()
    try:
        # 1) enrollment + student + course
        row = (
            db.query(CourseStudent, User, Course)
            .join(User, User.id == CourseStudent.student_id)
            .join(Course, Course.id == CourseStudent.course_id)
            .filter(CourseStudent.student_id == student_id)
            .filter(CourseStudent.course_id == course_id)
            .first()
        )
        if not row:
            return {"error": "Estudiante no inscrito en el curso"}, 404
        _enrollment, student, course = row
        if not student or not course:
            return {"error": "Estudiante o curso no encontrado"}, 404

        # 2) course_subjects + subjects
        subject_rows = (
            db.query(Subject)
            .join(CourseSubject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.course_id == course_id)
            .filter(CourseSubject.is_active.is_(True))
            .order_by(Subject.name)
            .all()
        )
        subject_ids = [s.id for s in subject_rows]

        # 3) all grades for the (student, course, subjects) scope
        grade_rows = (
            db.query(Grade)
            .filter(Grade.student_id == student_id)
            .filter(Grade.course_id == course_id)
            .filter(Grade.subject_id.in_(subject_ids))
            .all()
        )
        grades_by_subject_period: dict[tuple[int, int], Grade] = {
            (g.subject_id, g.period): g for g in grade_rows
        }

        # 4) evaluations + submissions (all 4 periods at once)
        eval_sub_rows = (
            db.query(Evaluation, EvaluationSubmission)
            .outerjoin(
                EvaluationSubmission,
                (EvaluationSubmission.evaluation_id == Evaluation.id)
                & (EvaluationSubmission.student_id == student_id)
                & EvaluationSubmission.is_completed.is_(True),
            )
            .filter(Evaluation.course_id == course_id)
            .filter(Evaluation.subject_id.in_(subject_ids))
            .all()
        )
        eval_scores: dict[tuple[int, int], list[float]] = {}
        for ev, sub in eval_sub_rows:
            if sub is not None and sub.score is not None:
                eval_scores.setdefault((ev.subject_id, ev.period), []).append(
                    sub.score
                )

        # 5) classes + assignments + submissions
        cas_rows = (
            db.query(ClassModel, Assignment, AssignmentSubmission)
            .join(Assignment, Assignment.class_id == ClassModel.id)
            .outerjoin(
                AssignmentSubmission,
                (AssignmentSubmission.assignment_id == Assignment.id)
                & (AssignmentSubmission.student_id == student_id),
            )
            .filter(ClassModel.course_id == course_id)
            .filter(ClassModel.subject_id.in_(subject_ids))
            .filter(Assignment.is_active.is_(True))
            .all()
        )
        task_scores: dict[tuple[int, int], list[float]] = {}
        for _cls, asg, sub in cas_rows:
            if sub is not None and sub.score is not None:
                max_score = asg.max_score or 100
                normalized = (sub.score / max_score) * 5
                task_scores.setdefault((_cls.subject_id, _cls.period), []).append(
                    normalized
                )

        def avg_or_none(values: list[float]) -> float | None:
            return round(sum(values) / len(values), 1) if values else None

        # 6) build the response
        subjects_global = []
        for subject in subject_rows:
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
            for p in (1, 2, 3, 4):
                grade = grades_by_subject_period.get((subject.id, p))
                if grade and grade.final_grade is not None:
                    subject_data[f"period_{p}"] = grade.final_grade
                    period_grades.append(grade.final_grade)
                else:
                    eval_grade = avg_or_none(eval_scores.get((subject.id, p), []))
                    task_grade = avg_or_none(task_scores.get((subject.id, p), []))
                    grades_list = [
                        g for g in [eval_grade, task_grade] if g is not None
                    ]
                    if grades_list:
                        final = round(
                            sum(grades_list) / len(grades_list), 1
                        )
                        subject_data[f"period_{p}"] = final
                        period_grades.append(final)

            if period_grades:
                subject_data["global_grade"] = round(
                    sum(period_grades) / len(period_grades), 1
                )
            subjects_global.append(subject_data)

        return (
            {
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
            },
            200,
        )
    except Exception as e:
        return {"error": f"Error al obtener calificaciones globales: {str(e)}"}, 500
    finally:
        db.close()


def calculate_evaluation_grade(
    db, student_id: int, course_id: int, subject_id: int, period: int
) -> float | None:
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
) -> float | None:
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
    tasks_grade: float | None,
    assignments_grade: float | None,
    evaluations_grade: float | None,
) -> float | None:
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
) -> tuple[dict | None, int]:
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
) -> tuple[dict | None, int]:
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
