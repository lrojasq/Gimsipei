from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required

from .controllers import (
    get_grades_api_controller,
    grades_view_controller,
    student_global_grades_view_controller,
    student_grades_view_controller,
    update_grade_api_controller,
    update_grade_controller,
)

grades_bp = Blueprint("grades", __name__, url_prefix="/grades")


# ========== HTML View Routes ==========
@grades_bp.route("", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def grades_view():
    """Vista principal de calificaciones"""
    return grades_view_controller(request)


@grades_bp.route("/course/<int:course_id>/student/<int:student_id>", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def student_grades_view(course_id, student_id):
    """Vista de calificaciones de un estudiante por materia y periodo"""
    return student_grades_view_controller(course_id, student_id, request)


@grades_bp.route(
    "/course/<int:course_id>/student/<int:student_id>/global", methods=["GET"]
)
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def student_global_grades_view(course_id, student_id):
    """Vista de calificaciones globales de un estudiante"""
    return student_global_grades_view_controller(course_id, student_id, request)


@grades_bp.route(
    "/course/<int:course_id>/student/<int:student_id>/subject/<int:subject_id>/update",
    methods=["POST"],
)
@jwt_required()
@role_required([UserRole.TEACHER])
def update_grade(course_id, student_id, subject_id):
    """Actualizar calificación de un estudiante"""
    return update_grade_controller(course_id, student_id, subject_id, request)


# ========== API Routes ==========
@grades_bp.route(
    "/api/course/<int:course_id>/student/<int:student_id>", methods=["GET"]
)
@jwt_required()
@role_required([UserRole.TEACHER])
def get_grades_api(course_id, student_id):
    """API para obtener calificaciones de un estudiante"""
    return get_grades_api_controller(course_id, student_id, request)


@grades_bp.route(
    "/api/course/<int:course_id>/student/<int:student_id>/subject/<int:subject_id>",
    methods=["PUT"],
)
@jwt_required()
@role_required([UserRole.TEACHER])
def update_grade_api(course_id, student_id, subject_id):
    """API para actualizar calificación"""
    return update_grade_api_controller(course_id, student_id, subject_id, request)
