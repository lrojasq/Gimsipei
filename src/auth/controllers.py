from flask import render_template, Request, jsonify, Response
from flask_jwt_extended import jwt_required
from .service import (
    login_user_service,
    get_current_user_service,
    logout_user_service,
    create_first_admin_service,
)
from .validation import (
    LoginSchema,
    CreateFirstAdminSchema,
)
from pydantic import ValidationError


def login_user_controller(request: Request) -> Response | tuple[dict, int]:
    try:
        validated = LoginSchema(**request.get_json())
        return login_user_service(validated, request)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def index_menu_controller(request: Request) -> Response:
    return render_template("auth/user.html")

def clases_controller(request: Request) -> Response:
    return render_template("category/clases.html")

def recursos_controller(request: Request) -> Response:
    return render_template("category/recursos.html")

def evaluaciones_controller(request: Request) -> Response:
    return render_template("category/evaluaciones.html")

def libros_controller(request: Request) -> Response:
    return render_template("category/libros.html")

def calificaciones_controller(request: Request) -> Response:
    return render_template("category/calificaciones.html")

def calificaciones_controller(request: Request) -> Response:
    return render_template("category/calificaciones.html")

def admin_controller(request: Request) -> Response:
    return render_template("admin/dashboard.html")

@jwt_required()
def get_current_user_controller(request: Request) -> Response | tuple[dict, int]:
    try:
        return get_current_user_service(request)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def forgot_password_controller(request: Request) -> Response:
    return render_template("auth/forgot_password.html")



@jwt_required()
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
