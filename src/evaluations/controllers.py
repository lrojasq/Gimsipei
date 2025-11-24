from flask import (
    Request,
    Response,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Tuple, Optional
import json

from .service import (
    get_evaluations_service,
    get_evaluation_service,
    get_evaluations_by_period_service,
    create_evaluation_service,
    update_evaluation_service,
    delete_evaluation_service,
    get_all_courses_with_subjects_for_evaluations,
)
from .validation import EvaluationWithQuestionsCreateSchema, EvaluationCreateSchema
from src.utils.api_response import ApiResponse
from src.models.user import UserRole
from src.utils.decorator_role_required import role_required
from src.database.database import SessionLocal
from src.models.user import User
from src.models.subject import Subject
from src.models.course import Course


# ========== HTML View Controllers ==========
def evaluations_view_controller(_: Request):
    """Vista principal de evaluaciones para profesores"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("admin.dashboard"))

        # Obtener todos los cursos con sus materias
        courses, status_code = get_all_courses_with_subjects_for_evaluations()

        if status_code != 200:
            flash("Error al cargar los cursos", "error")
            return redirect(url_for("admin.dashboard"))

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
            "teacher/evaluations_view.html",
            user=user_dict,
            courses=courses,
            accion_logout=True,
        )
    except Exception:
        flash("Error al cargar la vista de evaluaciones", "error")
        return redirect(url_for("admin.dashboard"))
    finally:
        db.close()


def subject_evaluations_view_controller(course_id: int, subject_id: int, _: Request):
    """Vista detallada de evaluaciones por materia"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("evaluations.evaluations_view"))

        # Obtener curso y materia
        course = db.query(Course).filter(Course.id == course_id).first()
        subject = db.query(Subject).filter(Subject.id == subject_id).first()

        if not course or not subject:
            flash("Curso o materia no encontrado", "error")
            return redirect(url_for("evaluations.evaluations_view"))

        # Obtener evaluaciones agrupadas por periodo
        evaluations_by_period, status_code = get_evaluations_by_period_service(
            course_id, subject_id
        )

        if status_code != 200:
            flash("Error al cargar las evaluaciones", "error")
            return redirect(url_for("evaluations.evaluations_view"))

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
            "teacher/subject_evaluations_view.html",
            user=user_dict,
            course=course,
            subject=subject,
            evaluations_by_period=evaluations_by_period,
            accion_logout=True,
        )
    except Exception:
        flash("Error al cargar la vista de evaluaciones", "error")
        return redirect(url_for("evaluations.evaluations_view"))
    finally:
        db.close()


def create_evaluation_controller(request: Request):
    """Crear una nueva evaluación"""
    try:
        current_user_id = get_jwt_identity()

        if request.method == "POST":
            # Obtener datos básicos del formulario
            base_data = {
                "title": request.form.get("title"),
                "description": request.form.get("description", ""),
                "period": int(request.form.get("period")),
                "course_id": int(request.form.get("course_id")),
                "subject_id": int(request.form.get("subject_id")),
            }

            # Parsear y validar payload completo
            questions_json = request.form.get("questions_json") or "[]"
            try:
                questions_raw = json.loads(questions_json)
            except Exception:
                questions_raw = []

            if questions_raw:
                schema = EvaluationWithQuestionsCreateSchema(
                    **base_data, questions=questions_raw
                )
                data_dict = schema.dict()
                questions_payload = data_dict.pop("questions")
            else:
                # Sin preguntas, usar esquema básico
                schema = EvaluationCreateSchema(**base_data)
                data_dict = schema.dict()
                questions_payload = None

            # Obtener archivo de imagen
            cover_image = request.files.get("cover_image")

            # Crear evaluación
            result, status_code = create_evaluation_service(
                data=data_dict,
                cover_image=cover_image,
                created_by_user_id=current_user_id,
                questions=questions_payload,
            )

            if status_code == 201:
                flash("Evaluación creada exitosamente", "success")
                return redirect(
                    url_for(
                        "evaluations.subject_evaluations_view",
                        course_id=base_data["course_id"],
                        subject_id=base_data["subject_id"],
                    )
                )
            else:
                flash(result.get("error", "Error al crear la evaluación"), "error")
                return redirect(
                    url_for(
                        "evaluations.subject_evaluations_view",
                        course_id=base_data["course_id"],
                        subject_id=base_data["subject_id"],
                    )
                )

    except Exception as e:
        flash(f"Error al crear la evaluación: {str(e)}", "error")
        course_id = request.form.get("course_id")
        subject_id = request.form.get("subject_id")
        if course_id and subject_id:
            return redirect(
                url_for(
                    "evaluations.subject_evaluations_view",
                    course_id=course_id,
                    subject_id=subject_id,
                )
            )
        return redirect(url_for("evaluations.evaluations_view"))


def update_evaluation_controller(evaluation_id: int, request: Request):
    """Actualizar una evaluación"""
    try:
        if request.method == "POST":
            # Obtener datos del formulario
            data = {}
            if request.form.get("title"):
                data["title"] = request.form.get("title")
            if request.form.get("description"):
                data["description"] = request.form.get("description")
            if request.form.get("period"):
                data["period"] = int(request.form.get("period"))
            if request.form.get("course_id"):
                data["course_id"] = int(request.form.get("course_id"))
            if request.form.get("subject_id"):
                data["subject_id"] = int(request.form.get("subject_id"))

            # Obtener archivo de imagen
            cover_image = request.files.get("cover_image")

            result, status_code = update_evaluation_service(
                evaluation_id, data, cover_image
            )

            if status_code == 200:
                flash("Evaluación actualizada exitosamente", "success")
                course_id = data.get("course_id") or request.form.get("course_id")
                subject_id = data.get("subject_id") or request.form.get("subject_id")
                if course_id and subject_id:
                    return redirect(
                        url_for(
                            "evaluations.subject_evaluations_view",
                            course_id=course_id,
                            subject_id=subject_id,
                        )
                    )
            else:
                flash(result.get("error", "Error al actualizar la evaluación"), "error")

            course_id = request.form.get("course_id")
            subject_id = request.form.get("subject_id")
            if course_id and subject_id:
                return redirect(
                    url_for(
                        "evaluations.subject_evaluations_view",
                        course_id=course_id,
                        subject_id=subject_id,
                    )
                )
        else:
            # GET request - redirect to evaluations view
            return redirect(url_for("evaluations.evaluations_view"))
    except Exception as e:
        flash(f"Error al actualizar la evaluación: {str(e)}", "error")
        course_id = request.form.get("course_id")
        subject_id = request.form.get("subject_id")
        if course_id and subject_id:
            return redirect(
                url_for(
                    "evaluations.subject_evaluations_view",
                    course_id=course_id,
                    subject_id=subject_id,
                )
            )
        return redirect(url_for("evaluations.evaluations_view"))


def delete_evaluation_controller(evaluation_id: int, request: Request):
    """Eliminar una evaluación"""
    try:
        # Obtener course_id y subject_id antes de eliminar
        evaluation_data, _ = get_evaluation_service(evaluation_id)
        course_id = evaluation_data.get("course_id") if evaluation_data else None
        subject_id = evaluation_data.get("subject_id") if evaluation_data else None

        _, status_code = delete_evaluation_service(evaluation_id)

        if status_code == 200:
            flash("Evaluación eliminada exitosamente", "success")
        else:
            flash("Error al eliminar la evaluación", "error")

        if course_id and subject_id:
            return redirect(
                url_for(
                    "evaluations.subject_evaluations_view",
                    course_id=course_id,
                    subject_id=subject_id,
                )
            )
        return redirect(url_for("evaluations.evaluations_view"))
    except Exception:
        flash("Error al eliminar la evaluación", "error")
        return redirect(url_for("evaluations.evaluations_view"))


def get_evaluation_json_controller(evaluation_id: int, _: Request):
    """Obtener una evaluación en formato JSON (para modales de edición)"""
    try:
        result, status_code = get_evaluation_service(evaluation_id)

        if status_code == 404:
            return jsonify({"error": "Evaluación no encontrada"}), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener la evaluación: {str(e)}"}), 500


# ========== API Controllers ==========
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def get_evaluations_api_controller(request: Request) -> Response | Tuple[list, int]:
    """API para obtener todas las evaluaciones"""
    try:
        course_id = request.args.get("course_id", type=int)
        subject_id = request.args.get("subject_id", type=int)
        period = request.args.get("period", type=int)

        evaluations, status_code = get_evaluations_service(
            course_id=course_id, subject_id=subject_id, period=period
        )

        if status_code == 200:
            return ApiResponse.list_response(items=evaluations, total=len(evaluations))
        else:
            return ApiResponse.error(
                message="Error al obtener las evaluaciones", status_code=status_code
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


@jwt_required()
def get_evaluation_api_controller(
    evaluation_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para obtener una evaluación específica"""
    try:
        result, status_code = get_evaluation_service(evaluation_id)

        if status_code == 404:
            return ApiResponse.error(
                message="Evaluación no encontrada", status_code=404
            )

        return ApiResponse.success(
            data=result, message="Evaluación obtenida exitosamente"
        )
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener la evaluación", details=str(e), status_code=500
        )
