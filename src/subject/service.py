from typing import List, Optional, Tuple

from flask import Request

from src.database.database import SessionLocal
from src.models.course import Course
from src.models.course_subject import CourseSubject
from src.models.subject import Subject
from src.models.user import User, UserRole

from .validation import (
    SubjectCreateSchema,
    SubjectResponseSchema,
    SubjectUpdateSchema,
)


def get_subjects_service(
    teacher_id: Optional[int] = None,
) -> Tuple[List[SubjectResponseSchema], int]:
    """Obtener lista de materias con filtros opcionales"""
    db = SessionLocal()
    try:
        query = db.query(Subject)

        # Aplicar filtros
        if teacher_id:
            query = query.filter(Subject.teacher_id == teacher_id)

        subjects = query.order_by(Subject.name).all()

        return [
            SubjectResponseSchema(
                id=subject.id,
                name=subject.name,
                teacher_id=subject.teacher_id,
                created_at=subject.created_at,
                updated_at=subject.updated_at,
            )
            for subject in subjects
        ], len(subjects)
    finally:
        db.close()


def get_subject_service(
    subject_id: int, request: Request
) -> Tuple[Optional[SubjectResponseSchema], int]:
    """Obtener una materia específica"""
    db = SessionLocal()
    try:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return None, 404

        return SubjectResponseSchema(
            id=subject.id,
            name=subject.name,
            teacher_id=subject.teacher_id,
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        ), 200
    finally:
        db.close()


def create_subject_service(
    data: SubjectCreateSchema, request: Request
) -> Tuple[Optional[SubjectResponseSchema], int]:
    """Crear una nueva materia"""
    db = SessionLocal()
    try:
        # Verificar que el profesor existe
        teacher = (
            db.query(User)
            .filter(User.id == data.teacher_id, User.role == UserRole.TEACHER)
            .first()
        )
        if not teacher:
            return None, 400

        # No validamos duplicados de nombre aquí porque un profesor puede dictar
        # la misma materia en diferentes cursos. La validación de duplicados se hace
        # a nivel de asignación curso-materia-profesor en CourseSubject.

        subject = Subject(
            name=data.name,
            teacher_id=data.teacher_id,
        )

        db.add(subject)
        db.commit()
        db.refresh(subject)

        return SubjectResponseSchema(
            id=subject.id,
            name=subject.name,
            teacher_id=subject.teacher_id,
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        ), 201
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def update_subject_service(
    subject_id: int, data: SubjectUpdateSchema, request: Request
) -> Tuple[Optional[SubjectResponseSchema], int]:
    """Actualizar una materia existente"""
    db = SessionLocal()
    try:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return None, 404

        # Verificar que el nuevo profesor existe (si se está cambiando)
        if data.teacher_id and data.teacher_id != subject.teacher_id:
            teacher = (
                db.query(User)
                .filter(User.id == data.teacher_id, User.role == UserRole.TEACHER)
                .first()
            )
            if not teacher:
                return None, 400

        # No validamos duplicados de nombre aquí porque un profesor puede dictar
        # la misma materia en diferentes cursos. La validación de duplicados se hace
        # a nivel de asignación curso-materia-profesor en CourseSubject.

        # Actualizar campos si se proporcionan
        if data.name is not None:
            subject.name = data.name
        if data.teacher_id is not None:
            subject.teacher_id = data.teacher_id

        db.commit()
        db.refresh(subject)

        return SubjectResponseSchema(
            id=subject.id,
            name=subject.name,
            teacher_id=subject.teacher_id,
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        ), 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def delete_subject_service(
    subject_id: int, request: Request
) -> Tuple[Optional[dict], int]:
    """Eliminar una materia"""
    db = SessionLocal()
    try:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not subject:
            return None, 404

        # First, delete all course-subject assignments for this subject
        course_subjects = (
            db.query(CourseSubject).filter(CourseSubject.subject_id == subject_id).all()
        )
        for course_subject in course_subjects:
            db.delete(course_subject)

        # Then delete the subject itself
        db.delete(subject)
        db.commit()

        return {"message": "Materia eliminada exitosamente"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def get_teachers_for_form_service() -> List[dict]:
    """Obtener lista de profesores para formularios"""
    db = SessionLocal()
    try:
        teachers = (
            db.query(User)
            .filter(User.role == UserRole.TEACHER)
            .order_by(User.full_name, User.username)
            .all()
        )
        return [
            {"id": t.id, "name": (t.full_name or t.username or f"Profesor {t.id}")}
            for t in teachers
        ]
    finally:
        db.close()


def get_course_by_id_service(course_id: int) -> Optional[Course]:
    """Obtener un curso por su ID"""
    db = SessionLocal()
    try:
        return db.query(Course).filter(Course.id == course_id).first()
    finally:
        db.close()


def get_subject_with_teachers_service(
    subject_id: int, request: Request
) -> Tuple[Optional[SubjectResponseSchema], List[dict], int]:
    """Obtener una materia con la lista de profesores para formularios"""
    subject, status_code = get_subject_service(subject_id, request)
    if status_code != 200:
        return None, [], status_code

    teachers = get_teachers_for_form_service()
    return subject, teachers, 200
