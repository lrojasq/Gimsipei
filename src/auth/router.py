from flask import Blueprint, request
from .controllers import (
    login_user_controller,
    get_current_user_controller,
    logout_user_controller,
    create_first_admin_controller,
    forgot_password_controller,
    index_menu_controller,
    clases_controller,
    recursos_controller,
    evaluaciones_controller,
    libros_controller,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    return login_user_controller(request)


@auth_bp.route("/index-menu", methods=["GET"])
def index_menu():
    return index_menu_controller(request)

@auth_bp.route("/clases", methods=["GET"])
def clases():
    return clases_controller(request)


@auth_bp.route("/recursos", methods=["GET"])
def recursos():
    return recursos_controller(request)

@auth_bp.route("/evaluaciones", methods=["GET"])
def evaluaciones():
    return evaluaciones_controller(request)


@auth_bp.route("/libros", methods=["GET"])
def libros():
    return libros_controller(request)









@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    return get_current_user_controller(request)


@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password():
    return forgot_password_controller(request)



@auth_bp.route("/logout", methods=["POST"])
def logout():
    return logout_user_controller(request)


@auth_bp.route("/first-admin", methods=["POST"])
def create_first_admin():
    return create_first_admin_controller(request)
