import os
from typing import List, Optional, Tuple

from flask import Request
from werkzeug.utils import secure_filename

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

        # Si se filtra por teacher_id, obtener subjects a través de CourseSubject
        if teacher_id:
            query = (
                query.join(CourseSubject, Subject.id == CourseSubject.subject_id)
                .filter(CourseSubject.teacher_id == teacher_id)
                .distinct()
            )

        subjects = query.order_by(Subject.name).all()

        return [
            SubjectResponseSchema(
                id=getattr(subject, "id"),
                name=getattr(subject, "name"),
                created_at=getattr(subject, "created_at"),
                updated_at=getattr(subject, "updated_at"),
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
            id=getattr(subject, "id"),
            name=getattr(subject, "name"),
            created_at=getattr(subject, "created_at"),
            updated_at=getattr(subject, "updated_at"),
        ), 200
    finally:
        db.close()


def create_subject_service(
    data: SubjectCreateSchema, request: Request
) -> Tuple[Optional[SubjectResponseSchema], int]:
    """Crear una nueva materia o retornar la existente si ya existe"""
    db = SessionLocal()
    try:
        # check if the subject already exists
        existing_subject = db.query(Subject).filter(Subject.name == data.name).first()

        if existing_subject:
            # return the existing subject
            return SubjectResponseSchema(
                id=getattr(existing_subject, "id"),
                name=getattr(existing_subject, "name"),
                created_at=getattr(existing_subject, "created_at"),
                updated_at=getattr(existing_subject, "updated_at"),
            ), 200

        # Process cover image if uploaded
        image_url = None
        if request.files and "subject_image" in request.files:
            image_file = request.files["subject_image"]
            if image_file.filename:
                static_folder = "src/static/uploads/cover_class"
                os.makedirs(static_folder, exist_ok=True)
                filename = secure_filename(image_file.filename)
                save_path = os.path.join(static_folder, filename)
                image_file.save(save_path)
                image_url = f"uploads/cover_class/{filename}"

        subject = Subject(name=data.name, image_url=image_url)

        db.add(subject)
        db.commit()
        db.refresh(subject)

        return SubjectResponseSchema(
            id=getattr(subject, "id"),
            name=getattr(subject, "name"),
            image_url=getattr(subject, "image_url", None),
            created_at=getattr(subject, "created_at"),
            updated_at=getattr(subject, "updated_at"),
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

        # Verificar si el nuevo nombre ya existe (si se está cambiando)
        if data.name is not None and data.name != subject.name:
            if data.name != "":
                existing_subject = (
                    db.query(Subject).filter(Subject.name == data.name).first()
                )
                if existing_subject:
                    return None, 400
                subject.name = data.name

        # Manejar actualización de imagen
        if request.files and "subject_image" in request.files:
            image_file = request.files["subject_image"]
            
            # Verificar si el archivo tiene un nombre (no está vacío)
            if image_file and image_file.filename and image_file.filename.strip():
                # Eliminar imagen anterior si existe
                old_image_url = getattr(subject, "image_url", None)
                if (
                    old_image_url
                    and isinstance(old_image_url, str)
                    and old_image_url.strip()
                ):
                    old_path = os.path.join("src/static", old_image_url)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception:
                            pass
                
                # Guardar nueva imagen
                static_folder = "src/static/uploads/cover_class"
                os.makedirs(static_folder, exist_ok=True)
                filename = secure_filename(image_file.filename)
                
                # Generar nombre único si ya existe
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(static_folder, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                save_path = os.path.join(static_folder, filename)
                image_file.save(save_path)
                
                # Actualizar la URL en la base de datos
                subject.image_url = f"uploads/cover_class/{filename}"

        db.commit()
        db.refresh(subject)

        return SubjectResponseSchema(
            id=getattr(subject, "id"),
            name=getattr(subject, "name"),
            image_url=getattr(subject, "image_url", None),
            created_at=getattr(subject, "created_at"),
            updated_at=getattr(subject, "updated_at"),
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


def get_available_subject_names() -> List[str]:
    """Genera lista de nombres de materias disponibles para un colegio"""
    subject_names = [
        "Álgebra",
        "Aritmética",
        "Artes",
        "Biología",
        "Cálculo",
        "Ciencias Naturales",
        "Financiera",
        "Emprendimiento",
        "Español",
        "Estética",
        "Ética",
        "Filosofía",
        "Física",
        "Geometría",
        "Inglés",
        "Informática",
        "Int. Física",
        "Int. Química",
        "Música",
        "Ortografía",
        "Plan Lector",
        "Química",
        "Religión",
        "Sociales",
        "Sociopolítica",
        "Tesis",
        "Trigonometría",
    ]
    return subject_names


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
