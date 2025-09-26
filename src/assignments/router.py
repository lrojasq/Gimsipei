from flask import Blueprint, request
from .controllers import (
    create_assignment_controller,
    get_assignments_controller,
    submit_assignment_controller,
    get_assignment_submissions_controller,
    grade_submission_controller,
)

assignments_bp = Blueprint("assignments", __name__, url_prefix="/api/assignments")


@assignments_bp.route("/", methods=["POST"])
def create_assignment():
    return create_assignment_controller(request)


@assignments_bp.route("/", methods=["GET"])
def get_assignments():
    return get_assignments_controller(request)


@assignments_bp.route("/<int:id>/submit", methods=["POST"])
def submit_assignment(id):
    return submit_assignment_controller(request, id)


@assignments_bp.route("/<int:id>/submissions", methods=["GET"])
def get_assignment_submissions(id):
    return get_assignment_submissions_controller(request, id)


@assignments_bp.route("/<int:id>/grade", methods=["POST"])
def grade_submission(id):
    return grade_submission_controller(request, id)
