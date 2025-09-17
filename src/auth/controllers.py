from flask import render_template, Request, jsonify, Response
from flask_jwt_extended import jwt_required
from .service import (
    login_user_service,
    get_current_user_service,
    logout_user_service,
    create_first_admin_service,
    forgot_password_service,
)
from .validation import (
    LoginSchema,
    CreateFirstAdminSchema,
    ForgotPasswordSchema,
)
from pydantic import ValidationError
from flask import flash, redirect, url_for


def login_user_controller(request: Request) -> Response | tuple[dict, int]:
    """Controlador para procesar el login"""
    if request.method == "GET":
        return render_template("auth/login.html")
    try:
        if request.is_json:
            validated = LoginSchema(**request.get_json())
        else:
            form_data = request.form
            username = form_data.get("username")
            password = form_data.get("password")
            validated = LoginSchema(username=username, password=password)

        return login_user_service(validated, request)
    except ValidationError as e:
        if request.is_json:
            return jsonify({"error": str(e)}), 400
        else:
            flash("Datos de formulario inválidos", "danger")
            return redirect(url_for("auth.login"))
    except Exception as e:
        if request.is_json:
            return jsonify({"error": str(e)}), 500
        else:
            flash("Error interno del servidor", "danger")
            return redirect(url_for("auth.login"))


@jwt_required()
def get_current_user_controller(request: Request) -> Response | tuple[dict, int]:
    try:
        return get_current_user_service(request)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def forgot_password_controller(request: Request) -> Response | tuple[dict, int]:
    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    try:
        if request.is_json:
            validated = ForgotPasswordSchema(**request.get_json())
        else:
            form_data = request.form
            username = form_data.get("username")
            new_password = form_data.get("new_password")
            validated = ForgotPasswordSchema(
                username=username, new_password=new_password
            )

        return forgot_password_service(validated, request)
    except ValidationError as e:
        if request.is_json:
            return jsonify({"error": str(e)}), 400
        else:
            flash("Datos de formulario inválidos", "danger")
            return redirect(url_for("auth.forgot_password"))
    except Exception as e:
        if request.is_json:
            return jsonify({"error": str(e)}), 500
        else:
            flash("Error interno del servidor: " + str(e), "danger")
            return redirect(url_for("auth.forgot_password"))


@jwt_required(optional=True)
def logout_user_controller(request: Request) -> Response | tuple[dict, int]:
    try:
        return logout_user_service(request)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_first_admin_controller(request: Request) -> Response | tuple[dict, int]:
    try:
        validated = CreateFirstAdminSchema(**request.get_json())
        return create_first_admin_service(validated, request)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
