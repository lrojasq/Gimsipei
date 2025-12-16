from flask import (
    Request,
    Response,
    render_template,
    redirect,
    url_for,
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
from src.models.evaluation import Evaluation
from src.models.evaluation_question import EvaluationQuestion, QuestionType
from src.models.evaluation_submission import EvaluationSubmission
from src.models.course_student import CourseStudent
from src.models.evaluation_submission_answer import EvaluationSubmissionAnswer


# ========== HTML View Controllers ==========
def evaluations_view_controller(_: Request):
    """Vista principal de evaluaciones para profesores"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener todos los cursos con sus materias
        courses, status_code = get_all_courses_with_subjects_for_evaluations()

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
            "teacher/evaluations_view.html",
            user=user_dict,
            courses=courses,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
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
            return redirect(url_for("evaluations.evaluations_view"))

        # Obtener curso y materia
        course = db.query(Course).filter(Course.id == course_id).first()
        subject = db.query(Subject).filter(Subject.id == subject_id).first()

        if not course or not subject:
            return redirect(url_for("evaluations.evaluations_view"))

        # Obtener evaluaciones agrupadas por periodo
        evaluations_by_period, status_code = get_evaluations_by_period_service(
            course_id, subject_id
        )

        if status_code != 200:
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
                return redirect(
                    url_for(
                        "evaluations.subject_evaluations_view",
                        course_id=base_data["course_id"],
                        subject_id=base_data["subject_id"],
                    )
                )
            else:
                return redirect(
                    url_for(
                        "evaluations.subject_evaluations_view",
                        course_id=base_data["course_id"],
                        subject_id=base_data["subject_id"],
                    )
                )

    except Exception:
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
                pass

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
    except Exception:
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
            pass
        else:
            pass

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


def student_evaluations_view_controller(filter_type: str, _: Request):
    """Vista de evaluaciones para estudiantes"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener el curso del estudiante
        course_student = (
            db.query(CourseStudent)
            .filter(CourseStudent.student_id == current_user_id)
            .first()
        )

        course = None
        if course_student:
            course = (
                db.query(Course).filter(Course.id == course_student.course_id).first()
            )

        # Convert the User object to a dictionary
        user_dict = {
            "id": user.id,
            "username": user.username,
            "document": user.document,
            "full_name": user.full_name,
            "avatar": getattr(user, "avatar", None),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }

        evaluations = []

        if course:
            if filter_type == "completed":
                # Evaluaciones completadas (con submission)
                submissions = (
                    db.query(EvaluationSubmission)
                    .filter(
                        EvaluationSubmission.student_id == current_user_id,
                        EvaluationSubmission.is_completed.is_(True),
                    )
                    .all()
                )

                for submission in submissions:
                    eval_obj = submission.evaluation
                    if eval_obj and eval_obj.course_id == course.id:
                        evaluations.append(
                            {
                                "id": eval_obj.id,
                                "title": eval_obj.title,
                                "description": eval_obj.description,
                                "cover_image": eval_obj.cover_image,
                                "subject_name": eval_obj.subject.name
                                if eval_obj.subject
                                else "",
                                "score": submission.score,
                                "submitted_at": submission.submitted_at,
                            }
                        )
            else:
                # Evaluaciones pendientes (sin submission o no completadas)
                # Obtener todas las evaluaciones del curso del estudiante
                all_evaluations = (
                    db.query(Evaluation).filter(Evaluation.course_id == course.id).all()
                )

                # Obtener IDs de evaluaciones ya completadas
                completed_ids = (
                    db.query(EvaluationSubmission.evaluation_id)
                    .filter(
                        EvaluationSubmission.student_id == current_user_id,
                        EvaluationSubmission.is_completed.is_(True),
                    )
                    .all()
                )
                completed_ids = [id[0] for id in completed_ids]

                for eval_obj in all_evaluations:
                    if eval_obj.id not in completed_ids:
                        evaluations.append(
                            {
                                "id": eval_obj.id,
                                "title": eval_obj.title,
                                "description": eval_obj.description,
                                "cover_image": eval_obj.cover_image,
                                "subject_name": eval_obj.subject.name
                                if eval_obj.subject
                                else "",
                                "score": None,
                            }
                        )

        return render_template(
            "student/evaluations_view.html",
            user=user_dict,
            course=course,
            evaluations=evaluations,
            filter_type=filter_type,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
    finally:
        db.close()


def student_take_evaluation_controller(evaluation_id: int, _: Request):
    """Vista para que el estudiante resuelva una evaluación"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener la evaluación
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

        if not evaluation:
            return redirect(url_for("evaluations.student_evaluations_view"))

        # Verificar si ya completó esta evaluación
        existing_submission = (
            db.query(EvaluationSubmission)
            .filter(
                EvaluationSubmission.evaluation_id == evaluation_id,
                EvaluationSubmission.student_id == current_user_id,
                EvaluationSubmission.is_completed.is_(True),
            )
            .first()
        )

        if existing_submission:
            return redirect(url_for("evaluations.student_evaluations_view"))

        # Obtener las preguntas de la evaluación
        questions = (
            db.query(EvaluationQuestion)
            .filter(EvaluationQuestion.evaluation_id == evaluation_id)
            .order_by(EvaluationQuestion.question_number)
            .all()
        )

        # Obtener la materia
        subject = db.query(Subject).filter(Subject.id == evaluation.subject_id).first()

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
            "student/take_evaluation.html",
            user=user_dict,
            evaluation=evaluation,
            subject=subject,
            questions=questions,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("evaluations.student_evaluations_view"))
    finally:
        db.close()


def student_submit_evaluation_controller(evaluation_id: int, request: Request):
    """Procesar el envío de respuestas de una evaluación"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

        if not evaluation:
            return redirect(url_for("evaluations.student_evaluations_view"))

        # Verificar si ya completó esta evaluación
        existing_submission = (
            db.query(EvaluationSubmission)
            .filter(
                EvaluationSubmission.evaluation_id == evaluation_id,
                EvaluationSubmission.student_id == current_user_id,
                EvaluationSubmission.is_completed.is_(True),
            )
            .first()
        )

        if existing_submission:
            return redirect(url_for("evaluations.student_evaluations_view"))

        # Obtener las preguntas
        questions = (
            db.query(EvaluationQuestion)
            .filter(EvaluationQuestion.evaluation_id == evaluation_id)
            .all()
        )

        if not questions:
            return redirect(url_for("evaluations.student_evaluations_view"))

        # Crear o actualizar la submission
        submission = (
            db.query(EvaluationSubmission)
            .filter(
                EvaluationSubmission.evaluation_id == evaluation_id,
                EvaluationSubmission.student_id == current_user_id,
            )
            .first()
        )

        if not submission:
            submission = EvaluationSubmission(
                evaluation_id=evaluation_id,
                student_id=current_user_id,
                total_questions=len(questions),
                is_completed=False,
            )
            db.add(submission)
            db.flush()

        # Procesar las respuestas
        correct_count = 0
        total_questions = len(questions)

        for question in questions:
            answer_key = f"question_{question.id}"
            answer_value = request.form.get(answer_key, "").strip()

            # Crear la respuesta
            answer = EvaluationSubmissionAnswer(
                submission_id=submission.id,
                question_id=question.id,
                answer_text=answer_value,
            )

            # Verificar si es correcta según el tipo de pregunta
            if (
                question.question_type == QuestionType.MULTIPLE_CHOICE
                or question.question_type == "multi"
            ):
                # Opción múltiple: verificar contra la respuesta correcta
                if (
                    question.correct_answer
                    and answer_value.upper() == question.correct_answer.upper()
                ):
                    answer.is_correct = True
                    correct_count += 1
                else:
                    answer.is_correct = False
            else:
                # Pregunta abierta: si respondió algo, cuenta como correcta
                if answer_value:
                    answer.is_correct = True
                    correct_count += 1
                else:
                    answer.is_correct = False

            db.add(answer)

        # Calcular puntaje: 5.0 / total_preguntas * preguntas_correctas
        # Fórmula: (correctas / total) * 5.0
        score = (correct_count / total_questions) * 5.0 if total_questions > 0 else 0.0

        # Actualizar submission
        submission.correct_answers = correct_count
        submission.score = round(score, 1)  # Redondear a 1 decimal
        submission.is_completed = True

        db.commit()

        return redirect(
            url_for("evaluations.student_evaluations_view", filter="completed")
        )

    except Exception:
        db.rollback()
        return redirect(url_for("evaluations.student_evaluations_view"))
    finally:
        db.close()


def reset_evaluation_submission_controller(submission_id: int, request: Request):
    """Reiniciar evaluación de un estudiante (eliminar respuestas y permitir volver a presentar)"""
    db = SessionLocal()
    try:
        # Obtener la submission
        submission = (
            db.query(EvaluationSubmission)
            .filter(EvaluationSubmission.id == submission_id)
            .first()
        )

        if not submission:
            return redirect(request.referrer or url_for("users.dashboard"))

        # Guardar datos para redirección
        evaluation = submission.evaluation
        course_id = evaluation.course_id if evaluation else None
        student_id = submission.student_id

        # Eliminar las respuestas asociadas
        db.query(EvaluationSubmissionAnswer).filter(
            EvaluationSubmissionAnswer.submission_id == submission_id
        ).delete()

        # Eliminar la submission (permitirá al estudiante volver a presentar)
        db.delete(submission)
        db.commit()

        # Redirigir de vuelta a la página de evaluaciones del estudiante
        if course_id and student_id:
            return redirect(
                url_for(
                    "users.student_evaluations",
                    course_id=course_id,
                    student_id=student_id,
                )
            )
        return redirect(request.referrer or url_for("users.dashboard"))

    except Exception:
        db.rollback()
        return redirect(request.referrer or url_for("users.dashboard"))
    finally:
        db.close()


def delete_evaluation_submission_controller(submission_id: int, request: Request):
    """Eliminar envío de evaluación de un estudiante"""
    db = SessionLocal()
    try:
        # Obtener la submission
        submission = (
            db.query(EvaluationSubmission)
            .filter(EvaluationSubmission.id == submission_id)
            .first()
        )

        if not submission:
            return redirect(request.referrer or url_for("users.dashboard"))

        # Guardar datos para redirección
        evaluation = submission.evaluation
        course_id = evaluation.course_id if evaluation else None
        student_id = submission.student_id

        # Eliminar las respuestas asociadas (debería hacerse automáticamente por cascade)
        db.query(EvaluationSubmissionAnswer).filter(
            EvaluationSubmissionAnswer.submission_id == submission_id
        ).delete()

        # Eliminar la submission
        db.delete(submission)
        db.commit()

        # Redirigir de vuelta a la página de evaluaciones del estudiante
        if course_id and student_id:
            return redirect(
                url_for(
                    "users.student_evaluations",
                    course_id=course_id,
                    student_id=student_id,
                )
            )
        return redirect(request.referrer or url_for("users.dashboard"))

    except Exception:
        db.rollback()
        return redirect(request.referrer or url_for("users.dashboard"))
    finally:
        db.close()


def view_submission_answers_controller(submission_id: int, request: Request):
    """Ver las respuestas de un estudiante en una evaluación"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener la submission con sus relaciones
        submission = (
            db.query(EvaluationSubmission)
            .filter(EvaluationSubmission.id == submission_id)
            .first()
        )

        if not submission:
            return redirect(request.referrer or url_for("users.dashboard"))

        # Obtener la evaluación
        evaluation = (
            db.query(Evaluation)
            .filter(Evaluation.id == submission.evaluation_id)
            .first()
        )
        if not evaluation:
            return redirect(request.referrer or url_for("users.dashboard"))

        # Obtener el estudiante
        student = db.query(User).filter(User.id == submission.student_id).first()
        if not student:
            return redirect(request.referrer or url_for("users.dashboard"))

        # Obtener el curso y materia
        course = db.query(Course).filter(Course.id == evaluation.course_id).first()
        subject = db.query(Subject).filter(Subject.id == evaluation.subject_id).first()

        # Obtener las preguntas de la evaluación con sus opciones
        questions = (
            db.query(EvaluationQuestion)
            .filter(EvaluationQuestion.evaluation_id == evaluation.id)
            .order_by(EvaluationQuestion.id)
            .all()
        )

        # Obtener las respuestas del estudiante
        answers = (
            db.query(EvaluationSubmissionAnswer)
            .filter(EvaluationSubmissionAnswer.submission_id == submission_id)
            .all()
        )

        # Crear diccionario de respuestas para fácil acceso
        answers_dict = {answer.question_id: answer for answer in answers}

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
            "teacher/view_submission_answers.html",
            user=user_dict,
            submission=submission,
            evaluation=evaluation,
            student=student,
            course=course,
            subject=subject,
            questions=questions,
            answers_dict=answers_dict,
            total_questions=len(questions),
            accion_logout=True,
        )

    except Exception:
        return redirect(request.referrer or url_for("users.dashboard"))
    finally:
        db.close()


def update_submission_score_controller(submission_id: int, request: Request):
    """Actualizar la nota de un envío de evaluación"""
    db = SessionLocal()
    try:
        # Obtener datos del request
        data = request.get_json()
        if not data or "score" not in data:
            return jsonify({"success": False, "error": "Nota no proporcionada"}), 400

        new_score = float(data["score"])

        # Validar rango de nota
        if new_score < 0 or new_score > 5:
            return jsonify(
                {"success": False, "error": "La nota debe estar entre 0.0 y 5.0"}
            ), 400

        # Obtener la submission
        submission = (
            db.query(EvaluationSubmission)
            .filter(EvaluationSubmission.id == submission_id)
            .first()
        )

        if not submission:
            return jsonify(
                {"success": False, "error": "Envío de evaluación no encontrado"}
            ), 404

        # Actualizar la nota
        submission.score = new_score
        db.commit()

        return jsonify(
            {
                "success": True,
                "message": "Nota actualizada correctamente",
                "score": new_score,
            }
        ), 200

    except ValueError:
        return jsonify({"success": False, "error": "Nota inválida"}), 400
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
