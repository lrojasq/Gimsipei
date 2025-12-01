from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required
from src.courses.service import (
    get_course_students_for_view_service,
    get_courses_service,
    add_student_to_course_service,
    get_student_tasks_service,
    get_student_evaluations_service,
)
from src.courses.validation import CourseStudentSchema

from .service import (
    get_user_service,
    create_user_service,
    update_user_service,
    delete_user_service,
)
from .validation import StudentCreateSchema, UserUpdateSchema


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
            return redirect(url_for("users.dashboard"))

        return render_template(
            "teacher/students.html",
            user=current_user,
            course=course_data,
            students=students_list,
            total=len(students_list),
            accion_logout=True,
        )
    except Exception as e:
        flash(f"Error al cargar los estudiantes: {str(e)}", "danger")
        return redirect(url_for("users.dashboard"))


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
            return redirect(url_for("users.dashboard"))

        # Obtener lista de cursos para el dropdown
        courses, _ = get_courses_service()

        if request.method == "GET":
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
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
                    accion_logout=True,
                )
            else:
                flash("Error al crear el estudiante", "danger")
                return render_template(
                    "teacher/create_student.html",
                    user=current_user,
                    course=course_data,
                    courses=courses,
                    accion_logout=True,
                )

        except ValidationError:
            flash("Datos inválidos. Por favor verifique la información", "danger")
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
            )
        except Exception as e:
            flash(f"Error interno: {str(e)}", "danger")
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
            )

    except Exception as e:
        flash(f"Error al cargar el formulario: {str(e)}", "danger")
        return redirect(url_for("users.dashboard"))


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def edit_student_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Vista para editar un estudiante"""
    user_id = get_jwt_identity()

    try:
        # Obtener información del usuario actual
        current_user, status_code = get_user_service(user_id, request)
        if status_code != 200 or not current_user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("auth.login"))

        # Obtener información del curso
        course_data, _, course_status = get_course_students_for_view_service(course_id)
        if course_status == 404 or not course_data:
            flash("Curso no encontrado", "danger")
            return redirect(url_for("users.dashboard"))

        # Obtener lista de cursos para el dropdown
        courses, _ = get_courses_service()

        if request.method == "GET":
            try:
                student, status_code = get_user_service(student_id, request)
                if status_code == 404:
                    flash("Estudiante no encontrado", "danger")
                    return redirect(
                        url_for("users.course_students", course_id=course_id)
                    )
                return render_template(
                    "teacher/edit_student.html",
                    student=student,
                    user=current_user,
                    course=course_data,
                    courses=courses,
                    accion_logout=True,
                )
            except Exception as e:
                flash(f"Error al cargar el estudiante: {str(e)}", "danger")
                return redirect(url_for("users.course_students", course_id=course_id))

        try:
            # Obtener datos del estudiante primero para fallback en caso de error
            student_data, _ = get_user_service(student_id, request)
            data = request.form.to_dict()

            # Remover campo de contraseña vacío para hacerlo opcional
            if "password" in data and not data["password"].strip():
                del data["password"]

            # Validar con UserUpdateSchema
            validated = UserUpdateSchema(**data)
            _, status_code = update_user_service(student_id, validated, request)

            if status_code == 200:
                flash("Estudiante actualizado exitosamente", "success")
                return redirect(url_for("users.course_students", course_id=course_id))
            elif status_code == 404:
                flash("Estudiante no encontrado", "danger")
                return redirect(url_for("users.course_students", course_id=course_id))
            else:
                flash("Error al actualizar el estudiante", "danger")
                return render_template(
                    "teacher/edit_student.html",
                    student=student_data,
                    user=current_user,
                    course=course_data,
                    courses=courses,
                    accion_logout=True,
                )

        except ValidationError:
            flash("Datos inválidos. Por favor verifique la información", "danger")
            return render_template(
                "teacher/edit_student.html",
                student=student_data,
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
            )

        except Exception as e:
            flash(f"Error interno: {str(e)}", "danger")
            return redirect(url_for("users.course_students", course_id=course_id))

    except Exception as e:
        flash(f"Error al cargar el formulario: {str(e)}", "danger")
        return redirect(url_for("users.dashboard"))


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def delete_student_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Eliminar un estudiante de un curso"""
    try:
        current_user_id = get_jwt_identity()
        result, status_code = delete_user_service(student_id, request, current_user_id)

        if status_code == 200:
            flash("Estudiante eliminado exitosamente", "success")
        elif status_code == 404:
            flash("Estudiante no encontrado", "danger")
        elif status_code == 409:
            message = result.get(
                "message",
                "No se puede eliminar el estudiante porque tiene datos relacionados",
            )
            flash(message, "warning")
        elif status_code == 500:
            message = (
                result.get("message", "Error al eliminar el estudiante")
                if result
                else "Error al eliminar el estudiante"
            )
            flash(message, "danger")
        else:
            flash("Error al eliminar el estudiante", "danger")

    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")

    return redirect(url_for("users.course_students", course_id=course_id))


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
def student_tasks_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Vista para mostrar las tareas/clases de un estudiante específico"""
    user_id = get_jwt_identity()

    try:
        # Obtener información del usuario actual
        current_user, status_code = get_user_service(user_id, request)
        if status_code != 200 or not current_user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("auth.login"))

        # Obtener datos del curso, estudiante y tareas agrupadas por asignatura
        data, subjects_list, status_code = get_student_tasks_service(
            course_id, student_id
        )

        if status_code == 404 or not data:
            flash("Curso o estudiante no encontrado", "danger")
            return redirect(url_for("users.course_students", course_id=course_id))

        if status_code != 200:
            flash(
                f"Error al obtener las materias del curso (código: {status_code})",
                "danger",
            )
            return redirect(url_for("users.course_students", course_id=course_id))

        # Si no hay materias, mostrar mensaje pero aún así renderizar la vista
        if not subjects_list:
            flash("Este curso no tiene materias asignadas", "info")

        return render_template(
            "teacher/student_tasks.html",
            user=current_user,
            course=data["course"],
            student=data["student"],
            subjects=subjects_list,
            accion_logout=True,
        )
    except Exception as e:
        flash(f"Error al cargar las tareas: {str(e)}", "danger")
        return redirect(url_for("users.course_students", course_id=course_id))


@jwt_required()
@role_required([UserRole.TEACHER])
def student_evaluations_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Vista para mostrar las evaluaciones de un estudiante específico"""
    user_id = get_jwt_identity()
    try:
        current_user, status_code = get_user_service(user_id, request)
        if status_code != 200 or not current_user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("auth.login"))

        # Obtener datos del curso, estudiante y evaluaciones agrupadas por asignatura
        data, subjects_list, status_code = get_student_evaluations_service(
            course_id, student_id
        )

        if status_code == 404 or not data:
            flash("Curso o estudiante no encontrado", "danger")
            return redirect(url_for("users.course_students", course_id=course_id))

        if status_code != 200:
            flash(
                f"Error al obtener las evaluaciones del estudiante (código: {status_code})",
                "danger",
            )
            return redirect(url_for("users.course_students", course_id=course_id))

        return render_template(
            "teacher/student_evaluations.html",
            user=current_user,
            course=data["course"],
            student=data["student"],
            subjects=subjects_list,
            accion_logout=True,
        )
    except Exception as e:
        flash(f"Error al cargar las evaluaciones: {str(e)}", "danger")
        return redirect(url_for("users.course_students", course_id=course_id))
