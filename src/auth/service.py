from flask import (
    redirect,
    url_for,
    flash,
    make_response,
)
from src.models.user import User, UserRole
from src.database.database import SessionLocal
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Request, Response
from .validation import (
    LoginSchema,
    CreateFirstAdminSchema,
)
import os


def login_user_service(
    validated: LoginSchema, request: Request
) -> Response | tuple[dict, int]:
    db = SessionLocal()
    try:
        try:
            user = (
                db.query(User).filter_by(username=validated.username).first()
                or db.query(User).filter_by(email=validated.username).first()
            )
        except Exception as e:
            db.rollback()
            message = "Error de conexión con la base de datos"
            if request.is_json:
                return {"error": message}, 500
            flash(message, "danger")
            return redirect(url_for("auth.login"))
    finally:
        db.close()

    try:
        if not user or not check_password_hash(
            user.hashed_password, validated.password
        ):
            message = "Credenciales inválidas"
            if request.is_json:
                return {"error": message}, 401
            flash(message, "danger")
            return redirect(url_for("auth.login"))
        access_token = create_access_token(identity=user.id)
        if request.is_json:
            return {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role.name,
                },
            }, 200
        response = make_response(redirect(url_for("admin.dashboard")))
        set_access_cookies(response, access_token)
        flash(f"Bienvenido, {user.username}!", "success")
        return response
    except Exception as e:
        message = "Error al procesar el inicio de sesión"
        if request.is_json:
            return {"error": message}, 500
        flash(message, "danger")
        return redirect(url_for("auth.login"))


def get_current_user_service(request: Request) -> tuple[dict, int]:
    user_id: int = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
    finally:
        db.close()
    if not user:
        return {"error": "User not found"}, 404
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role.name,
    }, 200


def logout_user_service(request: Request) -> Response:
    response = make_response(redirect(url_for("auth.login")))
    unset_jwt_cookies(response)
    flash("Has cerrado sesión exitosamente.", "success")
    return response


def create_first_admin_service(
    validated: CreateFirstAdminSchema, request: Request
) -> tuple[dict, int]:
    """Crea el primer administrador del sistema usando una clave secreta"""
    if validated.secret_key != os.getenv("FIRST_ADMIN_SECRET_KEY"):
        return {"error": "Clave secreta inválida"}, 401

    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        if db.query(User).filter(User.role == UserRole.ADMIN).first():
            return {"error": "Ya existe un administrador en el sistema"}, 400

        # Verificar si el email o username ya están en uso
        if db.query(User).filter_by(email=validated.email).first():
            return {"error": "El correo electrónico ya está registrado"}, 400
        if db.query(User).filter_by(username=validated.username).first():
            return {"error": "El nombre de usuario ya está en uso"}, 400

        user = User(
            email=validated.email,
            username=validated.username,
            hashed_password=generate_password_hash(validated.password),
            full_name=validated.full_name,
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Administrador creado exitosamente"}, 201
    finally:
        db.close()
