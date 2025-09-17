from typing import List, Optional, Tuple

from flask import Request
from flask_jwt_extended import get_jwt_identity

from src.database.database import SessionLocal
from src.models.course import Course
from src.models.course_student import CourseStudent
from src.models.course_subject import CourseSubject
from src.models.user import User, UserRole
from src.models.subject import Subject

from .validation import (
    CourseCreateSchema,
    CourseResponseSchema,
    CourseStudentSchema,
    CourseSubjectSchema,
    CourseUpdateSchema,
)


def get_courses_service(
    academic_year: Optional[str] = None,
    period: Optional[int] = None,
    grade_level: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Tuple[List[CourseResponseSchema], int]:
    """Obtener lista de cursos"""
    db = SessionLocal()
    try:
        query = db.query(Course)

        # Aplicar filtros
        if academic_year:
            query = query.filter(Course.academic_year == academic_year)
        if period:
            query = query.filter(Course.period == period)
        if grade_level:
            query = query.filter(Course.grade_level == grade_level)
        if is_active is not None:
            query = query.filter(Course.is_active == is_active)

        courses = query.order_by(
            Course.academic_year.desc(), Course.period, Course.grade_level
        ).all()

        return [
            CourseResponseSchema(
                id=course.id,
                academic_year=course.academic_year,
                period=course.period,
                grade_level=course.grade_level,
                name=course.name,
                is_active=course.is_active,
                created_by=course.created_by,
                created_at=course.created_at,
                updated_at=course.updated_at,
            )
            for course in courses
        ], len(courses)
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
            period=course.period,
            grade_level=course.grade_level,
            name=course.name,
            is_active=course.is_active,
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
        # Verificar si ya existe un curso con el mismo nombre en el mismo año y período
        existing_course = (
            db.query(Course)
            .filter(
                (Course.name == data.name)
                & (Course.academic_year == data.academic_year)
                & (Course.period == data.period)
            )
            .first()
        )

        if existing_course:
            return None, 400

        current_user_id = get_jwt_identity()
        course = Course(
            academic_year=data.academic_year,
            period=data.period,
            grade_level=data.grade_level,
            name=data.name,
            created_by=current_user_id,
        )

        db.add(course)
        db.commit()
        db.refresh(course)

        return CourseResponseSchema(
            id=course.id,
            academic_year=course.academic_year,
            period=course.period,
            grade_level=course.grade_level,
            name=course.name,
            is_active=course.is_active,
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
                    Course.academic_year == data.academic_year or course.academic_year,
                    Course.period == data.period or course.period,
                    Course.id != course_id,
                )
                .first()
            )

            if existing_course:
                return None, 400

        # Actualizar campos si se proporcionan
        if data.academic_year is not None:
            course.academic_year = data.academic_year
        if data.period is not None:
            course.period = data.period
        if data.grade_level is not None:
            course.grade_level = data.grade_level
        if data.name is not None:
            course.name = data.name
        if data.is_active is not None:
            course.is_active = data.is_active

        db.commit()
        db.refresh(course)

        return CourseResponseSchema(
            id=course.id,
            academic_year=course.academic_year,
            period=course.period,
            grade_level=course.grade_level,
            name=course.name,
            is_active=course.is_active,
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
    """Eliminar un curso (soft delete)"""
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None, 404

        # Soft delete: marcar como inactivo
        course.is_active = False
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
            .filter(CourseStudent.course_id == course_id, CourseStudent.is_active)
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
            if existing_enrollment.is_active:
                return None, 400  # Ya está inscrito
            else:
                # Reactivar inscripción
                existing_enrollment.is_active = True
                db.commit()
                return {"message": "Estudiante agregado al curso exitosamente"}, 200

        # Crear nueva inscripción
        course_student = CourseStudent(
            course_id=course_id, student_id=data.student_id, is_active=data.is_active
        )

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

        course_student.is_active = False
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
            .filter(CourseSubject.course_id == course_id, CourseSubject.is_active)
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
            if existing_assignment.is_active:
                return None, 400  # Ya está asignado
            else:
                # Reactivar asignación
                existing_assignment.is_active = True
                db.commit()
                return {"message": "Materia agregada al curso exitosamente"}, 200

        # Crear nueva asignación
        course_subject = CourseSubject(
            course_id=course_id,
            subject_id=data.subject_id,
            teacher_id=data.teacher_id,
            is_active=data.is_active,
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

        course_subject.is_active = False
        db.commit()

        return {"message": "Materia removida del curso exitosamente"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()
