from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required

from .service import (
    create_subject_service,
    delete_subject_service,
    get_course_by_id_service,
    get_subject_service,
    get_subject_with_teachers_service,
    get_teachers_for_form_service,
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

        # Load teachers list and course info from service
        teachers = get_teachers_for_form_service()
        course = get_course_by_id_service(course_id) if course_id else None

        return render_template(
            "admin/create_subject.html",
            teachers=teachers,
            course=course,
            course_id=course_id,
        )

    try:
        data = request.form.to_dict()
        course_id = int(data.get("course_id", 0)) if data.get("course_id") else None
        validated = SubjectCreateSchema(**data)
        result, status_code = create_subject_service(validated, request)

        if status_code == 201 and result:
            # If course_id is provided, create the course-subject assignment
            if course_id:
                from src.courses.service import add_subject_to_course_service
                from src.courses.validation import CourseSubjectSchema

                assignment_data = CourseSubjectSchema(
                    subject_id=result.id, teacher_id=result.teacher_id, is_active=True
                )
                _, assignment_status = add_subject_to_course_service(
                    course_id, assignment_data, request
                )

                if assignment_status in (200, 201):
                    flash("Materia creada y asignada al curso exitosamente", "success")
                else:
                    flash("Materia creada pero no se pudo asignar al curso", "warning")
            else:
                flash("Materia creada exitosamente", "success")

            # Redirect back to courses if coming from course view
            if course_id:
                return redirect(url_for("courses.courses_management"))
            return redirect(url_for("courses.courses_management"))
        elif status_code == 400:
            flash(
                "El profesor no es válido o ya está asignado a esta materia en este curso",
                "danger",
            )
        else:
            flash("Error al crear la materia", "danger")

        # Re-load form data for error display
        teachers = get_teachers_for_form_service()
        course = get_course_by_id_service(course_id) if course_id else None
        return render_template(
            "admin/create_subject.html",
            teachers=teachers,
            course=course,
            course_id=course_id,
        )

    except ValidationError as e:
        flash(f"Datos inválidos: {str(e)}", "danger")
        teachers = get_teachers_for_form_service()
        return render_template("admin/create_subject.html", teachers=teachers)
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        teachers = get_teachers_for_form_service()
        return render_template("admin/create_subject.html", teachers=teachers)


@jwt_required()
@role_required([UserRole.ADMIN])
def edit_subject_controller(subject_id: int, request: Request) -> Response:
    """View to edit a subject"""
    if request.method == "GET":
        try:
            subject, teachers, status_code = get_subject_with_teachers_service(
                subject_id, request
            )
            if status_code == 404:
                flash("Materia no encontrada", "danger")
                return redirect(url_for("courses.courses_management"))

            return render_template(
                "admin/edit_subject.html", subject=subject, teachers=teachers
            )
        except Exception as e:
            flash(f"Error al cargar la materia: {str(e)}", "danger")
            return redirect(url_for("courses.courses_management"))

    try:
        # Get subject data first in case of validation errors
        subject_data, _ = get_subject_service(subject_id, request)

        data = request.form.to_dict()
        validated = SubjectUpdateSchema(**data)
        result, status_code = update_subject_service(subject_id, validated, request)

        if status_code == 200:
            flash("Materia actualizada exitosamente", "success")
            # Redirect back to courses if coming from course view
            course_id = request.args.get("course_id")
            if course_id:
                return redirect(url_for("courses.courses_management"))
            return redirect(url_for("courses.courses_management"))
        elif status_code == 404:
            flash("Materia no encontrada", "danger")
            return redirect(url_for("courses.courses_management"))
        elif status_code == 400:
            flash(
                "El profesor no es válido o ya está asignado a esta materia en este curso",
                "danger",
            )
        else:
            flash("Error al actualizar la materia", "danger")

        # Load teachers for the form
        teachers = get_teachers_for_form_service()
        return render_template(
            "admin/edit_subject.html", subject=result, teachers=teachers
        )

    except ValidationError as e:
        flash(f"Datos inválidos: {str(e)}", "danger")
        teachers = get_teachers_for_form_service()
        return render_template(
            "admin/edit_subject.html", subject=subject_data, teachers=teachers
        )
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        teachers = get_teachers_for_form_service()
        return render_template(
            "admin/edit_subject.html", subject=subject_data, teachers=teachers
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_subject_controller(subject_id: int, request: Request) -> Response:
    """Delete a subject"""
    try:
        result, status_code = delete_subject_service(subject_id, request)

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
