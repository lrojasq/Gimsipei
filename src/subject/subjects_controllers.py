from flask import Request, Response, redirect, render_template, url_for
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
        subject_id = int(data.get("subject_id", 0)) if data.get("subject_id") else None
        teacher_id = int(data.get("teacher_id", 0)) if data.get("teacher_id") else None

        # 1) Resolver/crear la materia por nombre (siempre viene del modal)
        subject_name = data.get("name")
        if not subject_name:
            return redirect(url_for("courses.courses_management"))

        validated_subject = SubjectCreateSchema(name=subject_name)
        subject_result, subject_status = create_subject_service(
            validated_subject, request
        )

        if subject_status not in (200, 201) or not subject_result:
            return redirect(url_for("courses.courses_management"))

        # 2) Si viene course_id + teacher_id, asignar/actualizar en el curso
        if course_id and teacher_id:
            from src.courses.service import add_subject_to_course_service
            from src.courses.validation import CourseSubjectSchema

            assignment_data = CourseSubjectSchema(
                subject_id=subject_result.id,  # subject destino
                teacher_id=teacher_id,
                is_active=True,
                original_subject_id=subject_id
                or None,  # subject original (para edición)
            )
            _, assignment_status = add_subject_to_course_service(
                course_id, assignment_data, request
            )

            if assignment_status in (200, 201):
                if subject_id:
                    pass
                else:
                    pass
            elif assignment_status == 400:
                pass
            elif assignment_status == 404:
                pass
            else:
                pass

            return redirect(url_for("courses.courses_management"))

        # 3) Si no viene course_id/teacher_id, es solo creación de materia global
        if subject_status == 201:
            pass
        else:
            pass

        return redirect(url_for("courses.courses_management"))

    except ValidationError:
        return redirect(url_for("courses.courses_management"))
    except Exception:
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
            pass
        elif status_code == 404:
            pass
        elif status_code == 400:
            pass
        else:
            pass

        return redirect(url_for("courses.courses_management"))

    except ValidationError:
        return redirect(url_for("courses.courses_management"))
    except Exception:
        return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_subject_controller(subject_id: int, request: Request) -> Response:
    """Delete a subject"""
    try:
        _, status_code = delete_subject_service(subject_id, request)

        if status_code == 200:
            pass
        elif status_code == 404:
            pass
        else:
            pass

    except Exception:
        pass

    # Redirect back to courses if coming from course view
    course_id = request.args.get("course_id")
    if course_id:
        return redirect(url_for("courses.courses_management"))
    return redirect(url_for("courses.courses_management"))
