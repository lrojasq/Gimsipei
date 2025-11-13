from flask import Blueprint, request

from .controllers import (
    resources_view_controller,
    create_resource_controller,
    delete_resource_controller,
    get_resources_by_class_api_controller,
    get_resource_api_controller,
    create_resource_api_controller,
    update_resource_api_controller,
    delete_resource_api_controller,
)

resources_bp = Blueprint("resources", __name__, url_prefix="/resources")


# ========== HTML View Routes ==========
@resources_bp.route("", methods=["GET"])
def resources_view():
    """Vista principal de recursos"""
    return resources_view_controller(request)


@resources_bp.route("/create", methods=["GET", "POST"])
def create_resource():
    """Crear nuevo recurso"""
    return create_resource_controller(request)


@resources_bp.route("/<int:resource_id>/delete", methods=["POST"])
def delete_resource(resource_id):
    """Eliminar recurso"""
    return delete_resource_controller(resource_id, request)


# ========== API Routes ==========
@resources_bp.route("/api/class/<int:class_id>", methods=["GET"])
def get_resources_by_class_api(class_id):
    """API para obtener recursos de una clase"""
    return get_resources_by_class_api_controller(class_id, request)


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
