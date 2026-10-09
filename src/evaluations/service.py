import contextlib
import os
from datetime import datetime

from werkzeug.utils import secure_filename

from ..database.database import SessionLocal
from ..models.course import Course
from ..models.course_subject import CourseSubject
from ..models.evaluation import Evaluation
from ..models.evaluation_question import EvaluationQuestion, QuestionType
from ..models.evaluation_question_option import EvaluationQuestionOption
from ..models.subject import Subject


def evaluation_to_dict(evaluation):
    """Convertir objeto Evaluation a diccionario"""
    return {
        "id": evaluation.id,
        "title": evaluation.title,
        "description": evaluation.description or "",
        "cover_image": evaluation.cover_image,
        "period": evaluation.period,
        "course_id": evaluation.course_id,
        "subject_id": evaluation.subject_id,
        "created_by": evaluation.created_by,
        "created_at": evaluation.created_at.isoformat()
        if evaluation.created_at
        else None,
        "updated_at": evaluation.updated_at.isoformat()
        if evaluation.updated_at
        else None,
    }


def get_evaluations_service(
    course_id: int | None = None,
    subject_id: int | None = None,
    period: int | None = None,
) -> tuple[list[dict], int]:
    """Obtener todas las evaluaciones, opcionalmente filtradas"""
    db = SessionLocal()
    try:
        query = db.query(Evaluation)

        if course_id:
            query = query.filter(Evaluation.course_id == course_id)
        if subject_id:
            query = query.filter(Evaluation.subject_id == subject_id)
        if period:
            query = query.filter(Evaluation.period == period)

        evaluations = query.order_by(
            Evaluation.period, Evaluation.created_at.desc()
        ).all()
        return [evaluation_to_dict(e) for e in evaluations], 200
    except Exception:
        import traceback

        traceback.print_exc()
        return [], 500
    finally:
        db.close()


def get_evaluation_service(evaluation_id: int) -> tuple[dict | None, int]:
    """Obtener una evaluación específica"""
    db = SessionLocal()
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            return None, 404
        return evaluation_to_dict(evaluation), 200
    except Exception:
        import traceback

        traceback.print_exc()
        return None, 500
    finally:
        db.close()


def get_evaluations_by_period_service(
    course_id: int, subject_id: int
) -> tuple[dict[int, list[dict]], int]:
    """Obtener evaluaciones agrupadas por periodo"""
    db = SessionLocal()
    try:
        evaluations = (
            db.query(Evaluation)
            .filter(
                Evaluation.course_id == course_id,
                Evaluation.subject_id == subject_id,
            )
            .order_by(Evaluation.period, Evaluation.created_at.desc())
            .all()
        )

        evaluations_by_period = {1: [], 2: [], 3: [], 4: []}
        for evaluation in evaluations:
            period = evaluation.period
            if period in evaluations_by_period:
                evaluations_by_period[period].append(evaluation_to_dict(evaluation))

        return evaluations_by_period, 200
    except Exception:
        import traceback

        traceback.print_exc()
        return {1: [], 2: [], 3: [], 4: []}, 500
    finally:
        db.close()


def _save_cover_image(cover_image) -> str | None:
    """Guardar imagen de portada y devolver ruta relativa para servirla."""
    if not cover_image or not getattr(cover_image, "filename", None):
        return None

    filename = secure_filename(cover_image.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename}"

    upload_folder = os.path.join("src", "static", "uploads", "evaluations")
    os.makedirs(upload_folder, exist_ok=True)
    full_path = os.path.join(upload_folder, filename)
    cover_image.save(full_path)
    return f"/static/uploads/evaluations/{filename}"


def create_evaluation_service(
    data: dict,
    cover_image=None,
    created_by_user_id=None,
    questions: list[dict] | None = None,
) -> tuple[dict | None, int]:
    """
    Crear una nueva evaluación.

    Si se proporcionan preguntas, también se crean registros en
    `evaluation_questions` y `evaluation_question_options`.
    """
    db = SessionLocal()
    cover_path: str | None = None

    try:
        # Procesar imagen de portada si existe
        cover_path = _save_cover_image(cover_image)

        # Crear el registro de Evaluation
        evaluation = Evaluation(
            title=data.get("title"),
            description=data.get("description", ""),
            cover_image=cover_path,
            period=data.get("period"),
            course_id=data.get("course_id"),
            subject_id=data.get("subject_id"),
            created_by=created_by_user_id,
        )
        db.add(evaluation)
        db.flush()  # Obtener ID sin cerrar la transacción

        # Crear preguntas (si se envían)
        if questions:
            for idx, q in enumerate(questions, start=1):
                question = EvaluationQuestion(
                    evaluation_id=evaluation.id,
                    question_number=idx,
                    question_text=q.get("text", ""),
                    question_type=q.get("type", QuestionType.OPEN),
                    correct_answer=q.get("answer"),
                )
                db.add(question)
                db.flush()

                # Opciones para preguntas de selección múltiple
                if (
                    q.get("type") == QuestionType.MULTIPLE_CHOICE
                    or q.get("type") == "multi"
                ):
                    options = q.get("options") or {}
                    for order, (letter, text_) in enumerate(options.items(), start=1):
                        option = EvaluationQuestionOption(
                            question_id=question.id,
                            option_letter=letter,
                            option_text=text_,
                            display_order=order,
                        )
                        db.add(option)

        db.commit()
        db.refresh(evaluation)

        return {
            "message": "Evaluación creada exitosamente",
            "evaluation": evaluation_to_dict(evaluation),
        }, 201
    except Exception as e:
        db.rollback()
        # Limpiar archivo si ocurrió un error
        try:
            if cover_path:
                full_path = os.path.join("src", cover_path.lstrip("/"))
                if os.path.exists(full_path):
                    os.remove(full_path)
        except Exception:
            pass

        import traceback

        traceback.print_exc()
        return {"error": f"Error al crear la evaluación: {str(e)}"}, 500
    finally:
        db.close()


def update_evaluation_service(
    evaluation_id: int, data: dict, cover_image=None
) -> tuple[dict | None, int]:
    """Actualizar una evaluación"""
    db = SessionLocal()
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            return {"error": "Evaluación no encontrada"}, 404

        # Actualizar campos de texto
        if data.get("title") is not None:
            evaluation.title = data["title"]
        if data.get("description") is not None:
            evaluation.description = data["description"]
        if data.get("period") is not None:
            evaluation.period = data["period"]
        if data.get("course_id") is not None:
            evaluation.course_id = data["course_id"]
        if data.get("subject_id") is not None:
            evaluation.subject_id = data["subject_id"]

        # Actualizar imagen de portada si se proporciona una nueva
        if cover_image and cover_image.filename:
            # Eliminar imagen anterior si existe
            if evaluation.cover_image:
                old_path = os.path.join("src", evaluation.cover_image.lstrip("/"))
                if os.path.exists(old_path):
                    with contextlib.suppress(Exception):
                        os.remove(old_path)

            # Guardar nueva imagen
            filename = secure_filename(cover_image.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            upload_folder = os.path.join("src", "static", "uploads", "evaluations")
            os.makedirs(upload_folder, exist_ok=True)
            cover_path = os.path.join(upload_folder, filename)
            cover_image.save(cover_path)
            evaluation.cover_image = f"/static/uploads/evaluations/{filename}"

        db.commit()
        db.refresh(evaluation)
        return {
            "message": "Evaluación actualizada exitosamente",
            "evaluation": evaluation_to_dict(evaluation),
        }, 200
    except Exception as e:
        db.rollback()
        import traceback

        traceback.print_exc()
        return {"error": f"Error al actualizar la evaluación: {str(e)}"}, 500
    finally:
        db.close()


def delete_evaluation_service(evaluation_id: int) -> tuple[dict | None, int]:
    """Eliminar una evaluación"""
    db = SessionLocal()
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            return {"error": "Evaluación no encontrada"}, 404

        # Guardar ruta de imagen antes de eliminar el registro
        cover_image_path = evaluation.cover_image

        # Eliminar el registro de la base de datos
        db.delete(evaluation)
        db.commit()

        # Eliminar archivo físico
        if cover_image_path:
            full_path = os.path.join("src", cover_image_path.lstrip("/"))
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception as e:
                    print(f"Error al eliminar imagen: {str(e)}")

        return {
            "message": "Evaluación eliminada exitosamente",
        }, 200

    except Exception as e:
        db.rollback()
        import traceback

        traceback.print_exc()
        return {"error": f"Error al eliminar la evaluación: {str(e)}"}, 500
    finally:
        db.close()


def get_all_courses_with_subjects_for_evaluations():
    """
    Obtener todos los cursos con sus materias asignadas para evaluaciones.

    Single-query implementation: one JOIN fetches (course, course_subject,
    subject) tuples, then we group in Python. Was previously N+1: one
    query for the course list, plus one query per course to fetch its
    subjects. With 12 courses in the seed (and the same in prod) that
    cost 13 round-trips — each ~360ms of network latency against the
    production DB, so ~4.7s of pure network on this view alone.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(Course, CourseSubject, Subject)
            .outerjoin(
                CourseSubject, CourseSubject.course_id == Course.id
            )
            .outerjoin(Subject, Subject.id == CourseSubject.subject_id)
            .all()
        )

        # Group in a single pass, preserving the (course) order they
        # came out of the DB, and alphabetical subject order per course.
        course_order: list[int] = []
        courses_by_id: dict[int, dict] = {}
        for course, course_subject, subject in rows:
            if course.id not in courses_by_id:
                course_order.append(course.id)
                courses_by_id[course.id] = {
                    "id": course.id,
                    "name": course.name,
                    "academic_year": course.academic_year,
                    "subjects": [],
                }
            if subject is not None and course_subject is not None:
                courses_by_id[course.id]["subjects"].append(
                    {
                        "id": subject.id,
                        "name": subject.name,
                        "teacher_id": course_subject.teacher_id,
                    }
                )

        for course in courses_by_id.values():
            course["subjects"].sort(key=lambda s: s["name"])

        courses_data = [courses_by_id[cid] for cid in course_order]

        COURSE_NAME_ORDER = {
            "Sexto": 6,
            "Séptimo": 7,
            "Octavo": 8,
            "Noveno": 9,
            "Décimo": 10,
        }
        courses_data.sort(key=lambda c: COURSE_NAME_ORDER.get(c["name"], 999))

        return courses_data, 200
    except Exception:
        return [], 500
    finally:
        db.close()
