from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required

from .service import (
    create_user_service,
    delete_user_service,
    get_user_service,
    get_users_service,
    update_user_service,
)
from .validation import UserCreateSchema, UserUpdateSchema


# View to manage teachers
@jwt_required()
@role_required([UserRole.ADMIN])
def teachers_management_controller(request: Request) -> Response:
    """View to manage teachers"""
    try:
        users, total = get_users_service(role=UserRole.TEACHER)
        
        return render_template("admin/teachers_management.html", teachers=users, total=total)
    except Exception as e:
        flash(f"Error al cargar la lista de docentes: {str(e)}", "danger")
        return render_template("admin/teachers_management.html", teachers=[], total=0)


@jwt_required()
@role_required([UserRole.ADMIN])
def create_teacher_controller(request: Request) -> Response:
    """View to create a new teacher"""
    if request.method == "GET":
        return render_template("admin/create_teacher.html")

    try:
        data = request.form.to_dict()
        data["role"] = UserRole.TEACHER  # Forzar rol de docente
        validated = UserCreateSchema(**data)
        result, status_code = create_user_service(validated, request)

        if status_code == 201 and result:
            flash("Docente creado exitosamente", "success")
            return redirect(url_for("users.teachers_management"))
        elif status_code == 400:
            flash("El email o nombre de usuario ya está en uso", "danger")
            return render_template("admin/create_teacher.html")
        else:
            flash("Error al crear el docente", "danger")
            return render_template("admin/create_teacher.html")

    except ValidationError:
        flash("Datos inválidos. Por favor verifique la información", "danger")
        return render_template("admin/create_teacher.html")
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        return render_template("admin/create_teacher.html")


@jwt_required()
@role_required([UserRole.ADMIN])
def edit_teacher_controller(teacher_id: int, request: Request) -> Response:
    """View to edit a teacher"""
    if request.method == "GET":
        try:
            teacher, status_code = get_user_service(teacher_id, request)
            
            if status_code == 404:
                flash("Docente no encontrado", "danger")
                return redirect(url_for("users.teachers_management"))
            return render_template("admin/edit_teacher.html", teacher=teacher)
        except Exception as e:
            flash(f"Error al cargar el docente: {str(e)}", "danger")
            return redirect(url_for("users.teachers_management"))

    try:
        # Get teacher data first in case of validation errors
        teacher_data, _ = get_user_service(teacher_id, request)

        data = request.form.to_dict()

        # Remove empty password field to make it optional
        if "password" in data and not data["password"].strip():
            del data["password"]

        validated = UserUpdateSchema(**data)
        result, status_code = update_user_service(teacher_id, validated, request)

        if status_code == 200:
            flash("Docente actualizado exitosamente", "success")
            return redirect(url_for("users.teachers_management"))
        elif status_code == 404:
            flash("Docente no encontrado", "danger")
            return redirect(url_for("users.teachers_management"))
        else:
            flash("Error al actualizar el docente", "danger")
            return render_template("admin/edit_teacher.html", teacher=result)

    except ValidationError:
        flash("Datos inválidos. Por favor verifique la información", "danger")
        return render_template("admin/edit_teacher.html", teacher=teacher_data)
    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")
        return render_template("admin/edit_teacher.html", teacher=teacher_data)


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_teacher_controller(teacher_id: int, request: Request) -> Response:
    """Delete a teacher"""
    try:
        result, status_code = delete_user_service(teacher_id, request)

        if status_code == 200:
            flash("Docente eliminado exitosamente", "success")
        elif status_code == 404:
            flash("Docente no encontrado", "danger")
        else:
            flash("Error al eliminar el docente", "danger")

    except Exception as e:
        flash(f"Error interno: {str(e)}", "danger")

    return redirect(url_for("users.teachers_management"))
