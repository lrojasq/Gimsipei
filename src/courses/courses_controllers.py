from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required

from .service import (
    create_course_service,
    delete_course_service,
    get_course_service,
    get_courses_service,
    update_course_service,
)
from .validation import CourseCreateSchema, CourseUpdateSchema


# View to manage courses
@jwt_required()
@role_required([UserRole.ADMIN])
def courses_management_controller(request: Request) -> Response:
    """View to manage courses"""
    try:
        courses, total = get_courses_service()
        # Load subjects for each course
        from .service import get_course_subjects_service

        courses_with_subjects = []

        for course in courses:
            subjects, _ = get_course_subjects_service(course.id)
            course_dict = {
                "id": course.id,
                "academic_year": course.academic_year,
                "period": course.period,
                "grade_level": course.grade_level,
                "name": course.name,
                "is_active": course.is_active,
                "created_by": course.created_by,
                "created_at": course.created_at,
                "updated_at": course.updated_at,
                "subjects": subjects,
            }
            courses_with_subjects.append(course_dict)

        return render_template(
            "admin/courses_management.html", courses=courses_with_subjects, total=total
        )
    except Exception as e:
        flash(f"Error al cargar la lista de cursos: {str(e)}", "danger")
        return render_template("admin/courses_management.html", courses=[], total=0)


@jwt_required()
@role_required([UserRole.ADMIN])
def create_course_controller(request: Request) -> Response:
    """View to create a new course"""
    if request.method == "GET":
        return render_template("admin/create_course.html")

    try:
        data = request.form.to_dict()
        validated = CourseCreateSchema(**data)
        result, status_code = create_course_service(validated, request)

        if status_code == 201 and result:
            flash("Curso creado exitosamente", "success")
            return redirect(url_for("courses.courses_management"))
        elif status_code == 400:
            flash(
                "Ya existe un curso con ese nombre en el mismo año y período", "danger"
            )
            return render_template("admin/create_course.html")
        else:
            flash("Error al crear el curso", "danger")
            return render_template("admin/create_course.html")

    except ValidationError as e:
        flash(f"Datos inválidos: {str(e)}", "danger")
        return render_template("admin/create_course.html")
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        return render_template("admin/create_course.html")


@jwt_required()
@role_required([UserRole.ADMIN])
def edit_course_controller(course_id: int, request: Request) -> Response:
    """View to edit a course"""
    if request.method == "GET":
        try:
            course, status_code = get_course_service(course_id, request)
            if status_code == 404:
                flash("Curso no encontrado", "danger")
                return redirect(url_for("courses.courses_management"))
            return render_template("admin/edit_course.html", course=course)
        except Exception as e:
            flash(f"Error al cargar el curso: {str(e)}", "danger")
            return redirect(url_for("courses.courses_management"))

    try:
        # Get course data first in case of validation errors
        course_data, _ = get_course_service(course_id, request)

        data = request.form.to_dict()
        validated = CourseUpdateSchema(**data)
        result, status_code = update_course_service(course_id, validated, request)

        if status_code == 200:
            flash("Curso actualizado exitosamente", "success")
            return redirect(url_for("courses.courses_management"))
        elif status_code == 404:
            flash("Curso no encontrado", "danger")
            return redirect(url_for("courses.courses_management"))
        elif status_code == 400:
            flash(
                "Ya existe un curso con ese nombre en el mismo año y período", "danger"
            )
            return render_template("admin/edit_course.html", course=result)
        else:
            flash("Error al actualizar el curso", "danger")
            return render_template("admin/edit_course.html", course=result)

    except ValidationError as e:
        flash(f"Datos inválidos: {str(e)}", "danger")
        return render_template("admin/edit_course.html", course=course_data)
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        return render_template("admin/edit_course.html", course=course_data)


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_course_controller(course_id: int, request: Request) -> Response:
    """Delete a course"""
    try:
        result, status_code = delete_course_service(course_id, request)

        if status_code == 200:
            flash("Curso eliminado exitosamente", "success")
        elif status_code == 404:
            flash("Curso no encontrado", "danger")
        else:
            flash("Error al eliminar el curso", "danger")

    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")

    return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def course_detail_controller(course_id: int, request: Request) -> Response:
    """Detailed view of a course with students and subjects"""
    try:
        course, status_code = get_course_service(course_id, request)
        if status_code == 404:
            flash("Curso no encontrado", "danger")
            return redirect(url_for("courses.courses_management"))

        # Get course students
        from .service import get_course_students_service

        students, _ = get_course_students_service(course_id)

        # Get course subjects
        from .service import get_course_subjects_service

        subjects, _ = get_course_subjects_service(course_id)

        return render_template(
            "admin/course_detail.html",
            course=course,
            students=students,
            subjects=subjects,
        )
    except Exception as e:
        flash(f"Error al cargar el detalle del curso: {str(e)}", "danger")
        return redirect(url_for("courses.courses_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def remove_student_from_course_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Remove a student from a course via HTML POST"""
    try:
        from .service import remove_student_from_course_service

        result, status_code = remove_student_from_course_service(
            course_id, student_id, request
        )

        if status_code == 200:
            flash("Estudiante removido del curso exitosamente", "success")
        elif status_code == 404:
            flash("Inscripción no encontrada", "danger")
        else:
            flash("No se pudo remover el estudiante", "danger")
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")

    return redirect(url_for("courses.course_detail", course_id=course_id))


@jwt_required()
@role_required([UserRole.ADMIN])
def remove_subject_from_course_controller(
    course_id: int, subject_id: int, teacher_id: int, request: Request
) -> Response:
    """Remove a subject assignment from a course via HTML POST"""
    try:
        from .service import remove_subject_from_course_service

        result, status_code = remove_subject_from_course_service(
            course_id, subject_id, teacher_id, request
        )

        if status_code == 200:
            flash("Materia removida del curso exitosamente", "success")
        elif status_code == 404:
            flash("Asignación no encontrada", "danger")
        else:
            flash("No se pudo remover la materia", "danger")
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")

    return redirect(url_for("courses.course_detail", course_id=course_id))
