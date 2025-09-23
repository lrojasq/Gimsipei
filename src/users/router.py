from flask import Blueprint, request
from .controllers import (
    get_users_controller,
    get_user_controller,
    create_user_controller,
    update_user_controller,
    delete_user_controller,
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
