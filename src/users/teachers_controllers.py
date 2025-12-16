from flask import Request, Response, redirect, render_template, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
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
        teachers, _ = get_users_service(role=UserRole.TEACHER)
        admins, _ = get_users_service(role=UserRole.ADMIN)
        users = teachers + admins
        total = len(users)

        # Get current user info for the template
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)

        return render_template(
            "admin/teachers_management.html",
            teachers=users,
            total=total,
            user=current_user,
            accion_logout=True,
        )
    except Exception as e:
        # Try to get current user even in error case
        try:
            current_user_id = get_jwt_identity()
            current_user, _ = get_user_service(current_user_id, request)
        except Exception:
            current_user = None
        return render_template(
            "admin/teachers_management.html",
            teachers=[],
            total=0,
            user=current_user,
            accion_logout=True,
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def create_teacher_controller(request: Request) -> Response:
    """View to create a new teacher"""
    if request.method == "GET":
        # Get current user info for the template
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)
        return render_template(
            "admin/create_teacher.html", user=current_user, accion_logout=True
        )

    try:
        data = request.form.to_dict()
        validated = UserCreateSchema(**data)
        result, status_code = create_user_service(validated, request)

        if status_code == 201 and result:
            return redirect(url_for("users.teachers_management"))
        elif status_code == 400:
            # Get current user info for the template
            current_user_id = get_jwt_identity()
            current_user, _ = get_user_service(current_user_id, request)
            return render_template(
                "admin/create_teacher.html", user=current_user, accion_logout=True
            )
        else:
            # Get current user info for the template
            current_user_id = get_jwt_identity()
            current_user, _ = get_user_service(current_user_id, request)
            return render_template(
                "admin/create_teacher.html", user=current_user, accion_logout=True
            )

    except ValidationError:
        # Get current user info for the template
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)
        return render_template(
            "admin/create_teacher.html", user=current_user, accion_logout=True
        )
    except Exception as e:
        # Get current user info for the template
        current_user_id = get_jwt_identity()
        current_user, _ = get_user_service(current_user_id, request)
        return render_template(
            "admin/create_teacher.html", user=current_user, accion_logout=True
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def edit_teacher_controller(teacher_id: int, request: Request) -> Response:
    """View to edit a teacher"""
    current_user_id = get_jwt_identity()
    current_user, _ = get_user_service(current_user_id, request)
    if request.method == "GET":
        try:
            teacher, status_code = get_user_service(teacher_id, request)
            if status_code == 404:
                return redirect(url_for("users.teachers_management"))
            return render_template(
                "admin/edit_teacher.html",
                teacher=teacher,
                user=current_user,
                accion_logout=True,
            )
        except Exception as e:
            return redirect(url_for("users.teachers_management"))

    try:
        # Get teacher data first in case of validation/errors fallback
        teacher_data, _ = get_user_service(teacher_id, request)

        data = request.form.to_dict()

        # Remove empty password field to make it optional
        if "password" in data and not data["password"].strip():
            del data["password"]

        # Normalize role to lowercase
        if "role" in data and isinstance(data["role"], str):
            data["role"] = data["role"].lower()

        validated = UserUpdateSchema(**data)
        _, status_code = update_user_service(teacher_id, validated, request)

        if status_code == 200:
            return redirect(url_for("users.teachers_management"))
        elif status_code == 404:
            return redirect(url_for("users.teachers_management"))
        else:
            return render_template(
                "admin/edit_teacher.html",
                teacher=teacher_data,
                user=current_user,
                accion_logout=True,
            )

    except ValidationError:
        return render_template(
            "admin/edit_teacher.html",
            teacher=teacher_data,
            user=current_user,
            accion_logout=True,
        )

    except Exception as e:
        return redirect(url_for("users.teachers_management"))


@jwt_required()
@role_required([UserRole.ADMIN])
def delete_teacher_controller(teacher_id: int, request: Request) -> Response:
    """Delete a teacher or admin (only admins can do this)"""
    try:
        current_user_id = get_jwt_identity()
        result, status_code = delete_user_service(teacher_id, request, current_user_id)

        # Flash messages removidos por requerimiento del cliente.

    except Exception as e:
        pass

    return redirect(url_for("users.teachers_management"))
