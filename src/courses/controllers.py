from flask import Request, Response
from flask_jwt_extended import jwt_required
from typing import Tuple, Optional
from .validation import (
    CourseCreateSchema,
    CourseUpdateSchema,
    CourseResponseSchema,
    CourseSubjectSchema,
)
from .service import (
    get_courses_service,
    get_course_service,
    create_course_service,
    update_course_service,
    delete_course_service,
    get_course_subjects_service,
    add_subject_to_course_service,
    remove_subject_from_course_service,
)
from pydantic import ValidationError
from src.utils.api_response import ApiResponse
from src.models.user import UserRole
from src.utils.decorator_role_required import role_required


# API Controllers para AJAX
@jwt_required()
@role_required([UserRole.ADMIN])
def get_courses_api_controller(request: Request) -> Response | Tuple[list, int]:
    """API para obtener lista de cursos"""
    try:
        # Obtener parámetros de filtro
        academic_year = request.args.get("academic_year")
        period = request.args.get("period", type=int)
        grade_level = request.args.get("grade_level")
        is_active = request.args.get("is_active", type=bool)

        courses, total = get_courses_service(
            academic_year=academic_year,
            period=period,
            grade_level=grade_level,
            is_active=is_active,
        )

        return ApiResponse.list_response(
            items=[course.dict() for course in courses],
            total=total,
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener la lista de cursos",
            details=str(e),
            status_code=500,
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def get_course_api_controller(
    course_id: int, request: Request
) -> Response | Tuple[Optional[CourseResponseSchema], int]:
    """API para obtener un curso específico"""
    try:
        result, status_code = get_course_service(course_id, request)

        if status_code == 404:
            return ApiResponse.error(message="Curso no encontrado", status_code=404)

        return ApiResponse.success(data=result, message="Curso obtenido exitosamente")
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener el curso", details=str(e), status_code=500
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def create_course_api_controller(
    request: Request,
) -> Response | Tuple[Optional[CourseResponseSchema], int]:
    """API para crear un curso"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        validated = CourseCreateSchema(**data)
        result, status_code = create_course_service(validated, request)

        if status_code == 201 and result:
            return ApiResponse.success(
                data=result, message="Curso creado exitosamente", status_code=201
            )
        elif status_code == 400:
            return ApiResponse.error(
                message="Error al crear el curso",
                details="Ya existe un curso con ese nombre en el mismo año y período",
                status_code=400,
            )
        else:
            return ApiResponse.error(
                message="Error al crear el curso",
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
def update_course_api_controller(
    course_id: int, request: Request
) -> Response | Tuple[Optional[CourseResponseSchema], int]:
    """API para actualizar un curso"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        validated = CourseUpdateSchema(**data)
        result, status_code = update_course_service(course_id, validated, request)

        if status_code == 200:
            return ApiResponse.success(
                data=result, message="Curso actualizado exitosamente"
            )
        elif status_code == 404:
            return ApiResponse.error(message="Curso no encontrado", status_code=404)
        elif status_code == 400:
            return ApiResponse.error(
                message="Error al actualizar el curso",
                details="Ya existe un curso con ese nombre en el mismo año y período",
                status_code=400,
            )
        else:
            return ApiResponse.error(
                message="Error al actualizar el curso",
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
def delete_course_api_controller(
    course_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para eliminar un curso"""
    try:
        result, status_code = delete_course_service(course_id, request)

        if status_code == 200:
            return ApiResponse.success(message="Curso eliminado exitosamente")
        elif status_code == 404:
            return ApiResponse.error(message="Curso no encontrado", status_code=404)
        else:
            return ApiResponse.error(
                message="Error al eliminar el curso",
                details="Error interno del servidor",
                status_code=500,
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


# ---------- Subjects per course API (for accordion UI) ----------
@jwt_required()
@role_required([UserRole.ADMIN])
def get_course_subjects_api_controller(
    course_id: int, request: Request
) -> Response | Tuple[list, int]:
    """API: listar materias asignadas a un curso"""
    try:
        subjects, _ = get_course_subjects_service(course_id)
        return ApiResponse.list_response(items=subjects, total=len(subjects))
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener materias del curso",
            details=str(e),
            status_code=500,
        )


@jwt_required()
@role_required([UserRole.ADMIN])
def add_subject_to_course_api_controller(
    course_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API: agregar materia a un curso"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        validated = CourseSubjectSchema(**data)
        result, status_code = add_subject_to_course_service(
            course_id, validated, request
        )
        if status_code in (200, 201):
            return ApiResponse.success(
                message=result.get("message", "Materia agregada"),
                data=result,
                status_code=status_code,
            )
        elif status_code == 404:
            return ApiResponse.error(message="Curso no encontrado", status_code=404)
        else:
            return ApiResponse.error(
                message="No se pudo agregar la materia", status_code=400
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
def remove_subject_from_course_api_controller(
    course_id: int, subject_id: int, teacher_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API: eliminar materia de un curso"""
    try:
        result, status_code = remove_subject_from_course_service(
            course_id, subject_id, teacher_id, request
        )
        if status_code == 200:
            return ApiResponse.success(
                message=result.get("message", "Materia removida")
            )
        elif status_code == 404:
            return ApiResponse.error(
                message="Asignación no encontrada", status_code=404
            )
        else:
            return ApiResponse.error(
                message="No se pudo remover la materia", status_code=400
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )
