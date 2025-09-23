from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from pydantic import ValidationError

from src.classes import service, validation
from src.models.user import UserRole


# Subject Controllers
def create_subject_controller():
    try:
        request_data = dict(request.json) if request.json else {}
        subject_data = validation.SubjectCreate(**request_data)
        subject = service.create_subject(subject_data)
        return jsonify(validation.SubjectInDB.from_orm(subject).dict()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def get_subject_controller(subject_id: int):
    try:
        subject = service.get_subject(subject_id)
        if not subject:
            return jsonify({"error": "Subject not found"}), 404
        return jsonify(validation.SubjectInDB.from_orm(subject).dict())
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def get_all_subjects_controller():
    try:
        subjects = service.get_subjects()
        return jsonify(
            [validation.SubjectInDB.from_orm(subject).dict() for subject in subjects]
        )
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def update_subject_controller(subject_id: int):
    try:
        request_data = dict(request.json) if request.json else {}
        subject_data = validation.SubjectUpdate(**request_data)
        subject = service.update_subject(subject_id, subject_data)
        if not subject:
            return jsonify({"error": "Subject not found"}), 404
        return jsonify(validation.SubjectInDB.from_orm(subject).dict())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def delete_subject_controller(subject_id: int):
    try:
        current_user_id = get_jwt_identity()
        # Verificar autorización en el servicio
        result = service.delete_subject(subject_id, current_user_id)
        if not result:
            return jsonify({"error": "Subject not found"}), 404
        return jsonify({"message": "Subject deleted successfully"})
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


# Period Controllers
def create_period_controller():
    try:
        current_user_id = get_jwt_identity()
        request_data = dict(request.json) if request.json else {}
        period_data = validation.PeriodCreate(**request_data)
        period = service.create_period(period_data, current_user_id)
        return jsonify(validation.PeriodInDB.from_orm(period).dict()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def get_period_controller(period_id: int):
    try:
        period = service.get_period(period_id)
        if not period:
            return jsonify({"error": "Period not found"}), 404
        return jsonify(validation.PeriodInDB.from_orm(period).dict())
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def get_all_periods_controller():
    try:
        periods = service.get_periods()
        return jsonify(
            [validation.PeriodInDB.from_orm(period).dict() for period in periods]
        )
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def update_period_controller(period_id: int):
    try:
        current_user_id = get_jwt_identity()
        request_data = dict(request.json) if request.json else {}
        period_data = validation.PeriodUpdate(**request_data)
        period = service.update_period(period_id, period_data, current_user_id)
        if not period:
            return jsonify({"error": "Period not found"}), 404
        return jsonify(validation.PeriodInDB.from_orm(period).dict())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def delete_period_controller(period_id: int):
    try:
        current_user_id = get_jwt_identity()
        result = service.delete_period(period_id, current_user_id)
        if not result:
            return jsonify({"error": "Period not found"}), 404
        return jsonify({"message": "Period deleted successfully"})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def lock_period_controller(period_id: int):
    try:
        current_user_id = get_jwt_identity()
        period_data = validation.PeriodUpdate(is_locked=True)
        period = service.update_period(period_id, period_data, current_user_id)
        if not period:
            return jsonify({"error": "Period not found"}), 404
        return jsonify(validation.PeriodInDB.from_orm(period).dict())
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


def unlock_period_controller(period_id: int):
    try:
        current_user_id = get_jwt_identity()
        period_data = validation.PeriodUpdate(is_locked=False)
        period = service.update_period(period_id, period_data, current_user_id)
        if not period:
            return jsonify({"error": "Period not found"}), 404
        return jsonify(validation.PeriodInDB.from_orm(period).dict())
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


# # Class Controllers
# def create_class_controller():
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to create classes"}), 403

#             class_data = validation.ClassCreate(**request.json, created_by=current_user_id)
#             db_class = service.create_class(db=db, class_=class_data)
#             return jsonify(validation.ClassInDB.from_orm(db_class).dict()), 201
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def get_class_controller(class_id: int):
#     with get_db_session() as db:
#         db_class = service.get_class(db=db, class_id=class_id)
#         if db_class is None:
#             return jsonify({"message": "Class not found"}), 404
#         return jsonify(validation.ClassInDB.from_orm(db_class).dict())

# def get_all_classes_controller():
#     with get_db_session() as db:
#         classes = service.get_classes(db=db)
#         return jsonify([validation.ClassInDB.from_orm(class_).dict() for class_ in classes])

# def update_class_controller(class_id: int):
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to update classes"}), 403

#             class_data = validation.ClassUpdate(**request.json)
#             db_class = service.update_class(db=db, class_id=class_id, class_=class_data)
#             if db_class is None:
#                 return jsonify({"message": "Class not found"}), 404
#             return jsonify(validation.ClassInDB.from_orm(db_class).dict())
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def delete_class_controller(class_id: int):
#     current_user_id = get_jwt_identity()
#     with get_db_session() as db:
#         current_user = db.query(User).filter(User.id == current_user_id).first()
#         if not current_user or current_user.role not in ["teacher", "admin"]:
#             return jsonify({"message": "Not authorized to delete classes"}), 403

#         db_class = service.delete_class(db=db, class_id=class_id)
#         if db_class is None:
#             return jsonify({"message": "Class not found"}), 404
#         return jsonify({"message": "Class deleted successfully"})

# # Resource Controllers
# def create_resource_controller():
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to create resources"}), 403

#             resource_data = validation.ResourceCreate(**request.json)
#             db_resource = service.create_resource(db=db, resource=resource_data)
#             return jsonify(validation.ResourceInDB.from_orm(db_resource).dict()), 201
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def get_resource_controller(resource_id: int):
#     with get_db_session() as db:
#         db_resource = service.get_resource(db=db, resource_id=resource_id)
#         if db_resource is None:
#             return jsonify({"message": "Resource not found"}), 404
#         return jsonify(validation.ResourceInDB.from_orm(db_resource).dict())

# def get_all_resources_controller():
#     with get_db_session() as db:
#         resources = service.get_resources(db=db)
#         return jsonify([validation.ResourceInDB.from_orm(resource).dict() for resource in resources])

# def update_resource_controller(resource_id: int):
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to update resources"}), 403

#             resource_data = validation.ResourceUpdate(**request.json)
#             db_resource = service.update_resource(db=db, resource_id=resource_id, resource=resource_data)
#             if db_resource is None:
#                 return jsonify({"message": "Resource not found"}), 404
#             return jsonify(validation.ResourceInDB.from_orm(db_resource).dict())
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def delete_resource_controller(resource_id: int):
#     current_user_id = get_jwt_identity()
#     with get_db_session() as db:
#         current_user = db.query(User).filter(User.id == current_user_id).first()
#         if not current_user or current_user.role not in ["teacher", "admin"]:
#             return jsonify({"message": "Not authorized to delete resources"}), 403

#         db_resource = service.delete_resource(db=db, resource_id=resource_id)
#         if db_resource is None:
#             return jsonify({"message": "Resource not found"}), 404
#         return jsonify({"message": "Resource deleted successfully"})

# # Assignment Controllers
# def create_assignment_controller():
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to create assignments"}), 403

#             assignment_data = validation.AssignmentCreate(**request.json)
#             db_assignment = service.create_assignment(db=db, assignment=assignment_data)
#             return jsonify(validation.AssignmentInDB.from_orm(db_assignment).dict()), 201
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def get_assignment_controller(assignment_id: int):
#     with get_db_session() as db:
#         db_assignment = service.get_assignment(db=db, assignment_id=assignment_id)
#         if db_assignment is None:
#             return jsonify({"message": "Assignment not found"}), 404
#         return jsonify(validation.AssignmentInDB.from_orm(db_assignment).dict())

# def get_all_assignments_controller():
#     with get_db_session() as db:
#         assignments = service.get_assignments(db=db)
#         return jsonify([validation.AssignmentInDB.from_orm(assignment).dict() for assignment in assignments])

# def update_assignment_controller(assignment_id: int):
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to update assignments"}), 403

#             assignment_data = validation.AssignmentUpdate(**request.json)
#             db_assignment = service.update_assignment(db=db, assignment_id=assignment_id, assignment=assignment_data)
#             if db_assignment is None:
#                 return jsonify({"message": "Assignment not found"}), 404
#             return jsonify(validation.AssignmentInDB.from_orm(db_assignment).dict())
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def delete_assignment_controller(assignment_id: int):
#     current_user_id = get_jwt_identity()
#     with get_db_session() as db:
#         current_user = db.query(User).filter(User.id == current_user_id).first()
#         if not current_user or current_user.role not in ["teacher", "admin"]:
#             return jsonify({"message": "Not authorized to delete assignments"}), 403

#         db_assignment = service.delete_assignment(db=db, assignment_id=assignment_id)
#         if db_assignment is None:
#             return jsonify({"message": "Assignment not found"}), 404
#         return jsonify({"message": "Assignment deleted successfully"})

# # ClassView Controllers
# def create_class_view_controller():
#     try:
#         current_user_id = get_jwt_identity()
#         with get_db_session() as db:
#             current_user = db.query(User).filter(User.id == current_user_id).first()
#             if not current_user or current_user.role not in ["student", "teacher", "admin"]:
#                 return jsonify({"message": "Not authorized to create class views"}), 403

#             class_view_data = validation.ClassViewCreate(**request.json)
#             db_class_view = service.create_class_view(db=db, class_view=class_view_data)
#             return jsonify(validation.ClassViewInDB.from_orm(db_class_view).dict()), 201
#     except ValidationError as e:
#         return jsonify({"message": "Invalid data", "details": e.errors()}), 400
#     except Exception as e:
#         return jsonify({"message": "An error occurred", "details": str(e)}), 500

# def get_class_view_controller(class_view_id: int):
#     with get_db_session() as db:
#         db_class_view = service.get_class_view(db=db, class_view_id=class_view_id)
#         if db_class_view is None:
#             return jsonify({"message": "Class view not found"}), 404
#         return jsonify(validation.ClassViewInDB.from_orm(db_class_view).dict())

# def get_all_class_views_controller():
#     with get_db_session() as db:
#         class_views = service.get_class_views(db=db)
#         return jsonify([validation.ClassViewInDB.from_orm(class_view).dict() for class_view in class_views])

# def delete_class_view_controller(class_view_id: int):
#     current_user_id = get_jwt_identity()
#     with get_db_session() as db:
#         current_user = db.query(User).filter(User.id == current_user_id).first()
#         if not current_user or current_user.role not in ["student", "teacher", "admin"]:
#             return jsonify({"message": "Not authorized to delete class views"}), 403

#         db_class_view = service.delete_class_view(db=db, class_view_id=class_view_id)
#         if db_class_view is None:
#             return jsonify({"message": "Class view not found"}), 404
#         return jsonify({"message": "Class view deleted successfully"})
