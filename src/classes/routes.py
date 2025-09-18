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


# # Class Routes
# @class_bp.route('/classes', methods=['POST'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def create_class_route():
#     return controllers.create_class_controller()

# @class_bp.route('/classes/<int:class_id>', methods=['GET'])
# @jwt_required()
# def get_class_route(class_id):
#     return controllers.get_class_controller(class_id)

# @class_bp.route('/classes', methods=['GET'])
# def get_all_classes_route():
#     return controllers.get_all_classes_controller()

# @class_bp.route('/classes/<int:class_id>', methods=['PUT'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def update_class_route(class_id):
#     return controllers.update_class_controller(class_id)

# @class_bp.route('/classes/<int:class_id>', methods=['DELETE'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def delete_class_route(class_id):
#     return controllers.delete_class_controller(class_id)

# # Resource Routes
# @class_bp.route('/resources', methods=['POST'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def create_resource_route():
#     return controllers.create_resource_controller()

# @class_bp.route('/resources/<int:resource_id>', methods=['GET'])
# @jwt_required()
# def get_resource_route(resource_id):
#     return controllers.get_resource_controller(resource_id)

# @class_bp.route('/resources', methods=['GET'])
# @jwt_required()
# def get_all_resources_route():
#     return controllers.get_all_resources_controller()

# @class_bp.route('/resources/<int:resource_id>', methods=['PUT'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def update_resource_route(resource_id):
#     return controllers.update_resource_controller(resource_id)

# @class_bp.route('/resources/<int:resource_id>', methods=['DELETE'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def delete_resource_route(resource_id):
#     return controllers.delete_resource_controller(resource_id)

# # Assignment Routes
# @class_bp.route('/assignments', methods=['POST'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def create_assignment_route():
#     return controllers.create_assignment_controller()

# @class_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
# @jwt_required()
# def get_assignment_route(assignment_id):
#     return controllers.get_assignment_controller(assignment_id)

# @class_bp.route('/assignments', methods=['GET'])
# @jwt_required()
# def get_all_assignments_route():
#     return controllers.get_all_assignments_controller()

# @class_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def update_assignment_route(assignment_id):
#     return controllers.update_assignment_controller(assignment_id)

# @class_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER])
# def delete_assignment_route(assignment_id):
#     return controllers.delete_assignment_controller(assignment_id)

# # ClassView Routes
# @class_bp.route('/class-views', methods=['POST'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
# def create_class_view_route():
#     return controllers.create_class_view_controller()

# @class_bp.route('/class-views/<int:class_view_id>', methods=['GET'])
# @jwt_required()
# def get_class_view_route(class_view_id):
#     return controllers.get_class_view_controller(class_view_id)

# @class_bp.route('/class-views', methods=['GET'])
# @jwt_required()
# def get_all_class_views_route():
#     return controllers.get_all_class_views_controller()

# @class_bp.route('/class-views/<int:class_view_id>', methods=['DELETE'])
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
# def delete_class_view_route(class_view_id):
#     return controllers.delete_class_view_controller(class_view_id)
