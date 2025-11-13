from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from src.models.user import UserRole
from src.utils.decorator_role_required import role_required
from src.courses.service import get_all_courses_for_dashboard
from src.users.service import get_user_service


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def dashboard_controller(_: Request) -> Response:
    user_id = get_jwt_identity()
    user_role = get_jwt().get("role")

    try:
        # Obtener información del usuario
        user, status_code = get_user_service(user_id, _)
        if status_code != 200 or not user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("auth.login"))

        # User is admin
        if user_role == "ADMIN":
            return render_template(
                "admin/dashboard.html",
                user={
                    "id": user.id,
                    "full_name": user.full_name,
                    "document": user.document,
                    "role": user_role,
                },
                accion_logout=True,
            )

        # User is teacher
        elif user_role == "TEACHER":
            courses_list = get_all_courses_for_dashboard()

            return render_template(
                "admin/dashboard.html",
                user={
                    "id": user.id,
                    "full_name": user.full_name,
                    "document": user.document,
                    "role": user_role,
                },
                courses=courses_list,
                accion_logout=True,
            )

        # User is student
        else:
            return render_template("about_us.html", accion_logout=True)
    except Exception:
        flash("Error al obtener el dashboard", "danger")
        return redirect(url_for("auth.login"))


# Son temporales, se deben cambiar a sus respectivos modulos
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
# def materias_controller(request: Request) -> Response:
#     return render_template("category/materias.html", accion_logout=True)


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def evaluaciones_controller(request: Request) -> Response:
    return render_template("category/evaluaciones.html", accion_logout=True)


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def libros_controller(request: Request) -> Response:
    return render_template("category/libros.html", accion_logout=True)


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def calificaciones_controller(request: Request) -> Response:
    return render_template("category/calificaciones.html", accion_logout=True)
