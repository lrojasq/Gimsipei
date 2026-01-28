from flask import Request, Response, redirect, render_template, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.subject.service import (
    get_available_subject_names,
    get_teachers_for_form_service,
)
from src.users.service import get_user_service
from src.utils.decorator_role_required import role_required

from .service import (
    create_course_service,
    delete_course_service,
    get_available_course_names,
    get_course_subjects_service,
    get_courses_service,
    remove_student_from_course_service,
)
from .validation import CourseCreateSchema


# View to manage courses
@jwt_required()
@role_required([UserRole.ADMIN])
def courses_management_controller(_: Request) -> Response:
    """View to manage courses"""
    current_user = None
    try:
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, _)

        courses, total = get_courses_service()
        available_courses = get_available_course_names()
        teachers = get_teachers_for_form_service()
        available_subjects = get_available_subject_names()
        courses_with_subjects = []

        for course in courses:
            subjects, _ = get_course_subjects_service(course.id)
            course_dict = {
                "id": course.id,
                "academic_year": course.academic_year,
                "name": course.name,
                "created_by": course.created_by,
                "created_at": course.created_at,
                "updated_at": course.updated_at,
                "subjects": subjects,
            }
            courses_with_subjects.append(course_dict)

        return render_template(
            "admin/courses_management.html",
            courses=courses_with_subjects,
            total=total,
            user=current_user,
            available_courses=available_courses,
            teachers=teachers,
            available_subjects=available_subjects,
            accion_logout=True,
        )
    except Exception:
        return render_template(
            "admin/courses_management.html",
            courses=[],
            total=0,
            user=current_user,
            available_courses=[],
            teachers=[],
            available_subjects=[],
            accion_logout=True,
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def create_course_controller(request: Request) -> Response:
    """View to create a new course"""
    if request.method == "GET":
        return redirect(url_for("courses.courses_management"))

    try:
        data = request.form.to_dict()
        validated = CourseCreateSchema(**data)
        result, status_code = create_course_service(validated, request)

        if status_code == 201 and result:
            return redirect(url_for("courses.courses_management"))
        elif status_code == 400:
            return redirect(url_for("courses.courses_management"))
        else:
            return redirect(url_for("courses.courses_management"))

    except ValidationError:
        return redirect(url_for("courses.courses_management"))
    except Exception:
        return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_course_controller(course_id: int, request: Request) -> Response:
    """Delete a course"""
    try:
        result, status_code = delete_course_service(course_id, request)
    except Exception:
        pass

    return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def remove_student_from_course_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Remove a student from a course via HTML POST"""
    try:
        result, status_code = remove_student_from_course_service(
            course_id, student_id, request
        )

        if status_code == 200:
            pass
        elif status_code == 404:
            pass
        else:
            pass
    except Exception:
        pass

    return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def remove_subject_from_course_controller(
    course_id: int, subject_id: int, teacher_id: int, request: Request
) -> Response:
    """Remove a subject assignment from a course via HTML POST"""
    try:
        from .service import remove_subject_from_course_service

        _, status_code = remove_subject_from_course_service(
            course_id, subject_id, teacher_id, request
        )

        if status_code == 200:
            pass
        elif status_code == 404:
            pass
        else:
            pass
    except Exception:
        pass

    return redirect(url_for("courses.courses_management"))
