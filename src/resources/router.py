from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from src.utils.decorator_role_required import role_required
from src.models.user import UserRole

from .controllers import (
    resources_view_controller,
    resources_view_subject_controller,
    create_resource_controller,
    delete_resource_controller,
    download_resource_controller,
    student_resources_view_controller,
    get_resources_by_class_api_controller,
    get_resource_api_controller,
    create_resource_api_controller,
    update_resource_api_controller,
    delete_resource_api_controller,
    get_available_classes_api_controller,
)

resources_bp = Blueprint("resources", __name__, url_prefix="/resources")


# ========== HTML View Routes ==========
@resources_bp.route("", methods=["GET"])
@jwt_required()
@role_required(UserRole.TEACHER)
def resources_view():
    """Vista principal de recursos para profesores"""
    return resources_view_controller(request)


@resources_bp.route("/create", methods=["GET", "POST"])
@jwt_required()
@role_required(UserRole.TEACHER)
def create_resource():
    """Crear nuevo recurso"""
    return create_resource_controller(request)


@resources_bp.route("/<int:resource_id>/delete", methods=["POST"])
@jwt_required()
@role_required(UserRole.TEACHER)
def delete_resource(resource_id):
    """Eliminar recurso"""
    return delete_resource_controller(resource_id, request)


@resources_bp.route("/<int:resource_id>/download", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def download_resource(resource_id):
    """Descargar archivo del recurso"""
    return download_resource_controller(resource_id, request)


# ========== Student Routes ==========
@resources_bp.route("/student", methods=["GET"])
@jwt_required()
@role_required(UserRole.STUDENT)
def student_resources_view():
    """Vista principal de recursos para estudiantes - muestra materias"""
    return student_resources_view_controller(request)


@resources_bp.route("/course/<int:course_id>/subject/<int:subject_id>", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def resources_view_subject(course_id, subject_id):
    """Vista de recursos de una materia específica para profesores y estudiantes"""
    return resources_view_subject_controller(course_id, subject_id, request)


# ========== API Routes ==========
@resources_bp.route("/api/class/<int:class_id>", methods=["GET"])
def get_resources_by_class_api(class_id):
    """API para obtener recursos de una clase"""
    return get_resources_by_class_api_controller(class_id, request)


@resources_bp.route("/api/classes", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER])
def get_available_classes_api():
    """API para listar clases existentes (por curso/materia/periodo) para crear recursos"""
    return get_available_classes_api_controller(request)


@resources_bp.route("/api/<int:resource_id>", methods=["GET"])
def get_resource_api(resource_id):
    """API para obtener un recurso específico"""
    return get_resource_api_controller(resource_id, request)


@resources_bp.route("/api", methods=["POST"])
def create_resource_api():
    """API para crear un recurso"""
    return create_resource_api_controller(request)


@resources_bp.route("/api/<int:resource_id>", methods=["PUT", "PATCH"])
def update_resource_api(resource_id):
    """API para actualizar un recurso"""
    return update_resource_api_controller(resource_id, request)


@resources_bp.route("/api/<int:resource_id>", methods=["DELETE"])
def delete_resource_api(resource_id):
    """API para eliminar un recurso"""
    return delete_resource_api_controller(resource_id, request)
