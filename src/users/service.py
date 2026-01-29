from typing import List, Optional, Tuple

from flask import Request
from werkzeug.security import generate_password_hash

# from sqlalchemy.orm import Session
from src.database.database import SessionLocal
from src.models.assignment import Assignment
from src.models.assignment_submission import AssignmentSubmission
from src.models.book import Book
from src.models.class_model import ClassModel
from src.models.class_view import ClassView
from src.models.course import Course
from src.models.course_student import CourseStudent
from src.models.course_subject import CourseSubject
from src.models.document import Document
from src.models.evaluation import Evaluation
from src.models.evaluation_submission import EvaluationSubmission
from src.models.grade import Grade
from src.models.user import User, UserRole

from .validation import UserCreateSchema, UserResponseSchema, UserUpdateSchema


def get_users_service(
    role: Optional[UserRole] = None,
) -> Tuple[List[UserResponseSchema], int]:
    db = SessionLocal()
    try:
        query = db.query(User)

        # Only active users
        query = query.filter(User.is_active == 1)

        if role:
            query = query.filter(User.role == role)

        users = query.all()

        return [
            UserResponseSchema(
                id=user.id,
                username=user.username,
                document=user.document,
                full_name=user.full_name,
                avatar=getattr(user, "avatar", None),
                role=user.role.value,
                is_active=bool(user.is_active),
            )
            for user in users
        ], len(users)
    finally:
        db.close()


def get_user_service(
    user_id: int, request: Request
) -> Tuple[Optional[UserResponseSchema], int]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, 404
        return (
            UserResponseSchema(
                id=user.id,
                username=user.username,
                document=user.document,
                full_name=user.full_name,
                avatar=getattr(user, "avatar", None),
                role=user.role.value,
                is_active=bool(user.is_active),
            ),
            200,
        )
    finally:
        db.close()


def create_user_service(
    data: UserCreateSchema, request: Request
) -> Tuple[Optional[UserResponseSchema], int]:
    db = SessionLocal()
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == data.username).first():
            return None, 400

        # Check if document already exists
        if db.query(User).filter(User.document == data.document).first():
            return None, 400

        avatar_filename = data.avatar or "buho.png"

        user = User(
            username=data.username,
            document=data.document,
            hashed_password=generate_password_hash(data.password),
            full_name=data.full_name,
            avatar=avatar_filename,
            role=data.role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Convertir el usuario a UserResponseSchema antes de retornarlo
        user_response = UserResponseSchema(
            id=user.id,
            username=user.username,
            document=user.document,
            full_name=user.full_name,
            avatar=getattr(user, "avatar", None),
            role=user.role.value,
            is_active=bool(user.is_active),
        )

        return user_response, 201
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def update_user_service(
    user_id: int, data: UserUpdateSchema, request: Request
) -> Tuple[Optional[UserResponseSchema], int]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, 404

        # Update fields if provided
        if data.username is not None:
            # Check if new username is already taken
            if (
                db.query(User)
                .filter(User.username == data.username, User.id != user_id)
                .first()
            ):
                return None, 400
            user.username = data.username

        if data.document is not None:
            # Check if new document is already taken
            if (
                db.query(User)
                .filter(User.document == data.document, User.id != user_id)
                .first()
            ):
                return None, 400
            user.document = data.document

        if data.password is not None:
            user.hashed_password = generate_password_hash(data.password)

        if data.full_name is not None:
            user.full_name = data.full_name

        if data.avatar is not None:
            user.avatar = data.avatar

        if data.role is not None:
            user.role = data.role

        if data.is_active is not None:
            user.is_active = data.is_active

        db.commit()
        db.refresh(user)

        return (
            UserResponseSchema(
                id=user.id,
                username=user.username,
                document=user.document,
                full_name=user.full_name,
                avatar=getattr(user, "avatar", None),
                role=user.role.value,
                is_active=bool(user.is_active),
            ),
            200,
        )
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()


def delete_user_service(
    user_id: int, _: Request, current_user_id: Optional[int] = None
) -> Tuple[Optional[dict], int]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, 404

        if current_user_id and user_id == current_user_id:
            return (
                {
                    "message": "No se puede eliminar su propio usuario. Por favor, solicite a otro administrador que realice esta acción."
                },
                409,
            )

        # Verificar si es el último administrador
        if user.role == UserRole.ADMIN:
            admin_count = (
                db.query(User)
                .filter(User.role == UserRole.ADMIN, User.is_active == 1)
                .count()
            )
            if admin_count <= 1:
                return (
                    {
                        "message": "No se puede eliminar el último administrador del sistema. Debe haber al menos un administrador activo."
                    },
                    409,
                )

        # Eliminar datos específicos de docentes
        if user.role == UserRole.TEACHER:
            db.query(CourseSubject).filter(CourseSubject.teacher_id == user_id).delete()

        # Eliminar contenido educativo creado por el usuario
        db.query(Assignment).filter(Assignment.created_by == user_id).delete()
        db.query(Evaluation).filter(Evaluation.created_by == user_id).delete()
        db.query(Book).filter(Book.created_by == user_id).delete()
        db.query(Document).filter(Document.author_id == user_id).delete()
        try:
            db.query(ClassModel).filter(ClassModel.created_by == user_id).delete()
        except Exception:
            pass
        db.query(Course).filter(Course.created_by == user_id).delete()
        db.flush()

        # Eliminar datos específicos según el rol
        if user.role == UserRole.STUDENT:
            # Eliminar datos de actividad y progreso del estudiante
            db.query(ClassView).filter(ClassView.student_id == user_id).delete()
            db.query(AssignmentSubmission).filter(
                AssignmentSubmission.student_id == user_id
            ).delete()
            db.query(EvaluationSubmission).filter(
                EvaluationSubmission.student_id == user_id
            ).delete()
            db.query(Grade).filter(Grade.student_id == user_id).delete()
            db.query(CourseStudent).filter(CourseStudent.student_id == user_id).delete()
        else:
            # Para docentes/administradores, eliminar inscripciones si existen
            db.query(CourseStudent).filter(CourseStudent.student_id == user_id).delete()
        db.flush()

        # Eliminar usuario
        db.query(User).filter(User.id == user_id).delete()
        db.commit()

        return {"message": "Usuario eliminado exitosamente"}, 200
    except Exception as e:
        db.rollback()
        error_message = str(e)
        if (
            "foreign key constraint" in error_message.lower()
            or "FOREIGN KEY" in error_message
        ):
            return (
                {
                    "message": "No se puede eliminar el usuario porque tiene datos relacionados. Por favor, elimine primero los datos relacionados."
                },
                409,
            )
        return {"message": f"Error al eliminar el usuario: {error_message}"}, 500
    finally:
        db.close()
