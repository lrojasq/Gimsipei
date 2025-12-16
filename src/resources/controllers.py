from flask import (
    Request,
    Response,
    render_template,
    redirect,
    url_for,
    send_file,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Tuple, Optional
from pydantic import ValidationError
import os

from .service import (
    get_resources_by_class_service,
    get_resources_by_teacher_service,
    get_resources_by_student_service,
    get_resources_by_student_subject_service,
    get_resource_service,
    create_resource_service,
    update_resource_service,
    delete_resource_service,
    get_resource_file_path_service,
)
from src.utils.api_response import ApiResponse
from src.models.user import UserRole
from src.utils.decorator_role_required import role_required
from src.database.database import SessionLocal
from src.models.user import User
from src.models.class_model import ClassModel


def resources_view_controller(_: Request):
    """Vista principal de recursos para profesores"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener recursos organizados por materia
        resources_data, status_code = get_resources_by_teacher_service(current_user_id)

        if status_code != 200:
            return redirect(url_for("users.dashboard"))

        # Convert the User object to a dictionary with role as string
        user_dict = {
            "id": user.id,
            "username": user.username,
            "document": user.document,
            "full_name": user.full_name,
            "avatar": getattr(user, "avatar", None),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }

        return render_template(
            "teacher/resources_view.html",
            user=user_dict,
            subjects=resources_data.get("subjects", []),
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
    finally:
        db.close()


def create_resource_controller(request: Request):
    """Crear un nuevo recurso"""
    try:
        current_user_id = get_jwt_identity()

        if request.method == "POST":
            # Obtener datos del formulario
            class_number = request.form.get("class_id")
            title = request.form.get("title")
            period = request.form.get("period")
            course_id = request.form.get("course_id")
            subject_id = request.form.get("subject_id")

            data = {
                "class_id": class_number,
                "course_id": course_id,
                "subject_id": subject_id,
                "title": title,
                "period": period,
            }

            # Obtener archivos
            cover_file = request.files.get("cover_image")
            resource_file = request.files.get("resource_file")

            # Crear recurso
            result, status_code = create_resource_service(
                data=data,
                cover_file=cover_file,
                resource_file=resource_file,
                created_by_user_id=current_user_id,
            )

            if status_code == 201:
                pass
            else:
                pass

            return redirect(url_for("resources.resources_view"))

    except Exception:
        return redirect(url_for("resources.resources_view"))


def delete_resource_controller(resource_id: int, request: Request):
    """Eliminar un recurso"""
    try:
        _, status_code = delete_resource_service(resource_id, request)

        if status_code == 200:
            pass
        else:
            pass

        return redirect(url_for("resources.resources_view"))
    except Exception:
        return redirect(url_for("resources.resources_view"))


def download_resource_controller(resource_id: int, _: Request):
    """Descargar el archivo de un recurso"""
    try:
        file_path, filename, status_code = get_resource_file_path_service(resource_id)

        if status_code == 404:
            return redirect(url_for("resources.resources_view"))

        if not file_path or not os.path.exists(file_path):
            return redirect(url_for("resources.resources_view"))

        # Enviar el archivo con headers
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/octet-stream",
        )
    except Exception:
        return redirect(url_for("resources.resources_view"))


# ========== API Controllers ==========
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def get_resources_by_class_api_controller(
    class_id: int, request: Request
) -> Response | Tuple[list, int]:
    """API para obtener recursos de una clase"""
    try:
        resources, status_code = get_resources_by_class_service(class_id)

        if status_code == 200:
            return ApiResponse.list_response(items=resources, total=len(resources))
        else:
            return ApiResponse.error(
                message="Error al obtener los recursos", status_code=status_code
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def get_available_classes_api_controller(request: Request):
    """
    API: listar clases existentes por course_id, subject_id y period.
    Se usa para poblar el select del modal de creación de recursos y evitar
    que se envíen números de clase inexistentes.
    """
    db = SessionLocal()
    try:
        course_id = request.args.get("course_id", type=int)
        subject_id = request.args.get("subject_id", type=int)
        period = request.args.get("period", type=int)

        if not course_id or not subject_id or not period:
            return ApiResponse.error(
                message="Faltan parámetros requeridos: course_id, subject_id, period",
                status_code=400,
            )

        classes = (
            db.query(ClassModel)
            .filter(
                ClassModel.course_id == course_id,
                ClassModel.subject_id == subject_id,
                ClassModel.period == period,
            )
            .order_by(ClassModel.class_number.asc())
            .all()
        )

        items = [
            {
                "id": c.id,
                "class_number": c.class_number,
                "title": c.title,
                "period": c.period,
            }
            for c in classes
        ]

        return ApiResponse.list_response(
            items=items,
            total=len(items),
            page=1,
            per_page=max(len(items), 1),
            message="Clases obtenidas exitosamente",
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener clases",
            details=str(e),
            status_code=500,
        )
    finally:
        db.close()


@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def get_resource_api_controller(
    resource_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para obtener un recurso específico"""
    try:
        result, status_code = get_resource_service(resource_id, request)

        if status_code == 404:
            return ApiResponse.error(message="Recurso no encontrado", status_code=404)

        return ApiResponse.success(data=result, message="Recurso obtenido exitosamente")
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener el recurso", details=str(e), status_code=500
        )


@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def create_resource_api_controller(
    request: Request,
) -> Response | Tuple[Optional[dict], int]:
    """API para crear un recurso"""
    try:
        current_user_id = get_jwt_identity()

        # Obtener datos del formulario
        data = {
            "class_id": int(request.form.get("class_id")),
            "title": request.form.get("title"),
            "period": int(request.form.get("period")),
        }

        # Obtener archivos
        cover_file = request.files.get("cover_image")
        resource_file = request.files.get("resource_file")

        # Crear recurso
        result, status_code = create_resource_service(
            data=data,
            cover_file=cover_file,
            resource_file=resource_file,
            created_by_user_id=current_user_id,
        )

        if status_code == 201:
            return ApiResponse.success(
                data=result, message="Recurso creado exitosamente", status_code=201
            )
        elif status_code == 404:
            return ApiResponse.error(message="Clase no encontrada", status_code=404)
        else:
            return ApiResponse.error(
                message=result.get("error", "Error al crear el recurso"),
                status_code=status_code,
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
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def update_resource_api_controller(
    resource_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para actualizar un recurso"""
    try:
        # Obtener datos del formulario
        data = {}
        if request.form.get("title"):
            data["title"] = request.form.get("title")
        if request.form.get("period"):
            data["period"] = int(request.form.get("period"))

        # Obtener archivos
        cover_file = request.files.get("cover_image")
        resource_file = request.files.get("resource_file")

        result, status_code = update_resource_service(
            resource_id, data, cover_file, resource_file, request
        )

        if status_code == 200:
            return ApiResponse.success(
                data=result, message="Recurso actualizado exitosamente"
            )
        elif status_code == 404:
            return ApiResponse.error(message="Recurso no encontrado", status_code=404)
        else:
            return ApiResponse.error(
                message="Error al actualizar el recurso", status_code=status_code
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
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def delete_resource_api_controller(
    resource_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para eliminar un recurso"""
    try:
        _, status_code = delete_resource_service(resource_id, request)

        if status_code == 200:
            return ApiResponse.success(message="Recurso eliminado exitosamente")
        elif status_code == 404:
            return ApiResponse.error(message="Recurso no encontrado", status_code=404)
        else:
            return ApiResponse.error(
                message="Error al eliminar el recurso", status_code=status_code
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


# ========== Student Controllers ==========
def student_resources_view_controller(_: Request):
    """Vista principal de recursos para estudiantes - muestra las materias"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener el curso y materias del estudiante
        resources_data, status_code = get_resources_by_student_service(current_user_id)

        if status_code != 200:
            return redirect(url_for("users.dashboard"))

        # Convert the User object to a dictionary
        user_dict = {
            "id": user.id,
            "username": user.username,
            "document": user.document,
            "full_name": user.full_name,
            "avatar": getattr(user, "avatar", None),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }

        return render_template(
            "student/resources_view.html",
            user=user_dict,
            course=resources_data.get("course"),
            subjects=resources_data.get("subjects", []),
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
    finally:
        db.close()


def resources_view_subject_controller(
    course_id: int, subject_id: int, request: Request
):
    """Vista de recursos de una materia específica para profesores y estudiantes"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener los recursos de la materia
        resources_data, status_code = get_resources_by_student_subject_service(
            current_user_id, course_id, subject_id
        )

        if status_code != 200:
            back_url = (
                url_for("resources.student_resources_view")
                if user.role.value == "student"
                else url_for("resources.resources_view")
            )
            return redirect(back_url)

        # Convert the User object to a dictionary
        user_dict = {
            "id": user.id,
            "username": user.username,
            "document": user.document,
            "full_name": user.full_name,
            "avatar": getattr(user, "avatar", None),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }

        # Obtener el nombre de la materia
        subject_obj = resources_data.get("subject")
        subject_name = subject_obj.name if subject_obj else ""

        return render_template(
            "teacher/resources_view.html",
            user=user_dict,
            course=resources_data.get("course"),
            subjects=[
                {
                    "subject_id": subject_id,
                    "course_id": course_id,
                    "subject_name": subject_name,
                    "periods": resources_data.get("periods", {}),
                }
            ],
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
    finally:
        db.close()
