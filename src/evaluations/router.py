from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from src.utils.decorator_role_required import role_required
from src.models.user import UserRole

from .controllers import (
    evaluations_view_controller,
    subject_evaluations_view_controller,
    create_evaluation_controller,
    update_evaluation_controller,
    delete_evaluation_controller,
    get_evaluation_json_controller,
    get_evaluations_api_controller,
    get_evaluation_api_controller,
    student_evaluations_view_controller,
    student_take_evaluation_controller,
    student_submit_evaluation_controller,
    reset_evaluation_submission_controller,
    delete_evaluation_submission_controller,
    view_submission_answers_controller,
    update_submission_score_controller,
)

evaluations_bp = Blueprint("evaluations", __name__, url_prefix="/evaluations")


# ========== HTML View Routes ==========
@evaluations_bp.route("", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def evaluations_view():
    """Vista principal de evaluaciones para profesores"""
    return evaluations_view_controller(request)


@evaluations_bp.route(
    "/course/<int:course_id>/subject/<int:subject_id>", methods=["GET"]
)
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def subject_evaluations_view(course_id: int, subject_id: int):
    """Vista detallada de evaluaciones por materia"""
    return subject_evaluations_view_controller(course_id, subject_id, request)


@evaluations_bp.route("/create", methods=["GET", "POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def create_evaluation():
    """Crear nueva evaluación"""
    return create_evaluation_controller(request)


@evaluations_bp.route("/<int:evaluation_id>/edit", methods=["GET", "POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def update_evaluation(evaluation_id: int):
    """Actualizar evaluación"""
    return update_evaluation_controller(evaluation_id, request)


@evaluations_bp.route("/<int:evaluation_id>/delete", methods=["POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def delete_evaluation(evaluation_id: int):
    """Eliminar evaluación"""
    return delete_evaluation_controller(evaluation_id, request)


@evaluations_bp.route("/<int:evaluation_id>/get", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def get_evaluation_json(evaluation_id: int):
    """Obtener evaluación en formato JSON"""
    return get_evaluation_json_controller(evaluation_id, request)


# ========== API Routes ==========
@evaluations_bp.route("/api", methods=["GET"])
def get_evaluations_api():
    """API para obtener todas las evaluaciones"""
    return get_evaluations_api_controller(request)


@evaluations_bp.route("/api/<int:evaluation_id>", methods=["GET"])
def get_evaluation_api(evaluation_id: int):
    """API para obtener una evaluación específica"""
    return get_evaluation_api_controller(evaluation_id, request)


@evaluations_bp.route("/student", methods=["GET"])
@jwt_required()
@role_required([UserRole.STUDENT])
def student_evaluations_view():
    """Vista de evaluaciones para estudiantes"""
    filter_type = request.args.get("filter", "pending")
    return student_evaluations_view_controller(filter_type, request)


@evaluations_bp.route("/student/take/<int:evaluation_id>", methods=["GET"])
@jwt_required()
@role_required([UserRole.STUDENT])
def student_take_evaluation(evaluation_id: int):
    """Vista para que el estudiante resuelva una evaluación"""
    return student_take_evaluation_controller(evaluation_id, request)


@evaluations_bp.route("/student/submit/<int:evaluation_id>", methods=["POST"])
@jwt_required()
@role_required([UserRole.STUDENT])
def student_submit_evaluation(evaluation_id: int):
    """Enviar respuestas de la evaluación"""
    return student_submit_evaluation_controller(evaluation_id, request)


@evaluations_bp.route("/submission/<int:submission_id>/reset", methods=["POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def reset_evaluation_submission(submission_id: int):
    """Reiniciar evaluación de un estudiante (eliminar respuestas y permitir volver a presentar)"""
    return reset_evaluation_submission_controller(submission_id, request)


@evaluations_bp.route("/submission/<int:submission_id>/delete", methods=["POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def delete_evaluation_submission(submission_id: int):
    """Eliminar envío de evaluación de un estudiante"""
    return delete_evaluation_submission_controller(submission_id, request)


@evaluations_bp.route("/submission/<int:submission_id>/view", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER])
def view_submission_answers(submission_id: int):
    """Ver las respuestas de un estudiante en una evaluación"""
    return view_submission_answers_controller(submission_id, request)


@evaluations_bp.route("/submission/<int:submission_id>/update-score", methods=["POST"])
@jwt_required()
@role_required([UserRole.TEACHER])
def update_submission_score(submission_id: int):
    """Actualizar la nota de un envío de evaluación"""
    return update_submission_score_controller(submission_id, request)

