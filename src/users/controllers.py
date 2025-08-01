from flask import Request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from typing import Tuple, Optional
from .validation import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from .service import (
    get_users_service,
    get_user_service,
    create_user_service,
    update_user_service,
    delete_user_service,
)
from pydantic import ValidationError
from src.utils.api_response import ApiResponse
from src.models.user import User, UserRole
from src.database.database import SessionLocal
from src.utils.normalize_role_field import normalize_role_field
from src.utils.decorator_role_required import role_required


@jwt_required()
@role_required([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])
def get_users_controller(request: Request) -> Response | Tuple[list, int]:
    try:
        role = request.args.get("role")
        search = request.args.get("search")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        users, total = get_users_service(role, search, page, per_page)
        return ApiResponse.list_response(
            items=[user.dict() for user in users],
            total=total,
            page=page,
            per_page=per_page,
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener la lista de usuarios",
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
        result, status_code = delete_user_service(user_id, request)

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
