from flask import Blueprint
from flask_jwt_extended import jwt_required
from src.utils.decorator_role_required import role_required
from src.models.user import UserRole

from src.classes import controllers

class_bp = Blueprint("classes", __name__, url_prefix="/classes")


# Subject Routes
@class_bp.route("/subjects", methods=["POST"])
@jwt_required()
@role_required(UserRole.ADMIN)
def create_subject_route():
    return controllers.create_subject_controller()


@class_bp.route("/subjects/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_subject_route(subject_id):
    return controllers.get_subject_controller(subject_id)


@class_bp.route("/subjects", methods=["GET"])
@jwt_required()
def get_all_subjects_route():
    return controllers.get_all_subjects_controller()


@class_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def update_subject_route(subject_id):
    return controllers.update_subject_controller(subject_id)


@class_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_subject_route(subject_id):
    return controllers.delete_subject_controller(subject_id)


# Period Routes
@class_bp.route("/periods", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def create_period_route():
    return controllers.create_period_controller()


@class_bp.route("/periods/<int:period_id>", methods=["GET"])
@jwt_required()
def get_period_route(period_id):
    return controllers.get_period_controller(period_id)


@class_bp.route("/periods", methods=["GET"])
@jwt_required()
def get_all_periods_route():
    return controllers.get_all_periods_controller()


@class_bp.route("/periods/<int:period_id>", methods=["PUT"])
@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def update_period_route(period_id):
    return controllers.update_period_controller(period_id)


@class_bp.route("/periods/<int:period_id>", methods=["DELETE"])
@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def delete_period_route(period_id):
    return controllers.delete_period_controller(period_id)


@class_bp.route("/periods/<int:period_id>/lock", methods=["PUT"])
@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def lock_period_route(period_id):
    return controllers.lock_period_controller(period_id)


@class_bp.route("/periods/<int:period_id>/unlock", methods=["PUT"])
@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def unlock_period_route(period_id):
    return controllers.unlock_period_controller(period_id)


# HTML View Routes
@class_bp.route("/teacher", methods=["GET"])
@jwt_required()
@role_required(UserRole.TEACHER)
def teacher_classes_view():
    """Vista HTML de clases y recursos para teachers"""
    return controllers.teacher_classes_view_controller()


@class_bp.route("/teacher/subject/<int:course_id>/<int:subject_id>", methods=["GET"])
@jwt_required()
@role_required(UserRole.TEACHER)
def subject_classes_view(course_id: int, subject_id: int):
    """Vista HTML de clases de una materia específica"""
    return controllers.subject_classes_view_controller(course_id, subject_id)


# Rutas para crear clases y recursos
@class_bp.route("/create", methods=["POST"])
@jwt_required()
@role_required(UserRole.TEACHER)
def create_class():
    """Crear una nueva clase"""
    return controllers.create_class_controller()


@class_bp.route("/resources/create", methods=["POST"])
@jwt_required()
@role_required(UserRole.TEACHER)
def create_resource():
    """Crear un nuevo recurso"""
    return controllers.create_resource_controller()


@class_bp.route("/update/<int:class_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.TEACHER)
def update_class(class_id: int):
    """Actualizar una clase existente"""
    return controllers.update_class_controller(class_id)


@class_bp.route("/delete/<int:class_id>", methods=["POST"])
@jwt_required()
@role_required(UserRole.TEACHER)
def delete_class(class_id: int):
    """Eliminar una clase"""
    return controllers.delete_class_controller(class_id)


@class_bp.route("/get/<int:class_id>", methods=["GET"])
@jwt_required()
@role_required(UserRole.TEACHER)
def get_class(class_id: int):
    """Obtener datos de una clase específica"""
    return controllers.get_class_controller(class_id)
