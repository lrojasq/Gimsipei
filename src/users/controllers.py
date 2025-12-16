from typing import Optional, Tuple

from flask import (
    Request,
    Response,
    redirect,
    render_template,
    url_for,
    request as flask_request,
    jsonify,
)
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from pydantic import ValidationError

from src.database.database import SessionLocal
from src.models.user import User, UserRole
from src.utils.api_response import ApiResponse
from src.utils.decorator_role_required import role_required
from src.utils.normalize_role_field import normalize_role_field
from src.courses.service import get_all_courses_for_dashboard

from .service import (
    create_user_service,
    delete_user_service,
    get_user_service,
    get_users_service,
    update_user_service,
)
from .validation import UserCreateSchema, UserResponseSchema, UserUpdateSchema


AVATAR_FILES = [
    "oveja.png",
    "buho.png",
    "hipopotamo.png",
    "oso-polar.png",
    "coati.png",
    "zorro.png",
    "zorillo.png",
    "vaca.png",
    "perro.png",
    "perro-mini.png",
    "elefante.png",
    "marrano.png",
    "leon.png",
    "mico.png",
    "pato.png",
    "oso-negro.png",
    "tucan.png",
    "raton.png",
    "oso-miel.png",
    "oveja-lana.png",
    "marrano-cenu.png",
    "tigre.png",
    "cohala.png",
    "conejo.png",
]


@jwt_required()
@role_required([UserRole.ADMIN])
def get_users_controller(request: Request) -> Response | Tuple[list, int]:
    try:
        # Solo obtener usuarios con rol TEACHER
        users, total = get_users_service(role=UserRole.TEACHER)
        return ApiResponse.list_response(
            items=[user.dict() for user in users],
            total=total,
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener la lista de docentes",
            details=str(e),
            status_code=500,
        )


@jwt_required()
def get_user_controller(
    user_id: int, request: Request
) -> Response | Tuple[Optional[UserResponseSchema], int]:
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()
        current_user = db.query(User).get(current_user_id)
        db.close()
        # Solo admin o el propio usuario pueden ver el perfil
        if not current_user or (
            current_user.role != UserRole.ADMIN and current_user.id != user_id
        ):
            return ApiResponse.error(message="No autorizado", status_code=403)
        result, status_code = get_user_service(user_id, request)

        if status_code == 404:
            return ApiResponse.error(message="Usuario no encontrado", status_code=404)

        return ApiResponse.success(data=result, message="Usuario obtenido exitosamente")
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener el usuario", details=str(e), status_code=500
        )


@jwt_required()
@role_required(UserRole.ADMIN)
@normalize_role_field
def create_user_controller(
    request: Request,
) -> Response | Tuple[Optional[UserResponseSchema], int]:
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        validated = UserCreateSchema(**data)
        result, status_code = create_user_service(validated, request)

        if status_code == 201 and result:
            return ApiResponse.success(
                data=result, message="Usuario creado exitosamente", status_code=201
            )
        elif status_code == 400:
            return ApiResponse.error(
                message="Error al crear el usuario",
                details="El email o username ya está en uso",
                status_code=400,
            )
        else:
            return ApiResponse.error(
                message="Error al crear el usuario",
                details="Error interno del servidor",
                status_code=500,
            )

    except ValidationError as e:
        return ApiResponse.error(
            message="Datos inválidos", details=e.errors(), status_code=400
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER])
@normalize_role_field
def update_user_controller(
    user_id: int, request: Request
) -> Response | Tuple[Optional[UserResponseSchema], int]:
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        validated = UserUpdateSchema(**data)
        result, status_code = update_user_service(user_id, validated, request)

        if status_code == 200:
            return ApiResponse.success(
                data=result, message="Usuario actualizado exitosamente"
            )
        elif status_code == 404:
            return ApiResponse.error(message="Usuario no encontrado", status_code=404)
        else:
            return ApiResponse.error(
                message="Error al actualizar el usuario",
                details="Error interno del servidor",
                status_code=500,
            )

    except ValidationError as e:
        return ApiResponse.error(
            message="Datos inválidos", details=e.errors(), status_code=400
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


@jwt_required()
@role_required(UserRole.ADMIN)
def delete_user_controller(
    user_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    try:
        current_user_id = get_jwt_identity()
        _, status_code = delete_user_service(user_id, request, current_user_id)

        if status_code == 200:
            return ApiResponse.success(message="Usuario eliminado exitosamente")
        elif status_code == 404:
            return ApiResponse.error(message="Usuario no encontrado", status_code=404)
        else:
            return ApiResponse.error(
                message="Error al eliminar el usuario",
                details="Error interno del servidor",
                status_code=500,
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def profile_view_controller(request: Request) -> Response:
    """Vista de perfil con selección de avatar para cualquier rol"""
    user_id = get_jwt_identity()

    try:
        user, status_code = get_user_service(user_id, request)
        if status_code != 200 or not user:
            return redirect(url_for("auth.login"))

        if flask_request.method == "POST":
            if flask_request.is_json:
                selected_avatar = (flask_request.get_json() or {}).get("avatar")
            else:
                selected_avatar = flask_request.form.get("avatar")

            if selected_avatar not in AVATAR_FILES:
                if flask_request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return (
                        jsonify(
                            {"status": "error", "message": "Avatar no válido"},
                        ),
                        400,
                    )
                return redirect(url_for("users.profile"))

            try:
                update_data = UserUpdateSchema(avatar=selected_avatar)
                _, update_status = update_user_service(user_id, update_data, request)

                if update_status == 200:
                    if (
                        flask_request.headers.get("X-Requested-With")
                        == "XMLHttpRequest"
                    ):
                        return jsonify(
                            {"status": "success", "avatar": selected_avatar}
                        ), 200
                else:
                    if (
                        flask_request.headers.get("X-Requested-With")
                        == "XMLHttpRequest"
                    ):
                        return (
                            jsonify(
                                {
                                    "status": "error",
                                    "message": "Error al actualizar el avatar",
                                }
                            ),
                            500,
                        )
            except Exception:
                if flask_request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return (
                        jsonify(
                            {
                                "status": "error",
                                "message": "Error al actualizar el avatar",
                            }
                        ),
                        500,
                    )

            return redirect(url_for("users.profile"))

        # GET
        return render_template(
            "admin/datos_personales.html",
            user=user,
            avatars=AVATAR_FILES,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def dashboard_controller(_: Request) -> Response:
    user_id = get_jwt_identity()
    user_role = get_jwt().get("role")

    try:
        # Obtener información del usuario
        user, status_code = get_user_service(user_id, _)
        if status_code != 200 or not user:
            return redirect(url_for("auth.login"))

        # User is admin
        if user_role == "admin":
            return render_template(
                "admin/dashboard.html",
                user={
                    "id": user.id,
                    "full_name": user.full_name,
                    "document": user.document,
                    "avatar": getattr(user, "avatar", None),
                    "role": user_role,
                },
                accion_logout=True,
            )

        # User is teacher
        elif user_role == "teacher":
            courses_list = get_all_courses_for_dashboard()

            return render_template(
                "admin/dashboard.html",
                user={
                    "id": user.id,
                    "full_name": user.full_name,
                    "document": user.document,
                    "avatar": getattr(user, "avatar", None),
                    "role": user_role,
                },
                courses=courses_list,
                accion_logout=True,
            )

        # User is student
        else:
            return render_template(
                "student/dashboard.html",
                user={
                    "id": user.id,
                    "full_name": user.full_name,
                    "document": user.document,
                    "avatar": getattr(user, "avatar", None),
                    "role": user_role,
                },
                accion_logout=True,
            )
    except Exception:
        return redirect(url_for("auth.login"))
