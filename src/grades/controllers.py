from flask import (
    Request,
    flash,
    jsonify,
    redirect,
    render_template,
    url_for,
)
from flask_jwt_extended import get_jwt_identity

from src.database.database import SessionLocal
from src.models.course_student import CourseStudent
from src.models.user import User, UserRole

from .service import (
    get_courses_with_students_service,
    get_student_global_grades_service,
    get_student_grades_service,
    update_grade_service,
)


# ========== HTML View Controllers ==========
def grades_view_controller(_: Request):
    """Vista principal de calificaciones - muestra cursos con estudiantes para profesores,
    o redirige a sus propias calificaciones si es estudiante"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("users.dashboard"))

        if user.role == UserRole.STUDENT:
            # Obtener el curso del estudiante
            enrollment = (
                db.query(CourseStudent)
                .filter(CourseStudent.student_id == user.id)
                .first()
            )
            if enrollment:
                return redirect(
                    url_for(
                        "grades.student_grades_view",
                        course_id=enrollment.course_id,
                        student_id=user.id,
                        period=1,
                    )
                )
            else:
                flash("No estás inscrito en ningún curso", "danger")
                return redirect(url_for("users.dashboard"))

        # Mostrar todos los cursos con estudiantes
        courses, status_code = get_courses_with_students_service(current_user_id)

        if status_code != 200:
            flash("Error al cargar los cursos", "danger")
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
            "teacher/grades_view.html",
            user=user_dict,
            courses=courses,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
    finally:
        db.close()


def student_grades_view_controller(course_id: int, student_id: int, request: Request):
    """Vista de calificaciones de un estudiante por materia y periodo"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("users.dashboard"))

        # Solo puede ver sus propias calificaciones
        if user.role == UserRole.STUDENT and user.id != student_id:
            flash("No tienes permiso para ver estas calificaciones", "danger")
            return redirect(url_for("grades.grades_view"))

        # Obtener periodo del query string (por defecto periodo 1)
        period = request.args.get("period", type=int)

        # Obtener calificaciones del estudiante
        grades_data, status_code = get_student_grades_service(
            student_id, course_id, period
        )

        if status_code != 200:
            flash(grades_data.get("error", "Error al cargar calificaciones"), "danger")
            return redirect(url_for("grades.grades_view"))

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
            "teacher/student_grades_view.html",
            user=user_dict,
            grades_data=grades_data,
            current_period=period or 1,
            accion_logout=True,
        )
    except Exception:
        flash("Error al cargar las calificaciones del estudiante", "danger")
        return redirect(url_for("grades.grades_view"))
    finally:
        db.close()


def student_global_grades_view_controller(course_id: int, student_id: int, _: Request):
    """Vista de calificaciones globales de un estudiante"""
    db = SessionLocal()
    try:
        current_user_id = get_jwt_identity()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("users.dashboard"))

        # Si es estudiante, solo puede ver sus propias calificaciones
        if user.role == UserRole.STUDENT and user.id != student_id:
            flash("No tienes permiso para ver estas calificaciones", "danger")
            return redirect(url_for("grades.grades_view"))

        # Obtener calificaciones globales del estudiante
        grades_data, status_code = get_student_global_grades_service(
            student_id, course_id
        )

        if status_code != 200:
            flash(grades_data.get("error", "Error al cargar calificaciones"), "danger")
            return redirect(url_for("grades.grades_view"))

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
            "teacher/student_global_grades_view.html",
            user=user_dict,
            grades_data=grades_data,
            accion_logout=True,
        )
    except Exception:

        flash("Error al cargar las calificaciones globales", "danger")
        return redirect(url_for("grades.grades_view"))
    finally:
        db.close()


def update_grade_controller(
    course_id: int, student_id: int, subject_id: int, request: Request
):
    """Actualizar calificación de un estudiante"""
    try:
        if request.method == "POST":
            period = request.form.get("period", type=int)
            data = {
                "tasks_grade": request.form.get("tasks_grade"),
                "assignments_grade": request.form.get("assignments_grade"),
                "evaluations_grade": request.form.get("evaluations_grade"),
                "final_grade": request.form.get("final_grade"),
            }

            # Limpiar valores vacíos
            data = {k: v for k, v in data.items() if v is not None and v != ""}

            result, status_code = update_grade_service(
                student_id=student_id,
                course_id=course_id,
                subject_id=subject_id,
                period=period,
                data=data,
            )

            if status_code == 200:
                flash("Calificación actualizada exitosamente", "success")
            else:
                flash(result.get("error", "Error al actualizar calificación"), "danger")

            # Redirigir de vuelta a la vista del estudiante
            return redirect(
                url_for(
                    "grades.student_grades_view",
                    course_id=course_id,
                    student_id=student_id,
                    period=period,
                )
            )

        return redirect(url_for("grades.grades_view"))
    except Exception:
        flash("Error al actualizar la calificación", "danger")
        return redirect(url_for("grades.grades_view"))


# ========== API Controllers ==========
def get_grades_api_controller(course_id: int, student_id: int, request: Request):
    """API para obtener calificaciones de un estudiante"""
    try:
        period = request.args.get("period", type=int)
        grades_data, status_code = get_student_grades_service(
            student_id, course_id, period
        )
        return jsonify(grades_data), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_grade_api_controller(
    course_id: int, student_id: int, subject_id: int, request: Request
):
    """API para actualizar calificación"""
    try:
        data = request.get_json()
        period = data.get("period")

        if not period:
            return jsonify({"error": "Periodo es requerido"}), 400

        result, status_code = update_grade_service(
            student_id=student_id,
            course_id=course_id,
            subject_id=subject_id,
            period=period,
            data=data,
        )
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
