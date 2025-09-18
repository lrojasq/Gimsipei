from flask import Blueprint, request
from .controllers import (
    admin_controller,
    login_user_controller,
    get_current_user_controller,
    logout_user_controller,
    create_first_admin_controller,
    forgot_password_controller,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Procesa login"""
    return login_user_controller(request)


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    return get_current_user_controller(request)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return forgot_password_controller(request)


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    return logout_user_controller(request)


@auth_bp.route("/first-admin", methods=["POST"])
def create_first_admin():
    return create_first_admin_controller(request)

