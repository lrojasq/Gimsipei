from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required

from .service import (
    create_subject_service,
    delete_subject_service,
    get_course_by_id_service,
    get_teachers_for_form_service,
    get_available_subject_names,
    update_subject_service,
)
from .validation import SubjectCreateSchema, SubjectUpdateSchema


@jwt_required()
@role_required([UserRole.ADMIN])
def create_subject_controller(request: Request) -> Response:
    """View to create a new subject"""
    if request.method == "GET":
        # Get course_id from query parameter
        course_id = (
            int(request.args.get("course_id", 0))
            if request.args.get("course_id")
            else None
        )

        # Load teachers list, available subjects, and course info from service
        teachers = get_teachers_for_form_service()
        available_subjects = get_available_subject_names()
        course = get_course_by_id_service(course_id) if course_id else None

        return render_template(
            "admin/create_subject.html",
            teachers=teachers,
            available_subjects=available_subjects,
            course=course,
            course_id=course_id,
            accion_logout=True,
        )

    try:
        data = request.form.to_dict()
        course_id = int(data.get("course_id", 0)) if data.get("course_id") else None
        validated = SubjectCreateSchema(**data)
        result, status_code = create_subject_service(validated, request)

        # 200: materia existente, 201: materia nueva
        if status_code in (200, 201) and result:
            # If course_id and teacher_id are provided, create the course-subject-teacher assignment
            if course_id and data.get("teacher_id"):
                from src.courses.service import add_subject_to_course_service
                from src.courses.validation import CourseSubjectSchema

                assignment_data = CourseSubjectSchema(
                    subject_id=result.id,
                    teacher_id=int(data.get("teacher_id")),
                    is_active=True,
                )
                _, assignment_status = add_subject_to_course_service(
                    course_id, assignment_data, request
                )

                if assignment_status in (200, 201):
                    if status_code == 201:
                        flash(
                            "Materia creada y asignada al curso exitosamente", "success"
                        )
                    else:
                        flash("Materia asignada al curso exitosamente", "success")
                elif assignment_status == 400:
                    flash(
                        "Esta materia ya está asignada a este curso con el mismo profesor",
                        "danger",
                    )
                else:
                    if status_code == 201:
                        flash(
                            "Materia creada pero no se pudo asignar al curso", "warning"
                        )
                    else:
                        flash("No se pudo asignar la materia al curso", "warning")
            else:
                if status_code == 201:
                    flash("Materia creada exitosamente", "success")
                else:
                    flash("Materia ya existe en el sistema", "info")

            # Redirect back to courses if coming from course view
            if course_id:
                return redirect(url_for("courses.courses_management"))
            return redirect(url_for("courses.courses_management"))
        elif status_code == 400:
            flash(
                "Ya existe una materia con ese nombre o el profesor no es válido",
                "danger",
            )
        else:
            flash("Error al crear la materia", "danger")

        return redirect(url_for("courses.courses_management"))

    except ValidationError as e:
        flash(f"Datos inválidos: {str(e)}", "danger")
        return redirect(url_for("courses.courses_management"))
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def edit_subject_controller(subject_id: int, request: Request) -> Response:
    """View to edit a subject"""
    if request.method == "GET":
        return redirect(url_for("courses.courses_management"))

    try:
        data = request.form.to_dict()
        validated = SubjectUpdateSchema(**data)
        result, status_code = update_subject_service(subject_id, validated, request)

        if status_code == 200:
            flash("Materia actualizada exitosamente", "success")
        elif status_code == 404:
            flash("Materia no encontrada", "danger")
        elif status_code == 400:
            flash("Ya existe una materia con ese nombre", "danger")
        else:
            flash("Error al actualizar la materia", "danger")

        return redirect(url_for("courses.courses_management"))

    except ValidationError as e:
        flash(f"Datos inválidos: {str(e)}", "danger")
        return redirect(url_for("courses.courses_management"))
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_subject_controller(subject_id: int, request: Request) -> Response:
    """Delete a subject"""
    try:
        _, status_code = delete_subject_service(subject_id, request)

        if status_code == 200:
            flash("Materia eliminada exitosamente", "success")
        elif status_code == 404:
            flash("Materia no encontrada", "danger")
        else:
            flash("Error al eliminar la materia", "danger")

    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")

    # Redirect back to courses if coming from course view
    course_id = request.args.get("course_id")
    if course_id:
        return redirect(url_for("courses.courses_management"))
    return redirect(url_for("courses.courses_management"))
