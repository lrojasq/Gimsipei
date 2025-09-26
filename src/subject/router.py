from flask import Blueprint, request
from .subjects_controllers import (
    create_subject_controller,
    edit_subject_controller,
    delete_subject_controller,
)
from .controllers import (
    get_subjects_api_controller,
    get_subject_api_controller,
    create_subject_api_controller,
    update_subject_api_controller,
    delete_subject_api_controller,
)

subjects_bp = Blueprint("subjects", __name__, url_prefix="/subjects")


# Rutas para vistas HTML
@subjects_bp.route("/create", methods=["GET", "POST"])
def create_subject():
    """Crear nueva materia"""
    return create_subject_controller(request)


@subjects_bp.route("/<int:subject_id>/edit", methods=["GET", "POST"])
def edit_subject(subject_id):
    """Editar materia existente"""
    return edit_subject_controller(subject_id, request)


@subjects_bp.route("/<int:subject_id>/delete", methods=["POST"])
def delete_subject(subject_id):
    """Eliminar materia"""
    return delete_subject_controller(subject_id, request)


# Rutas API
@subjects_bp.route("/api", methods=["GET"])
def get_subjects_api():
    """API para obtener lista de materias"""
    return get_subjects_api_controller(request)


@subjects_bp.route("/api/<int:subject_id>", methods=["GET"])
def get_subject_api(subject_id):
    """API para obtener una materia específica"""
    return get_subject_api_controller(subject_id, request)


@subjects_bp.route("/api", methods=["POST"])
def create_subject_api():
    """API para crear una materia"""
    return create_subject_api_controller(request)


@subjects_bp.route("/api/<int:subject_id>", methods=["PUT", "PATCH"])
def update_subject_api(subject_id):
    """API para actualizar una materia"""
    return update_subject_api_controller(subject_id, request)


@subjects_bp.route("/api/<int:subject_id>", methods=["DELETE"])
def delete_subject_api(subject_id):
    """API para eliminar una materia"""
    return delete_subject_api_controller(subject_id, request)
