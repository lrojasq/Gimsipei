from typing import List, Optional, Tuple
from datetime import datetime

from flask import Request
from flask_jwt_extended import get_jwt_identity

from src.database.database import SessionLocal
from src.models.course import Course
from src.models.course_student import CourseStudent
from src.models.course_subject import CourseSubject
from src.models.user import User, UserRole
from src.models.subject import Subject
from src.models.class_model import ClassModel

from .validation import (
    CourseCreateSchema,
    CourseResponseSchema,
    CourseStudentSchema,
    CourseSubjectSchema,
    CourseUpdateSchema,
)


def get_available_course_names() -> List[str]:
    """Genera lista de nombres de cursos disponibles"""

    course_names = ["Sexto", "Séptimo", "Octavo", "Noveno", "Décimo", "Undécimo"]
    return course_names


# Diccionario de cursos ordenados por grado
COURSE_NAME_ORDER = {
    "Sexto": 1,
    "Séptimo": 2,
    "Octavo": 3,
    "Noveno": 4,
    "Décimo": 5,
    "Undécimo": 6,
}

# Mapeo de nombres de cursos a números de grado
COURSE_NAME_TO_GRADE = {
    "Sexto": 6,
    "Séptimo": 7,
    "Octavo": 8,
    "Noveno": 9,
    "Décimo": 10,
    "Undécimo": 11,
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
                    "grade_number": grade_number if grade_number else course.id,
                }
            )

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
    """Agregar materia a un curso"""
    db = SessionLocal()
    try:
        # Verificar que el curso existe
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        # Verificar que el usuario es profesor
        teacher = (
            db.query(User)
            .filter(User.id == data.teacher_id, User.role == UserRole.TEACHER)
            .first()
        )
        if not teacher:
            return None, 400

        # Verificar que no esté ya asignado
        existing_assignment = (
            db.query(CourseSubject)
            .filter(
                CourseSubject.course_id == course_id,
                CourseSubject.subject_id == data.subject_id,
                CourseSubject.teacher_id == data.teacher_id,
            )
            .first()
        )

        if existing_assignment:
            return None, 400  # Ya está asignado

        # Crear nueva asignación
        course_subject = CourseSubject(
            course_id=course_id,
            subject_id=data.subject_id,
            teacher_id=data.teacher_id,
        )

        db.add(course_subject)
        db.commit()

        return {"message": "Materia agregada al curso exitosamente"}, 201
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
    """Obtener tareas/clases de un estudiante en un curso, agrupadas por asignatura"""
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

        # Obtener todas las materias del curso (aunque no tengan clases)
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

        # Obtener todas las clases del curso y agregarlas a las materias correspondientes
        classes = (
            db.query(ClassModel, Subject)
            .join(Subject, ClassModel.subject_id == Subject.id)
            .filter(ClassModel.course_id == course_id)
            .order_by(Subject.name, ClassModel.class_number)
            .all()
        )

        # Agrupar clases por asignatura
        for class_model, subject in classes:
            if subject.id in subjects_dict:
                subjects_dict[subject.id]["classes"].append(
                    {
                        "id": class_model.id,
                        "title": class_model.title,
                        "class_number": class_model.class_number,
                        "date": class_model.date.strftime("%d-%m-%y")
                        if class_model.date
                        else "",
                        "description": class_model.description,
                    }
                )

        # Si no hay clases reales, agregar clases de ejemplo para cada materia
        if not classes:
            from datetime import datetime

            example_date = datetime.now().strftime("%d-%m-%y")
            for subject_id, subject_data in subjects_dict.items():
                # Agregar 3 clases de ejemplo por materia
                for i in range(1, 4):
                    subject_data["classes"].append(
                        {
                            "id": f"example_{subject_id}_{i}",
                            "title": f"Clase de ejemplo {i}",
                            "class_number": i,
                            "date": example_date,
                            "description": "Clase de ejemplo",
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
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en get_student_tasks_service: {str(e)}\n{error_trace}")
        return None, [], 500
    finally:
        db.close()