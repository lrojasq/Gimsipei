from flask import Blueprint, request
from .courses_controllers import (
    courses_management_controller,
    create_course_controller,
    edit_course_controller,
    delete_course_controller,
    course_detail_controller,
    remove_student_from_course_controller,
    remove_subject_from_course_controller,
)
from .controllers import (
    get_courses_api_controller,
    get_course_api_controller,
    create_course_api_controller,
    update_course_api_controller,
    delete_course_api_controller,
    get_course_subjects_api_controller,
    add_subject_to_course_api_controller,
    remove_subject_from_course_api_controller,
)

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


# Rutas para vistas HTML
@courses_bp.route("", methods=["GET"])
def courses_management():
    """Gestión de cursos - Vista principal"""
    return courses_management_controller(request)


@courses_bp.route("/create", methods=["GET", "POST"])
def create_course():
    """Crear nuevo curso"""
    return create_course_controller(request)


@courses_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id):
    """Editar curso existente"""
    return edit_course_controller(course_id, request)


@courses_bp.route("/<int:course_id>/delete", methods=["POST"])
def delete_course(course_id):
    """Eliminar curso"""
    return delete_course_controller(course_id, request)


@courses_bp.route("/<int:course_id>", methods=["GET"])
def course_detail(course_id):
    """Detalle del curso con estudiantes y materias"""
    return course_detail_controller(course_id, request)


@courses_bp.route("/<int:course_id>/students/<int:student_id>/remove", methods=["POST"])
def remove_student_from_course(course_id, student_id):
    return remove_student_from_course_controller(course_id, student_id, request)


@courses_bp.route(
    "/<int:course_id>/subjects/<int:subject_id>/<int:teacher_id>/remove",
    methods=["POST"],
)
def remove_subject_from_course(course_id, subject_id, teacher_id):
    return remove_subject_from_course_controller(
        course_id, subject_id, teacher_id, request
    )


# Rutas API
@courses_bp.route("/api", methods=["GET"])
def get_courses_api():
    """API para obtener lista de cursos"""
    return get_courses_api_controller(request)


@courses_bp.route("/api/<int:course_id>", methods=["GET"])
def get_course_api(course_id):
    """API para obtener un curso específico"""
    return get_course_api_controller(course_id, request)


@courses_bp.route("/api", methods=["POST"])
def create_course_api():
    """API para crear un curso"""
    return create_course_api_controller(request)


@courses_bp.route("/api/<int:course_id>", methods=["PUT", "PATCH"])
def update_course_api(course_id):
    """API para actualizar un curso"""
    return update_course_api_controller(course_id, request)


@courses_bp.route("/api/<int:course_id>", methods=["DELETE"])
def delete_course_api(course_id):
    """API para eliminar un curso"""
    return delete_course_api_controller(course_id, request)


# API de materias por curso (para UI acordeón)
@courses_bp.route("/api/<int:course_id>/subjects", methods=["GET"])
def get_course_subjects_api(course_id):
    return get_course_subjects_api_controller(course_id, request)


@courses_bp.route("/api/<int:course_id>/subjects", methods=["POST"])
def add_subject_to_course_api(course_id):
    return add_subject_to_course_api_controller(course_id, request)


@courses_bp.route(
    "/api/<int:course_id>/subjects/<int:subject_id>/<int:teacher_id>",
    methods=["DELETE"],
)
def remove_subject_from_course_api(course_id, subject_id, teacher_id):
    return remove_subject_from_course_api_controller(
        course_id, subject_id, teacher_id, request
    )
