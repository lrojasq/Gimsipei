from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity, get_jwt
from pydantic import ValidationError

from src.classes import service, validation
from src.classes.service import create_class_service
from src.classes.service import create_resource_service


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


# HTML View Controllers
def teacher_classes_view_controller():
    """Vista HTML para que los teachers vean los cursos con sus materias"""
    try:
        courses, status_code = service.get_all_courses_with_subjects()

        if status_code != 200:
            flash("Error al cargar los cursos", "danger")
            courses = []

        return render_template(
            "teacher/teacher_classes.html",
            courses=courses,
            user={"role": get_jwt().get("role").lower(), "id": get_jwt().get("id")},
            accion_logout=True,
        )
    except Exception as e:
        flash(f"Error al cargar los cursos: {str(e)}", "danger")
        return render_template(
            "teacher/teacher_classes.html",
            courses=[],
            user={"role": get_jwt().get("role").lower(), "id": get_jwt().get("id")},
            accion_logout=True,
        )


def create_class_controller():
    """Controlador para crear una nueva clase"""
    try:
        current_user_id = get_jwt_identity()

        # Obtener datos del formulario
        data = {
            "course_id": request.form.get("course_id"),
            "subject_id": request.form.get("subject_id"),
            "class_number": request.form.get("class_number"),
            "title": request.form.get("title"),
            "description": request.form.get("description", ""),
            "period": request.form.get("period", 1),
        }

        # Obtener archivo de portada si existe
        cover_file = request.files.get("cover_image")
        result, status_code = create_class_service(data, cover_file, current_user_id)

        if status_code == 201:
            flash(result["message"], "success")
        else:
            flash(result.get("error", "Error al crear la clase"), "danger")

        return redirect(url_for("classes.teacher_classes_view"))
    except Exception:
        flash("Error al crear la clase", "danger")
        return redirect(url_for("classes.teacher_classes_view"))


def create_resource_controller():
    """Controlador para crear un nuevo recurso"""
    try:
        # Obtener datos del formulario
        data = {
            "class_id": request.form.get("class_id"),
            "title": request.form.get("title"),
            "description": request.form.get("description", ""),
            "url": request.form.get("url", ""),
        }

        # Obtener archivo del recurso si existe
        resource_file = request.files.get("resource_file")
        result, status_code = create_resource_service(data, resource_file)

        if status_code == 201:
            flash(result["message"], "success")
        else:
            flash(result.get("error", "Error al crear el recurso"), "danger")

        # Redirigir a la vista de clases
        return redirect(url_for("classes.teacher_classes_view"))

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en create_resource_controller: {str(e)}\n{error_trace}")
        flash("Error al crear el recurso", "danger")
        return redirect(url_for("classes.teacher_classes_view"))


def subject_classes_view_controller(course_id: int, subject_id: int):
    """Vista HTML para mostrar las clases de una materia específica"""
    try:
        data, status_code = service.get_classes_by_subject_service(
            course_id, subject_id
        )

        if status_code != 200:
            flash(data.get("error", "Error al cargar las clases"), "danger")
            return redirect(url_for("classes.teacher_classes_view"))

        return render_template(
            "teacher/subject_classes_view.html",
            course=data["course"],
            subject=data["subject"],
            teacher=data["teacher"],
            classes_by_period=data["classes_by_period"],
            user={"role": get_jwt().get("role").lower(), "id": get_jwt().get("id")},
            accion_logout=True,
        )
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en subject_classes_view_controller: {str(e)}\n{error_trace}")
        flash(f"Error al cargar las clases: {str(e)}", "danger")
        return redirect(url_for("classes.teacher_classes_view"))


def update_class_controller(class_id: int):
    """Controlador para actualizar una clase existente"""
    try:
        data = {
            "class_number": request.form.get("class_number"),
            "title": request.form.get("title"),
            "description": request.form.get("description", ""),
            "period": request.form.get("period"),
        }

        # Obtener archivo de portada si existe
        cover_file = request.files.get("cover_image")
        result, status_code = service.update_class_service(class_id, data, cover_file)

        if status_code == 200:
            flash(result["message"], "success")
        else:
            flash(result.get("error", "Error al actualizar la clase"), "danger")

        # Redirigir a la vista anterior (obtener de referrer o default)
        course_id = request.form.get("course_id")
        subject_id = request.form.get("subject_id")

        if course_id and subject_id:
            return redirect(
                url_for(
                    "classes.subject_classes_view",
                    course_id=course_id,
                    subject_id=subject_id,
                )
            )
        return redirect(url_for("classes.teacher_classes_view"))

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en update_class_controller: {str(e)}\n{error_trace}")
        flash("Error al actualizar la clase", "danger")
        return redirect(url_for("classes.teacher_classes_view"))


def delete_class_controller(class_id: int):
    """Controlador para eliminar una clase"""
    try:
        current_user_id = get_jwt_identity()
        result, status_code = service.delete_class_service(class_id, current_user_id)

        if status_code == 200:
            flash(result["message"], "success")
        else:
            flash(result.get("error", "Error al eliminar la clase"), "danger")

        # Redirigir a la vista anterior
        return redirect(request.referrer or url_for("classes.teacher_classes_view"))
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en delete_class_controller: {str(e)}\n{error_trace}")
        flash("Error al eliminar la clase", "danger")
        return redirect(url_for("classes.teacher_classes_view"))


def get_class_controller(class_id: int):
    """Controlador para obtener datos de una clase específica"""
    try:
        result, status_code = service.get_class_by_id_service(class_id)
        return jsonify(result), status_code

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error en get_class_controller: {str(e)}\n{error_trace}")
        return jsonify({"error": "Error al obtener la clase"}), 500
