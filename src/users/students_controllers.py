from flask import Request, Response, redirect, render_template, url_for
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
            return redirect(url_for("auth.login"))

        # Obtener curso y estudiantes usando el servicio
        course_data, students_list, status_code = get_course_students_for_view_service(
            course_id
        )

        if status_code == 404 or not course_data:
            return redirect(url_for("users.dashboard"))

        return render_template(
            "teacher/students.html",
            user=current_user,
            course=course_data,
            students=students_list,
            total=len(students_list),
            accion_logout=True,
        )
    except Exception:
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
            return redirect(url_for("auth.login"))

        # Obtener información del curso
        from src.courses.service import get_course_students_for_view_service

        course_data, _, course_status = get_course_students_for_view_service(course_id)
        if course_status == 404 or not course_data:
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
                    return redirect(
                        url_for("users.course_students", course_id=selected_course_id)
                    )
                elif enroll_status == 400:
                    return redirect(
                        url_for("users.course_students", course_id=selected_course_id)
                    )
                else:
                    return redirect(
                        url_for("users.course_students", course_id=selected_course_id)
                    )
            elif status_code == 400:
                return render_template(
                    "teacher/create_student.html",
                    user=current_user,
                    course=course_data,
                    courses=courses,
                    accion_logout=True,
                )
            else:
                return render_template(
                    "teacher/create_student.html",
                    user=current_user,
                    course=course_data,
                    courses=courses,
                    accion_logout=True,
                )

        except ValidationError:
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
            )
        except Exception:
            return render_template(
                "teacher/create_student.html",
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
            )

    except Exception:
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
            return redirect(url_for("auth.login"))

        # Obtener información del curso
        course_data, _, course_status = get_course_students_for_view_service(course_id)
        if course_status == 404 or not course_data:
            return redirect(url_for("users.dashboard"))

        # Obtener lista de cursos para el dropdown
        courses, _ = get_courses_service()

        if request.method == "GET":
            try:
                student, status_code = get_user_service(student_id, request)
                if status_code == 404:
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
            except Exception:
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
                return redirect(url_for("users.course_students", course_id=course_id))
            elif status_code == 404:
                return redirect(url_for("users.course_students", course_id=course_id))
            else:
                return render_template(
                    "teacher/edit_student.html",
                    student=student_data,
                    user=current_user,
                    course=course_data,
                    courses=courses,
                    accion_logout=True,
                )

        except ValidationError:
            return render_template(
                "teacher/edit_student.html",
                student=student_data,
                user=current_user,
                course=course_data,
                courses=courses,
                accion_logout=True,
            )

        except Exception:
            return redirect(url_for("users.course_students", course_id=course_id))

    except Exception:
        return redirect(url_for("users.dashboard"))


@jwt_required()
@role_required([UserRole.TEACHER])
def delete_student_controller(
    course_id: int, student_id: int, request: Request
) -> Response:
    """Eliminar un estudiante de un curso"""
    try:
        current_user_id = get_jwt_identity()
        delete_user_service(student_id, request, current_user_id)
    except Exception:
        pass

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
            return redirect(url_for("auth.login"))

        # Obtener datos del curso, estudiante y tareas agrupadas por asignatura
        data, subjects_list, status_code = get_student_tasks_service(
            course_id, student_id
        )

        if status_code == 404 or not data:
            return redirect(url_for("users.course_students", course_id=course_id))

        if status_code != 200:
            return redirect(url_for("users.course_students", course_id=course_id))

        # Si no hay materias, mostrar mensaje pero aún así renderizar la vista
        if not subjects_list:
            pass

        return render_template(
            "teacher/student_tasks.html",
            user=current_user,
            course=data["course"],
            student=data["student"],
            subjects=subjects_list,
            accion_logout=True,
        )
    except Exception:
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
            return redirect(url_for("auth.login"))

        # Obtener datos del curso, estudiante y evaluaciones agrupadas por asignatura
        data, subjects_list, status_code = get_student_evaluations_service(
            course_id, student_id
        )

        if status_code == 404 or not data:
            return redirect(url_for("users.course_students", course_id=course_id))

        if status_code != 200:
            return redirect(url_for("users.course_students", course_id=course_id))

        return render_template(
            "teacher/student_evaluations.html",
            user=current_user,
            course=data["course"],
            student=data["student"],
            subjects=subjects_list,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.course_students", course_id=course_id))
