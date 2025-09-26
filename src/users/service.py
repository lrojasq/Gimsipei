from flask import Request
from typing import List, Optional, Tuple

# from sqlalchemy.orm import Session
from src.database.database import SessionLocal
from src.models.user import User, UserRole
from werkzeug.security import generate_password_hash
from .validation import UserCreateSchema, UserUpdateSchema, UserResponseSchema


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

        user = User(
            username=data.username,
            document=data.document,
            hashed_password=generate_password_hash(data.password),
            full_name=data.full_name,
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


def delete_user_service(user_id: int, request: Request) -> Tuple[Optional[dict], int]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, 404

        # Soft delete: mark as inactive to avoid FK constraint issues
        user.is_active = 0
        db.commit()

        return {"message": "User deleted successfully"}, 200
    except Exception:
        db.rollback()
        return None, 500
    finally:
        db.close()
