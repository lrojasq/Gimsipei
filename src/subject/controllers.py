from flask import Request, Response
from flask_jwt_extended import jwt_required
from typing import Tuple, Optional
from .validation import SubjectCreateSchema, SubjectUpdateSchema, SubjectResponseSchema
from .service import (
    get_subjects_service,
    get_subject_service,
    create_subject_service,
    update_subject_service,
    delete_subject_service,
)
from pydantic import ValidationError
from src.utils.api_response import ApiResponse
from src.models.user import UserRole
from src.utils.decorator_role_required import role_required


# API Controllers
@jwt_required()
@role_required([UserRole.ADMIN])
def get_subjects_api_controller(request: Request) -> Response | Tuple[list, int]:
    """API para obtener lista de materias"""
    try:
        # Obtener parámetros de filtro
        teacher_id = request.args.get("teacher_id", type=int)

        subjects, total = get_subjects_service(teacher_id=teacher_id)

        return ApiResponse.list_response(
            items=[subject.dict() for subject in subjects],
            total=total,
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener la lista de materias",
            details=str(e),
            status_code=500,
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def get_subject_api_controller(
    subject_id: int, request: Request
) -> Response | Tuple[Optional[SubjectResponseSchema], int]:
    """API para obtener una materia específica"""
    try:
        result, status_code = get_subject_service(subject_id, request)

        if status_code == 404:
            return ApiResponse.error(message="Materia no encontrada", status_code=404)

        return ApiResponse.success(data=result, message="Materia obtenida exitosamente")
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener la materia", details=str(e), status_code=500
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def create_subject_api_controller(
    request: Request,
) -> Response | Tuple[Optional[SubjectResponseSchema], int]:
    """API para crear una materia"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        validated = SubjectCreateSchema(**data)
        result, status_code = create_subject_service(validated, request)

        if status_code == 201 and result:
            return ApiResponse.success(
                data=result, message="Materia creada exitosamente", status_code=201
            )
        elif status_code == 400:
            return ApiResponse.error(
                message="Error al crear la materia",
                details="Ya existe una materia con ese nombre o el profesor no es válido",
                status_code=400,
            )
        else:
            return ApiResponse.error(
                message="Error al crear la materia",
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
@role_required([UserRole.ADMIN])
def update_subject_api_controller(
    subject_id: int, request: Request
) -> Response | Tuple[Optional[SubjectResponseSchema], int]:
    """API para actualizar una materia"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        validated = SubjectUpdateSchema(**data)
        result, status_code = update_subject_service(subject_id, validated, request)

        if status_code == 200:
            return ApiResponse.success(
                data=result, message="Materia actualizada exitosamente"
            )
        elif status_code == 404:
            return ApiResponse.error(message="Materia no encontrada", status_code=404)
        elif status_code == 400:
            return ApiResponse.error(
                message="Error al actualizar la materia",
                details="Ya existe una materia con ese nombre o el profesor no es válido",
                status_code=400,
            )
        else:
            return ApiResponse.error(
                message="Error al actualizar la materia",
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
@role_required([UserRole.ADMIN])
def delete_subject_api_controller(
    subject_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para eliminar una materia"""
    try:
        result, status_code = delete_subject_service(subject_id, request)

        if status_code == 200:
            return ApiResponse.success(message="Materia eliminada exitosamente")
        elif status_code == 404:
            return ApiResponse.error(message="Materia no encontrada", status_code=404)
        else:
            return ApiResponse.error(
                message="Error al eliminar la materia",
                details="Error interno del servidor",
                status_code=500,
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )
