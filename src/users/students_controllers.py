from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required
from src.courses.service import (
    get_course_students_for_view_service,
    get_courses_service,
    add_student_to_course_service,
)
from src.courses.validation import CourseStudentSchema

from .service import get_user_service, create_user_service
from .validation import StudentCreateSchema


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def course_students_controller(course_id: int, request: Request) -> Response:
    """Vista para mostrar estudiantes de un curso específico"""
    user_id = get_jwt_identity()

    try:
        # Obtener información del usuario actual
        current_user, status_code = get_user_service(user_id, request)
        if status_code != 200 or not current_user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("auth.login"))

        # Obtener curso y estudiantes usando el servicio
        course_data, students_list, status_code = get_course_students_for_view_service(
            course_id
        )

        if status_code == 404 or not course_data:
            flash("Curso no encontrado", "danger")
            return redirect(url_for("admin.dashboard"))

        return render_template(
            "teacher/students.html",
            user=current_user,
            course=course_data,
            students=students_list,
            total=len(students_list),
        )
    except Exception as e:
        flash(f"Error al cargar los estudiantes: {str(e)}", "danger")
        return redirect(url_for("admin.dashboard"))


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def create_student_controller(course_id: int, request: Request) -> Response:
    """Vista para crear un nuevo estudiante y asociarlo a un curso"""
    user_id = get_jwt_identity()

    try:
        # Obtener información del usuario actual
        current_user, status_code = get_user_service(user_id, request)
        if status_code != 200 or not current_user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("auth.login"))

        # Obtener información del curso
        from src.courses.service import get_course_students_for_view_service

        course_data, _, course_status = get_course_students_for_view_service(course_id)
        if course_status == 404 or not course_data:
            flash("Curso no encontrado", "danger")
            return redirect(url_for("admin.dashboard"))

        # Obtener lista de cursos para el dropdown
        courses, _ = get_courses_service()

        if request.method == "GET":
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
            )

        # POST: Crear estudiante
        try:
            data = request.form.to_dict()

            # Si no hay course_id en el formulario, usar el de la URL
            if "course_id" not in data or not data.get("course_id"):
                data["course_id"] = course_id

            # Validar con StudentCreateSchema (la conversión y validación se hace en el schema)
            student_data = StudentCreateSchema(**data)

            # Obtener el course_id seleccionado (si no viene en el schema, usar el de la URL)
            selected_course_id = student_data.course_id or course_id

            # Convertir a schema de usuario para crear el usuario
            user_data = student_data.to_user_create_schema()
            result, status_code = create_user_service(user_data, request)

            if status_code == 201 and result:
                # Asociar estudiante al curso seleccionado
                course_student_data = CourseStudentSchema(student_id=result.id)
                _, enroll_status = add_student_to_course_service(
                    selected_course_id, course_student_data, request
                )

                if enroll_status == 201:
                    flash(
                        "Estudiante creado y asociado al curso exitosamente", "success"
                    )
                    return redirect(
                        url_for("users.course_students", course_id=selected_course_id)
                    )
                elif enroll_status == 400:
                    flash(
                        "El estudiante fue creado pero ya está inscrito en este curso",
                        "warning",
                    )
                    return redirect(
                        url_for("users.course_students", course_id=selected_course_id)
                    )
                else:
                    flash(
                        "Estudiante creado pero hubo un error al asociarlo al curso",
                        "warning",
                    )
                    return redirect(
                        url_for("users.course_students", course_id=selected_course_id)
                    )
            elif status_code == 400:
                flash("El documento o nombre de usuario ya está en uso", "danger")
                return render_template(
                    "teacher/create_student.html",
                    user=current_user,
                    course=course_data,
                    courses=courses,
                )
            else:
                flash("Error al crear el estudiante", "danger")
                return render_template(
                    "teacher/create_student.html",
                    user=current_user,
                    course=course_data,
                    courses=courses,
                )

        except ValidationError:
            flash("Datos inválidos. Por favor verifique la información", "danger")
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
            )
        except Exception as e:
            flash(f"Error interno: {str(e)}", "danger")
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
            )

    except Exception as e:
        flash(f"Error al cargar el formulario: {str(e)}", "danger")
        return redirect(url_for("admin.dashboard"))
