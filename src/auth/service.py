from flask import (
    redirect,
    url_for,
    flash,
    make_response,
    render_template,
)
from src.models.user import User, UserRole
from src.database.database import SessionLocal
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Request, Response
from .validation import (
    LoginSchema,
    CreateFirstAdminSchema,
    ForgotPasswordSchema,
)
import os
from functools import wraps


def login_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            flash("Por favor inicie sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login_form"))
        return f(*args, **kwargs)

    return decorated_function


def login_user_service(
    validated: LoginSchema, request: Request
) -> Response | tuple[dict, int]:
    db = SessionLocal()
    try:
        try:
            user = db.query(User).filter_by(username=validated.username).first()
        except Exception:
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

        # Crear token de acceso
        access_token = create_access_token(
            identity=user.id, additional_claims={"role": user.role.name}
        )

        if request.is_json:
            return {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.name,
                },
            }, 200

        # Redirigir al dashboard
        response = make_response(redirect(url_for("admin.dashboard")))

        set_access_cookies(response, access_token)
        flash(f"Bienvenido, {user.username}!", "success")
        return response
    except Exception:
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
        "username": user.username,
        "role": user.role.name,
    }, 200


def logout_user_service(request: Request) -> Response:
    from flask_jwt_extended import get_jwt_identity

    # Crear respuesta de redirección
    response = make_response(redirect(url_for("auth.login")))

    # Verificar si había una sesión activa
    try:
        user_id = get_jwt_identity()
        if user_id:
            # Si había sesión activa, limpiar cookies y mostrar mensaje de éxito
            unset_jwt_cookies(response)
            flash("Has cerrado sesión exitosamente.", "success")
        else:
            # Si no había sesión activa, solo redirigir
            flash("Ya no tenías una sesión activa.", "info")
    except Exception:
        # En caso de cualquier error, solo limpiar cookies y redirigir
        unset_jwt_cookies(response)
        flash("Sesión cerrada.", "info")

    return response


def forgot_password_service(
    validated: ForgotPasswordSchema, request: Request
) -> Response | tuple[dict, int]:
    """Servicio para recuperar/actualizar contraseña"""
    db = SessionLocal()
    try:
        # Buscar usuario por username
        user = db.query(User).filter_by(username=validated.username).first()

        if not user:
            message = "Usuario no encontrado"
            if request.is_json:
                return {"error": message}, 404
            flash(message, "danger")
            return redirect(url_for("auth.forgot_password"))

        # Actualizar contraseña
        user.hashed_password = generate_password_hash(validated.new_password)
        db.commit()

        message = f"Se ha actualizado la contraseña para el usuario {user.username}"
        if request.is_json:
            return {"message": message}, 200

        flash(message, "success")
        return render_template("auth/forgot_password.html")

    except Exception:
        db.rollback()
        message = "Error al actualizar la contraseña"
        if request.is_json:
            return {"error": message}, 500
        flash(message, "danger")
        return redirect(url_for("auth.forgot_password"))
    finally:
        db.close()


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

        # Verificar si el username ya está en uso
        if db.query(User).filter_by(username=validated.username).first():
            return {"error": "El nombre de usuario ya está en uso"}, 400

        user = User(
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
        db.rollback()
        db.close()
