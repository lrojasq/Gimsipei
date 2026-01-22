import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from flask import Request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError

from src.database.database import SessionLocal
from src.models.assignment import Assignment
from src.models.assignment_submission import AssignmentSubmission
from src.models.class_model import ClassModel
from src.models.course import Course
from src.models.course_student import CourseStudent
from src.models.course_subject import CourseSubject
from src.models.subject import Subject
from src.models.user import User, UserRole
from src.models.evaluation import Evaluation
from src.models.evaluation_submission import EvaluationSubmission

from .validation import (
    CourseCreateSchema,
    CourseResponseSchema,
    CourseStudentSchema,
    CourseSubjectSchema,
    CourseUpdateSchema,
)


def get_available_course_names() -> List[str]:
    """Genera lista de nombres de cursos disponibles"""

    course_names = [
        "Primero",
        "Segundo",
        "Tercero",
        "Cuarto",
        "Quinto",
        "Sexto",
        "Séptimo",
        "Octavo",
        "Noveno",
        "Décimo",
        "Undecimo",
        "Extracurricular",
    ]
    return course_names


# Diccionario de cursos ordenados por grado
COURSE_NAME_ORDER = {
    "Primero": 1,
    "Segundo": 2,
    "Tercero": 3,
    "Cuarto": 4,
    "Quinto": 5,
    "Sexto": 6,
    "Séptimo": 7,
    "Octavo": 8,
    "Noveno": 9,
    "Décimo": 10,
    "Undécimo": 11,
    "Extracurricular": 12,
}

# Mapeo de nombres de cursos a números de grado (E para Extracurricular)
COURSE_NAME_TO_GRADE = {
    "Primero": 1,
    "Segundo": 2,
    "Tercero": 3,
    "Cuarto": 4,
    "Quinto": 5,
    "Sexto": 6,
    "Séptimo": 7,
    "Octavo": 8,
    "Noveno": 9,
    "Décimo": 10,
    "Undécimo": 11,
    "Extracurricular": "E",
}


def get_grade_number_from_course_name(course_name: str) -> Optional[int]:
    """Extrae el número del grado del nombre del curso"""
    return COURSE_NAME_TO_GRADE.get(course_name)


def get_courses_service(
    academic_year: Optional[str] = None,
) -> Tuple[List[CourseResponseSchema], int]:
    """Obtener lista de cursos"""
    db = SessionLocal()
    try:
        query = db.query(Course)

        # Aplicar filtros
        if academic_year:
            query = query.filter(Course.academic_year == academic_year)

        courses = query.all()
        course_schemas = [
            CourseResponseSchema(
                id=course.id,
                academic_year=course.academic_year,
                name=course.name,
                created_by=course.created_by,
                created_at=course.created_at,
                updated_at=course.updated_at,
            )
            for course in courses
        ]

        # Ordenar solo por orden lógico de grados
        course_schemas.sort(key=lambda c: COURSE_NAME_ORDER.get(c.name, 999))
        return course_schemas, len(course_schemas)
    finally:
        db.close()


def get_all_courses_for_dashboard() -> List[dict]:
    """Obtener todos los cursos con información para el dashboard"""
    db = SessionLocal()
    try:
        courses = db.query(Course).order_by(Course.name).all()

        courses_list = []
        for course in courses:
            grade_number = get_grade_number_from_course_name(course.name)
            courses_list.append(
                {
                    "id": course.id,
                    "name": course.name,
                    "academic_year": course.academic_year,
                    "grade_number": grade_number if grade_number else "?",
                }
            )

        # Ordenar cursos: números primero (1-11), luego strings (E, ?) al final
        def sort_key(x):
            gn = x["grade_number"]
            # Si es número, ordenar por ese número; si es string, va al final
            return gn if isinstance(gn, int) else 999
        
        courses_list.sort(key=sort_key, reverse=False)
        return courses_list
    finally:
        db.close()


def get_course_service(
    course_id: int, request: Request
) -> Tuple[Optional[CourseResponseSchema], int]:
    """Obtener un curso específico"""
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        return CourseResponseSchema(
            id=course.id,
            academic_year=course.academic_year,
            name=course.name,
            created_by=course.created_by,
            created_at=course.created_at,
            updated_at=course.updated_at,
        ), 200
    finally:
        db.close()


def create_course_service(
    data: CourseCreateSchema, request: Request
) -> Tuple[Optional[CourseResponseSchema], int]:
    """Crear un nuevo curso"""
    db = SessionLocal()
    try:
        academic_year = str(datetime.now().year)

        # Verificar si ya existe un curso con el mismo nombre en el mismo año
        existing_course = (
            db.query(Course)
            .filter(
                (Course.name == data.name) & (Course.academic_year == academic_year)
            )
            .first()
        )

        if existing_course:
            return None, 400

        current_user_id = get_jwt_identity()
        course = Course(
            academic_year=academic_year,
            name=data.name,
            created_by=current_user_id,
        )

        db.add(course)
        db.commit()
        db.refresh(course)

        return CourseResponseSchema(
            id=course.id,
            academic_year=course.academic_year,
            name=course.name,
            created_by=course.created_by,
            created_at=course.created_at,
            updated_at=course.updated_at,
        ), 201
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def update_course_service(
    course_id: int, data: CourseUpdateSchema, request: Request
) -> Tuple[Optional[CourseResponseSchema], int]:
    """Actualizar un curso existente"""
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        # Verificar si el nuevo nombre ya existe (si se está cambiando)
        if data.name and data.name != course.name:
            existing_course = (
                db.query(Course)
                .filter(
                    Course.name == data.name,
                    Course.academic_year == course.academic_year,
                    Course.id != course_id,
                )
                .first()
            )

            if existing_course:
                return None, 400

        # Actualizar campos si se proporcionan
        if data.name is not None:
            course.name = data.name

        db.commit()
        db.refresh(course)

        return CourseResponseSchema(
            id=course.id,
            academic_year=course.academic_year,
            name=course.name,
            created_by=course.created_by,
            created_at=course.created_at,
            updated_at=course.updated_at,
        ), 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def delete_course_service(
    course_id: int, request: Request
) -> Tuple[Optional[dict], int]:
    """Eliminar un curso"""
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        # Hard delete: eliminar el curso directamente
        db.delete(course)
        db.commit()

        return {"message": "Curso eliminado exitosamente"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def get_course_students_service(course_id: int) -> Tuple[List[dict], int]:
    """Obtener estudiantes de un curso"""
    db = SessionLocal()
    try:
        course_students = (
            db.query(CourseStudent, User)
            .join(User, CourseStudent.student_id == User.id)
            .filter(CourseStudent.course_id == course_id)
            .all()
        )

        students = []
        for course_student, user in course_students:
            students.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "document": user.document,
                    "enrolled_at": course_student.enrolled_at.isoformat(),
                }
            )

        return students, 200
    finally:
        db.close()


def get_course_students_for_view_service(
    course_id: int,
) -> Tuple[Optional[dict], List[dict], int]:
    """Obtener curso y estudiantes para la vista de estudiantes"""
    db = SessionLocal()
    try:
        # Obtener información del curso
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, [], 404

        # Obtener estudiantes del curso
        course_students = (
            db.query(CourseStudent, User)
            .join(User, CourseStudent.student_id == User.id)
            .filter(CourseStudent.course_id == course_id)
            .filter(User.role == UserRole.STUDENT)
            .all()
        )

        # Convertir a lista de diccionarios
        students_list = []
        for course_student, student_user in course_students:
            students_list.append(
                {
                    "id": student_user.id,
                    "full_name": student_user.full_name or student_user.username,
                    "document": student_user.document,
                    "enrolled_at": course_student.enrolled_at,
                }
            )

        # Extraer número del grado
        grade_number = get_grade_number_from_course_name(course.name)
        if not grade_number:
            grade_number = course.id

        course_data = {
            "id": course.id,
            "name": course.name,
            "academic_year": course.academic_year,
            "grade_number": grade_number,
        }

        return course_data, students_list, 200
    finally:
        db.close()


def add_student_to_course_service(
    course_id: int, data: CourseStudentSchema, request: Request
) -> Tuple[Optional[dict], int]:
    """Agregar estudiante a un curso"""
    db = SessionLocal()
    try:
        # Verificar que el curso existe
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        # Verificar que el usuario es estudiante
        user = (
            db.query(User)
            .filter(User.id == data.student_id, User.role == UserRole.STUDENT)
            .first()
        )
        if not user:
            return None, 400

        # Verificar que no esté ya inscrito
        existing_enrollment = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.course_id == course_id,
                CourseStudent.student_id == data.student_id,
            )
            .first()
        )

        if existing_enrollment:
            return None, 400  # Ya está inscrito

        # Crear nueva inscripción
        course_student = CourseStudent(course_id=course_id, student_id=data.student_id)

        db.add(course_student)
        db.commit()

        return {"message": "Estudiante agregado al curso exitosamente"}, 201
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def remove_student_from_course_service(
    course_id: int, student_id: int, request: Request
) -> Tuple[Optional[dict], int]:
    """Remover estudiante de un curso"""
    db = SessionLocal()
    try:
        course_student = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.course_id == course_id,
                CourseStudent.student_id == student_id,
            )
            .first()
        )

        if not course_student:
            return None, 404

        # Hard delete: eliminar la inscripción directamente
        db.delete(course_student)
        db.commit()

        return {"message": "Estudiante removido del curso exitosamente"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def get_course_subjects_service(course_id: int) -> Tuple[List[dict], int]:
    """Obtener materias de un curso"""
    db = SessionLocal()
    try:
        course_subjects = (
            db.query(CourseSubject, User, Course, Subject)
            .join(User, CourseSubject.teacher_id == User.id)
            .join(Course, CourseSubject.course_id == Course.id)
            .join(Subject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.course_id == course_id)
            .all()
        )

        subjects = []
        for course_subject, teacher, course, subject in course_subjects:
            subjects.append(
                {
                    "id": course_subject.id,
                    "subject_id": course_subject.subject_id,
                    "subject_name": subject.name,
                    "teacher_id": course_subject.teacher_id,
                    "teacher_name": teacher.full_name or teacher.username,
                    "assigned_at": course_subject.assigned_at.isoformat(),
                }
            )

        return subjects, 200
    finally:
        db.close()


def add_subject_to_course_service(
    course_id: int, data: CourseSubjectSchema, request: Request
) -> Tuple[Optional[dict], int]:
    """Agregar o actualizar materia en un curso"""
    db = SessionLocal()
    try:
        # Verificar que el curso existe
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        # --- Modo edición con cambio de materia (mover asignación) ---
        if data.original_subject_id and data.original_subject_id != data.subject_id:
            original_assignment = (
                db.query(CourseSubject)
                .filter(
                    CourseSubject.course_id == course_id,
                    CourseSubject.subject_id == data.original_subject_id,
                )
                .first()
            )

            target_assignment = (
                db.query(CourseSubject)
                .filter(
                    CourseSubject.course_id == course_id,
                    CourseSubject.subject_id == data.subject_id,
                )
                .first()
            )

            # Si ya existe una asignación para el subject destino, actualizamos y eliminamos la original
            if target_assignment:
                # Si no hay original, lo tratamos como "update" normal del destino
                if target_assignment.teacher_id != data.teacher_id:
                    target_assignment.teacher_id = data.teacher_id
                target_assignment.assigned_at = datetime.now(timezone.utc)

                if (
                    original_assignment
                    and original_assignment.id != target_assignment.id
                ):
                    db.delete(original_assignment)

                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()
                    return None, 400
                return {"message": "Asignación actualizada exitosamente"}, 200

            # Si existe la asignación original, la movemos (cambiando subject_id y teacher_id)
            if original_assignment:
                original_assignment.subject_id = data.subject_id
                original_assignment.teacher_id = data.teacher_id
                original_assignment.assigned_at = datetime.now(timezone.utc)
                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()
                    return None, 400
                return {"message": "Asignación actualizada exitosamente"}, 200

        # --- Crear si no existe, o actualizar profesor si existe
        existing_assignment = (
            db.query(CourseSubject)
            .filter(
                CourseSubject.course_id == course_id,
                CourseSubject.subject_id == data.subject_id,
            )
            .first()
        )

        if existing_assignment:
            if existing_assignment.teacher_id == data.teacher_id:
                return {"message": "La materia ya está asignada a este profesor"}, 200

            existing_assignment.teacher_id = data.teacher_id
            existing_assignment.assigned_at = datetime.now(timezone.utc)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                return None, 400
            return {"message": "Asignación actualizada exitosamente"}, 200

        course_subject = CourseSubject(
            course_id=course_id,
            subject_id=data.subject_id,
            teacher_id=data.teacher_id,
        )
        db.add(course_subject)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None, 400
        return {"message": "Materia agregada al curso exitosamente"}, 201
    except IntegrityError:
        db.rollback()
        return None, 400
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def remove_subject_from_course_service(
    course_id: int, subject_id: int, teacher_id: int, request: Request
) -> Tuple[Optional[dict], int]:
    """Remover materia de un curso"""
    db = SessionLocal()
    try:
        course_subject = (
            db.query(CourseSubject)
            .filter(
                CourseSubject.course_id == course_id,
                CourseSubject.subject_id == subject_id,
                CourseSubject.teacher_id == teacher_id,
            )
            .first()
        )

        if not course_subject:
            return None, 404

        db.delete(course_subject)
        db.commit()

        return {"message": "Materia removida del curso exitosamente"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def get_student_tasks_service(
    course_id: int, student_id: int
) -> Tuple[Optional[dict], List[dict], int]:
    """Obtener tareas/asignaciones de un estudiante en un curso, agrupadas por asignatura"""
    db = SessionLocal()
    try:
        # Verificar que el curso existe
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, [], 404

        # Verificar que el estudiante existe y está inscrito en el curso
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            return None, [], 404

        course_student = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.course_id == course_id,
                CourseStudent.student_id == student_id,
            )
            .first()
        )
        if not course_student:
            return None, [], 404

        # Obtener todas las materias del curso (aunque no tengan asignaciones)
        course_subjects = (
            db.query(CourseSubject, Subject)
            .join(Subject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.course_id == course_id)
            .order_by(Subject.name)
            .all()
        )

        # Crear diccionario con todas las materias del curso
        subjects_dict = {}
        for course_subject, subject in course_subjects:
            subjects_dict[subject.id] = {
                "subject_id": subject.id,
                "subject_name": subject.name,
                "classes": [],
            }

        # Obtener todas las asignaciones (tareas) enviadas por el estudiante
        submissions = (
            db.query(
                AssignmentSubmission,
                Assignment,
                ClassModel,
                Subject,
            )
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .join(ClassModel, Assignment.class_id == ClassModel.id)
            .join(Subject, ClassModel.subject_id == Subject.id)
            .filter(
                ClassModel.course_id == course_id,
                AssignmentSubmission.student_id == student_id,
            )
            .order_by(Subject.name, Assignment.title)
            .all()
        )

        # Agrupar asignaciones por asignatura
        for submission, assignment, class_model, subject in submissions:
            if subject.id in subjects_dict:
                subjects_dict[subject.id]["classes"].append(
                    {
                        "id": assignment.id,
                        "title": assignment.title,
                        "class_number": class_model.class_number,
                        "date": submission.submitted_at.strftime("%d-%m-%y")
                        if submission.submitted_at
                        else "",
                        "description": assignment.description,
                    }
                )

        # Si no hay asignaciones, no agregar datos de ejemplo
        # Solo mostrar un mensaje en la vista

        # Convert to ordered list
        subjects_list = list(subjects_dict.values())

        # Preparar datos del curso y estudiante
        course_data = {
            "id": course.id,
            "name": course.name,
            "academic_year": course.academic_year,
            "grade_number": get_grade_number_from_course_name(course.name),
        }

        student_data = {
            "id": student.id,
            "full_name": student.full_name or student.username,
            "document": student.document,
        }

        return {"course": course_data, "student": student_data}, subjects_list, 200
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en get_student_tasks_service: {str(e)}\n{error_trace}")
        return None, [], 500
    finally:
        db.close()


def download_assignment_submission_service(
    course_id: int, student_id: int, assignment_id: int
) -> Tuple[Optional[dict], int]:
    """Obtener el archivo de una entrega de asignación"""
    db = SessionLocal()
    try:
        # Verificar que la entrega existe
        submission = (
            db.query(AssignmentSubmission)
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .join(ClassModel, Assignment.class_id == ClassModel.id)
            .filter(
                AssignmentSubmission.student_id == student_id,
                AssignmentSubmission.assignment_id == assignment_id,
                ClassModel.course_id == course_id,
            )
            .first()
        )

        if not submission or not submission.file_url:
            return None, 404

        # Retornar la ruta del archivo y su información
        return {
            "file_url": submission.file_url,
            "submission_text": submission.submission_text,
            "student_id": submission.student_id,
            "assignment_id": submission.assignment_id,
        }, 200
    except Exception as e:
        print(f"Error en download_assignment_submission_service: {str(e)}")
        return None, 500
    finally:
        db.close()


def delete_assignment_submission_service(
    course_id: int, student_id: int, assignment_id: int
) -> Tuple[Optional[dict], int]:
    """Eliminar una entrega de asignación (archivo y registro)"""
    db = SessionLocal()
    try:
        # Verificar que la entrega existe
        submission = (
            db.query(AssignmentSubmission)
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .join(ClassModel, Assignment.class_id == ClassModel.id)
            .filter(
                AssignmentSubmission.student_id == student_id,
                AssignmentSubmission.assignment_id == assignment_id,
                ClassModel.course_id == course_id,
            )
            .first()
        )

        if not submission:
            return None, 404

        # Obtener la ruta del archivo antes de eliminar el registro
        file_url = submission.file_url

        # Eliminar el archivo físico si existe
        if file_url:
            try:
                # Construir la ruta completa del archivo
                # Asumiendo que file_url es una ruta relativa como "uploads/assignments/..."
                file_path = Path("src/static") / file_url.lstrip("/")

                if file_path.exists():
                    os.remove(file_path)
            except Exception as e:
                print(f"Error al eliminar archivo físico: {str(e)}")
                # Continuar incluso si no se puede eliminar el archivo

        # Eliminar el registro de la base de datos
        db.delete(submission)
        db.commit()

        return {"message": "Entrega eliminada exitosamente"}, 200
    except Exception as e:
        db.rollback()
        print(f"Error en delete_assignment_submission_service: {str(e)}")
        return None, 500
    finally:
        db.close()


def get_student_evaluations_service(
    course_id: int, student_id: int
) -> Tuple[Optional[dict], List[dict], int]:
    """Obtener evaluaciones de un estudiante en un curso, agrupadas por asignatura"""
    db = SessionLocal()
    try:
        # Verificar que el curso existe
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, [], 404

        # Verificar que el estudiante existe y está inscrito en el curso
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            return None, [], 404

        course_student = (
            db.query(CourseStudent)
            .filter(
                CourseStudent.course_id == course_id,
                CourseStudent.student_id == student_id,
            )
            .first()
        )
        if not course_student:
            return None, [], 404

        # Obtener todas las materias del curso
        course_subjects = (
            db.query(CourseSubject, Subject)
            .join(Subject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.course_id == course_id)
            .order_by(Subject.name)
            .all()
        )

        # Crear diccionario con todas las materias del curso
        subjects_dict = {}
        for _, subject in course_subjects:
            subjects_dict[subject.id] = {
                "subject_id": subject.id,
                "subject_name": subject.name,
                "evaluations": [],
            }

        # Obtener todas las evaluaciones enviadas por el estudiante
        submissions = (
            db.query(
                EvaluationSubmission,
                Evaluation,
                Subject,
            )
            .join(Evaluation, EvaluationSubmission.evaluation_id == Evaluation.id)
            .join(Subject, Evaluation.subject_id == Subject.id)
            .filter(
                Evaluation.course_id == course_id,
                EvaluationSubmission.student_id == student_id,
                EvaluationSubmission.is_completed.is_(True),
            )
            .order_by(Subject.name, Evaluation.title)
            .all()
        )

        # Agrupar evaluaciones por asignatura
        for submission, evaluation, subject in submissions:
            if subject.id in subjects_dict:
                subjects_dict[subject.id]["evaluations"].append(
                    {
                        "submission_id": submission.id,
                        "evaluation_id": evaluation.id,
                        "title": evaluation.title,
                        "description": evaluation.description,
                        "score": submission.score,
                        "correct_answers": submission.correct_answers,
                        "total_questions": submission.total_questions,
                        "submitted_at": submission.submitted_at,
                    }
                )

        # Convert to ordered list
        subjects_list = list(subjects_dict.values())

        # Preparar datos del curso y estudiante
        course_data = {
            "id": course.id,
            "name": course.name,
            "academic_year": course.academic_year,
            "grade_number": get_grade_number_from_course_name(course.name),
        }

        student_data = {
            "id": student.id,
            "full_name": student.full_name or student.username,
            "document": student.document,
        }

        return {"course": course_data, "student": student_data}, subjects_list, 200
    except Exception:
        return None, [], 500
    finally:
        db.close()
