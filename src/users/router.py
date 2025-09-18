from flask import Blueprint, request
from .controllers import (
    get_users_controller,
    get_user_controller,
    create_user_controller,
    update_user_controller,
    delete_user_controller,
)
from .teachers_controllers import (
    teachers_management_controller,
    create_teacher_controller,
    edit_teacher_controller,
    delete_teacher_controller,
)

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
def get_users():
    return get_users_controller(request)


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    return get_user_controller(user_id, request)


@users_bp.route("/create", methods=["GET", "POST"])
def create_user():
    return create_user_controller(request)


@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def update_user(user_id):
    return update_user_controller(user_id, request)


@users_bp.route("/<int:user_id>/delete", methods=["GET", "POST"])
def delete_user(user_id):
    return delete_user_controller(user_id, request)


# Routes for teachers management
@users_bp.route("/teachers", methods=["GET"])
def teachers_management():
    return teachers_management_controller(request)


@users_bp.route("/teachers/create", methods=["GET", "POST"])
def create_teacher():
    return create_teacher_controller(request)


@users_bp.route("/teachers/<int:teacher_id>/edit", methods=["GET", "POST"])
def edit_teacher(teacher_id):
    return edit_teacher_controller(teacher_id, request)


@users_bp.route("/teachers/<int:teacher_id>/delete", methods=["POST"])
def delete_teacher(teacher_id):
    return delete_teacher_controller(teacher_id, request)
