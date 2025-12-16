from flask import request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import get_jwt_identity, get_jwt
from pydantic import ValidationError

from src.classes import service, validation
from src.users.service import get_user_service
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


# HTML View Controllers
def teacher_classes_view_controller():
    """Vista HTML para que los teachers vean los cursos con sus materias"""
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)
        courses, status_code = service.get_all_courses_with_subjects()

        if status_code != 200:
            courses = []

        return render_template(
            "teacher/teacher_classes.html",
            courses=courses,
            user=current_user,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))


def create_class_controller():
    """Controlador para crear una nueva clase"""
    try:
        current_user_id = get_jwt_identity()

        # Obtener datos del formulario
        course_id = request.form.get("course_id")
        subject_id = request.form.get("subject_id")

        data = {
            "course_id": course_id,
            "subject_id": subject_id,
            "class_number": request.form.get("class_number"),
            "title": request.form.get("title"),
            "description": request.form.get("description", ""),
            "period": request.form.get("period", 1),
        }

        # Obtener archivo de portada si existe
        cover_file = request.files.get("cover_image")
        result, status_code = create_class_service(data, cover_file, current_user_id)

        # Redirigir a la vista de clases de la materia si tenemos los IDs
        if course_id and subject_id:
            return redirect(
                url_for(
                    "classes.subject_classes_view",
                    course_id=course_id,
                    subject_id=subject_id,
                )
            )

        # Fallback a la vista general
        return redirect(url_for("classes.teacher_classes_view"))
    except Exception:
        # Try to redirect with the IDs if they are available
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

        # Redirigir a la vista de clases
        return redirect(url_for("classes.teacher_classes_view"))

    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def subject_classes_view_controller(course_id: int, subject_id: int):
    """Vista HTML para mostrar las clases de una materia específica"""
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)

        data, status_code = service.get_classes_by_subject_service(
            course_id, subject_id
        )

        if status_code != 200:
            return redirect(url_for("classes.teacher_classes_view"))

        return render_template(
            "teacher/subject_classes_view.html",
            course=data["course"],
            subject=data["subject"],
            teacher=data["teacher"],
            classes_by_period=data["classes_by_period"],
            user=current_user,
            accion_logout=True,
        )
    except Exception:
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

        # Redirigir a la vista de clases por período
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

    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def delete_class_controller(class_id: int):
    """Controlador para eliminar una clase"""
    try:
        user_role = get_jwt().get("role")
        result, status_code = service.delete_class_service(class_id, user_role)

        if status_code == 200:
            pass
        else:
            pass

        # Redirect to the previous view
        return redirect(request.referrer or url_for("classes.teacher_classes_view"))
    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def get_class_controller(class_id: int):
    """Controlador para obtener datos de una clase específica"""
    try:
        result, status_code = service.get_class_by_id_service(class_id)
        return jsonify(result), status_code

    except Exception:
        return jsonify({"error": "Error al obtener la clase"}), 500


# Student Controllers
def student_classes_view_controller():
    """Vista HTML para que los estudiantes vean las materias de su curso"""
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)

        # Obtener el curso y materias del estudiante
        data, status_code = service.get_student_course_subjects_service(current_user_id)

        if status_code != 200:
            return redirect(url_for("users.dashboard"))

        return render_template(
            "student/classes_view.html",
            course=data.get("course"),
            subjects=data.get("subjects", []),
            user=current_user,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))


def student_subject_classes_view_controller(course_id: int, subject_id: int):
    """Vista HTML para que los estudiantes vean las clases de una materia"""
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)

        # Obtener las clases de la materia y el progreso del estudiante
        data, status_code = service.get_student_subject_classes_service(
            current_user_id, course_id, subject_id
        )

        if status_code != 200:
            return redirect(url_for("classes.student_classes_view"))

        return render_template(
            "student/subject_classes_view.html",
            course=data["course"],
            subject=data["subject"],
            classes_by_period=data["classes_by_period"],
            viewed_class_ids=data["viewed_class_ids"],
            viewed_classes=data["viewed_classes"],
            total_classes=data["total_classes"],
            viewed_percentage=data["viewed_percentage"],
            user=current_user,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("classes.student_classes_view"))


def mark_class_as_viewed_controller():
    """Controlador para marcar una clase como vista o no vista"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        class_id = data.get("class_id")
        course_id = data.get("course_id")
        subject_id = data.get("subject_id")
        viewed = data.get("viewed", True)

        if not all([class_id, course_id, subject_id]):
            return jsonify({"success": False, "error": "Datos incompletos"}), 400

        # Call the service to mark/unmark the class
        result, status_code = service.mark_class_as_viewed_service(
            current_user_id, class_id, course_id, subject_id, viewed
        )

        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_student_progress_controller(course_id: int, subject_id: int):
    """Controlador para obtener el progreso de un estudiante en una materia"""
    try:
        current_user_id = get_jwt_identity()

        # Call the service to get the progress
        result, status_code = service.get_student_progress_service(
            current_user_id, course_id, subject_id
        )

        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_student_viewed_classes_controller(course_id: int, subject_id: int):
    """Obtener IDs de clases vistas."""
    try:
        current_user_id = get_jwt_identity()
        result, status_code = service.get_student_viewed_class_ids_service(
            current_user_id, course_id, subject_id
        )
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Class Detail View Controllers
def class_detail_view_controller(class_id: int):
    """Redirige a la vista de detalle según el rol del usuario"""
    try:
        user_role = get_jwt().get("role")

        if user_role == "student":
            return redirect(
                url_for("classes.student_class_detail_view", class_id=class_id)
            )
        elif user_role == "teacher":
            return redirect(
                url_for("classes.teacher_class_detail_view", class_id=class_id)
            )
        else:
            return redirect(url_for("users.dashboard"))
    except Exception:
        return redirect(url_for("users.dashboard"))


def student_class_detail_view_controller(class_id: int):
    """Vista detallada de una clase para estudiantes"""
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)

        # Obtener detalle de la clase
        data, status_code = service.get_class_detail_service(
            class_id, user_id=current_user_id, user_role="student"
        )

        if status_code != 200:
            return redirect(url_for("classes.student_classes_view"))

        return render_template(
            "student/class_detail_view.html",
            class_data=data["class"],
            course=data["course"],
            subject=data["subject"],
            contents=data["contents"],
            assignments=data["assignments"],
            user=current_user,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("classes.student_classes_view"))


def teacher_class_detail_view_controller(class_id: int):
    """Vista detallada de una clase para profesores"""
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)

        # Obtener detalle de la clase
        data, status_code = service.get_class_detail_service(
            class_id, user_id=current_user_id, user_role="teacher"
        )

        if status_code != 200:
            return redirect(url_for("classes.teacher_classes_view"))

        return render_template(
            "teacher/class_detail_view.html",
            class_data=data["class"],
            course=data["course"],
            subject=data["subject"],
            contents=data["contents"],
            assignments=data["assignments"],
            user=current_user,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


# Class Content Controllers
def create_class_content_controller():
    """Controlador para crear contenido de una clase"""
    try:
        data = {
            "class_id": request.form.get("class_id"),
            "content_order": request.form.get("content_order", 1),
            "section_title": request.form.get("section_title"),
            "content_text": request.form.get("content_text"),
        }

        image_file = request.files.get("content_image")
        result, status_code = service.create_class_content_service(data, image_file)

        # Redirigir a la vista de detalle de la clase
        class_id = request.form.get("class_id")
        return redirect(url_for("classes.teacher_class_detail_view", class_id=class_id))

    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def update_class_content_controller(content_id: int):
    """Controlador para actualizar contenido de una clase"""
    try:
        data = {
            "section_title": request.form.get("section_title"),
            "content_text": request.form.get("content_text"),
            "content_order": request.form.get("content_order"),
        }

        image_file = request.files.get("content_image")
        result, status_code = service.update_class_content_service(
            content_id, data, image_file
        )

        # Redirigir a la vista de detalle de la clase
        class_id = request.form.get("class_id")
        return redirect(url_for("classes.teacher_class_detail_view", class_id=class_id))

    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def delete_class_content_controller(content_id: int):
    """Controlador para eliminar contenido de una clase"""
    try:
        result, status_code = service.delete_class_content_service(content_id)

        return redirect(request.referrer or url_for("classes.teacher_classes_view"))
    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


# Assignment Controllers
def create_assignment_controller():
    """Controlador para crear una tarea"""
    try:
        current_user_id = get_jwt_identity()

        data = {
            "class_id": request.form.get("class_id"),
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "due_date": request.form.get("due_date"),
            "max_score": request.form.get("max_score", 100),
        }

        result, status_code = service.create_assignment_service(data, current_user_id)

        # Redirigir a la vista de detalle de la clase
        class_id = request.form.get("class_id")
        return redirect(url_for("classes.teacher_class_detail_view", class_id=class_id))
    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def update_assignment_controller(assignment_id: int):
    """Controlador para actualizar una tarea"""
    try:
        data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "due_date": request.form.get("due_date"),
            "max_score": request.form.get("max_score", 100),
        }

        result, status_code = service.update_assignment_service(assignment_id, data)

        if status_code == 200:
            class_id = result.get("class_id")

            if class_id:
                return redirect(
                    url_for("classes.teacher_class_detail_view", class_id=class_id)
                )
            else:
                return redirect(url_for("classes.teacher_classes_view"))
        else:
            return redirect(url_for("classes.teacher_classes_view"))

    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def delete_assignment_controller(assignment_id: int):
    """Controlador para eliminar una tarea"""
    try:
        # Primero obtener el class_id antes de eliminar
        result, status_code = service.delete_assignment_service(assignment_id)

        if status_code == 200:
            class_id = result.get("class_id")

            if class_id:
                return redirect(
                    url_for("classes.teacher_class_detail_view", class_id=class_id)
                )
            else:
                return redirect(url_for("classes.teacher_classes_view"))
        else:
            return redirect(url_for("classes.teacher_classes_view"))

    except Exception:
        return redirect(url_for("classes.teacher_classes_view"))


def submit_assignment_controller():
    """Controlador para enviar una tarea como estudiante"""
    try:
        current_user_id = get_jwt_identity()

        data = {
            "assignment_id": request.form.get("assignment_id"),
            "submission_text": request.form.get("submission_text"),
        }

        file = request.files.get("submission_file")
        result, status_code = service.submit_assignment_service(
            data, current_user_id, file
        )

        # Redirigir a la vista de detalle de la clase
        class_id = request.form.get("class_id")
        return redirect(url_for("classes.student_class_detail_view", class_id=class_id))
    except Exception:
        return redirect(url_for("classes.student_classes_view"))
