from flask import Request, Response, flash, redirect, render_template, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from src.database.database import SessionLocal
from src.models.user import User, UserRole

# from src.models.course import Course
from src.utils.decorator_role_required import role_required


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def dashboard_controller(request: Request) -> Response:
    user_id = get_jwt_identity()
    user_role = get_jwt().get("role")

    try:
        db = SessionLocal()
        user = (
            db.query(User.id, User.full_name, User.document, User.role)
            .filter(User.id == user_id)
            .first()
        )
        db.close()

        if not user:
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
                    "role": user_role
                },
                accion_logout=True,
            )

        # User is teacher
        elif user_role == "TEACHER":
            # Grados en los que pertenece
            # grades = db.query(Course.grade_level).filter(Course.teacher_id == user_id).all()
            # grades = [grade.grade_level for grade in grades]
            grades = [6, 7, 8, 9, 10, 11]
            return render_template(
                "admin/dashboard.html",
                user={
                    "id": user.id,
                    "full_name": user.full_name,
                    "document": user.document,
                    "role": user_role
                },
                grades=grades,
                accion_logout=True,
            )

        # User is student
        else:
            return render_template("about_us.html", accion_logout=True)
    except Exception as e:
        print(e)
        flash("Error al obtener el dashboard", "danger")
        return redirect(url_for("auth.login"))


# Son temporales, se deben cambiar a sus respectivos modulos
# @jwt_required()
# @role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
# def materias_controller(request: Request) -> Response:
#     return render_template("category/materias.html", accion_logout=True)


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def clases_recursos_controller(request: Request) -> Response:
    return render_template("category/clases-recursos.html", accion_logout=True)


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
