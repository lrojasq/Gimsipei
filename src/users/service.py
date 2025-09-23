from flask import Request, Response
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from src.database.database import SessionLocal
from src.models.user import User, UserRole
from werkzeug.security import generate_password_hash
from .validation import UserCreateSchema, UserUpdateSchema, UserResponseSchema


def get_users_service(
    role: Optional[UserRole] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
) -> Tuple[List[UserResponseSchema], int]:
    db = SessionLocal()
    try:
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term))
                | (User.email.ilike(search_term))
                | (User.full_name.ilike(search_term))
            )

        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()

        return [
            UserResponseSchema(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role.value,
                is_active=bool(user.is_active),
            )
            for user in users
        ], total
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
                email=user.email,
                username=user.username,
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
        # Check if email or username already exists
        if db.query(User).filter(User.email == data.email).first():
            return None, 400
        if db.query(User).filter(User.username == data.username).first():
            return None, 400

        user = User(
            email=data.email,
            username=data.username,
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
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            is_active=bool(user.is_active),
        )

        return user_response, 201
    except Exception as e:
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
        if data.email is not None:
            # Check if new email is already taken
            if (
                db.query(User)
                .filter(User.email == data.email, User.id != user_id)
                .first()
            ):
                return None, 400
            user.email = data.email

        if data.username is not None:
            # Check if new username is already taken
            if (
                db.query(User)
                .filter(User.username == data.username, User.id != user_id)
                .first()
            ):
                return None, 400
            user.username = data.username

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
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role.value,
                is_active=bool(user.is_active),
            ),
            200,
        )
    except Exception as e:
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

        db.delete(user)
        db.commit()

        return {"message": "User deleted successfully"}, 200
    except Exception as e:
        db.rollback()
        return None, 500
    finally:
        db.close()
