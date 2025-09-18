from flask import Blueprint, request
from .controllers import (
    create_exercise_controller,
    get_exercises_controller,
    submit_exercise_controller,
    get_exercise_submissions_controller,
)

exercises_bp = Blueprint("exercises", __name__, url_prefix="/api/exercises")


@exercises_bp.route("/", methods=["POST"])
def create_exercise():
    return create_exercise_controller(request)


@exercises_bp.route("/", methods=["GET"])
def get_exercises():
    return get_exercises_controller(request)


@exercises_bp.route("/<int:id>/submit", methods=["POST"])
def submit_exercise(id):
    return submit_exercise_controller(request, id)


@exercises_bp.route("/<int:id>/submissions", methods=["GET"])
def get_exercise_submissions(id):
    return get_exercise_submissions_controller(request, id)
