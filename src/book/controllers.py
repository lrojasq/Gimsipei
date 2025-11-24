from flask import (
    Request,
    Response,
    render_template,
    redirect,
    url_for,
    flash,
    send_file,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Tuple, Optional
import os

from .service import (
    get_books_service,
    get_book_service,
    create_book_service,
    update_book_service,
    delete_book_service,
)
from src.utils.api_response import ApiResponse
from src.models.user import UserRole
from src.utils.decorator_role_required import role_required
from src.database.database import SessionLocal
from src.models.user import User
from src.models.subject import Subject
from src.models.class_model import ClassModel
from src.models.course_subject import CourseSubject


# ========== HTML View Controllers ==========
def books_view_controller(_: Request):
    """Vista principal de libros para profesores"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("admin.dashboard"))

        # Obtener todos los libros
        books, status_code = get_books_service()

        if status_code != 200:
            flash("Error al cargar los libros", "error")
            return redirect(url_for("admin.dashboard"))

        # Obtener materias del profesor para el filtro
        course_subjects = (
            db.query(CourseSubject, Subject)
            .join(Subject, CourseSubject.subject_id == Subject.id)
            .filter(CourseSubject.teacher_id == current_user_id)
            .distinct(Subject.id)
            .all()
        )

        subjects_list = []
        for _, subject in course_subjects:
            subjects_list.append(
                {
                    "id": subject.id,
                    "name": subject.name,
                }
            )

        # Obtener clases del profesor para el filtro
        classes = (
            db.query(ClassModel)
            .join(
                CourseSubject,
                (CourseSubject.subject_id == ClassModel.subject_id)
                & (CourseSubject.course_id == ClassModel.course_id),
            )
            .filter(CourseSubject.teacher_id == current_user_id)
            .distinct(ClassModel.id)
            .all()
        )

        classes_list = []
        for class_item in classes:
            classes_list.append(
                {
                    "id": class_item.id,
                    "title": class_item.title,
                    "class_number": class_item.class_number,
                }
            )

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
            "teacher/books_view.html",
            user=user_dict,
            books=books,
            subjects=subjects_list,
            classes=classes_list,
            accion_logout=True,
        )
    except Exception:
        flash("Error al cargar la vista de libros", "error")
        return redirect(url_for("admin.dashboard"))
    finally:
        db.close()


def create_book_controller(request: Request):
    """Crear un nuevo libro"""
    try:
        current_user_id = get_jwt_identity()

        if request.method == "POST":
            # Obtener datos del formulario
            data = {
                "title": request.form.get("title"),
                "author": request.form.get("author"),
                "description": request.form.get("description", ""),
                "target_audience": request.form.get("target_audience", "STUDENT"),
            }

            # Obtener archivos
            book_file = request.files.get("book_file")
            cover_image = request.files.get("cover_image")

            # Crear libro
            result, status_code = create_book_service(
                data=data,
                file=book_file,
                cover_image=cover_image,
                created_by_user_id=current_user_id,
            )

            if status_code == 201:
                flash("Libro creado exitosamente", "success")
            else:
                flash(result.get("error", "Error al crear el libro"), "error")

            return redirect(url_for("books.books_view"))

    except Exception:
        flash("Error al crear el libro", "error")
        return redirect(url_for("books.books_view"))


def update_book_controller(book_id: int, request: Request):
    """Actualizar un libro"""
    try:
        if request.method == "POST":
            # Obtener datos del formulario
            data = {}
            if request.form.get("title"):
                data["title"] = request.form.get("title")
            if request.form.get("author"):
                data["author"] = request.form.get("author")
            if request.form.get("description"):
                data["description"] = request.form.get("description")
            if request.form.get("target_audience"):
                data["target_audience"] = request.form.get("target_audience")

            # Obtener archivos
            book_file = request.files.get("book_file")
            cover_image = request.files.get("cover_image")

            result, status_code = update_book_service(
                book_id, data, book_file, cover_image
            )

            if status_code == 200:
                flash("Libro actualizado exitosamente", "success")
            else:
                flash(result.get("error", "Error al actualizar el libro"), "error")

            return redirect(url_for("books.books_view"))
        else:
            # GET request - redirect to books view (editing is handled via modal)
            return redirect(url_for("books.books_view"))
    except Exception:
        flash("Error al actualizar el libro", "error")
        return redirect(url_for("books.books_view"))


def delete_book_controller(book_id: int, request: Request):
    """Eliminar un libro"""
    try:
        _, status_code = delete_book_service(book_id)

        if status_code == 200:
            flash("Libro eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el libro", "error")

        return redirect(url_for("books.books_view"))
    except Exception:
        flash("Error al eliminar el libro", "error")
        return redirect(url_for("books.books_view"))


def download_book_controller(book_id: int, _: Request):
    """Descargar el archivo de un libro"""
    try:
        book_data, status_code = get_book_service(book_id)

        if status_code == 404:
            flash("Libro no encontrado", "error")
            return redirect(url_for("books.books_view"))

        if not book_data or not book_data.get("file_path"):
            flash("El archivo del libro no está disponible", "error")
            return redirect(url_for("books.books_view"))

        file_path = os.path.join("src", book_data["file_path"].lstrip("/"))

        if not os.path.exists(file_path):
            flash("El archivo no existe", "error")
            return redirect(url_for("books.books_view"))

        # Enviar el archivo con headers
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{book_data['title']}.epub",
            mimetype="application/epub+zip",
        )
    except Exception:
        flash("Error al descargar el archivo", "error")
        return redirect(url_for("books.books_view"))


def read_book_controller(book_id: int, _: Request):
    """Vista para leer un libro (estudiantes)"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()

        # Obtener información del usuario
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("admin.dashboard"))

        # Obtener el libro
        book_data, status_code = get_book_service(book_id)

        if status_code == 404:
            flash("Libro no encontrado", "error")
            return redirect(url_for("admin.dashboard"))

        # Si es estudiante, solo puede ver libros para estudiantes
        if (
            user.role.value == "student"
            and book_data.get("target_audience") != "STUDENT"
        ):
            flash("No tienes permiso para ver este libro", "error")
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
            "student/read_book.html",
            user=user_dict,
            book=book_data,
            accion_logout=True,
        )
    except Exception:
        flash("Error al cargar el libro", "error")
        return redirect(url_for("admin.dashboard"))
    finally:
        db.close()


# ========== API Controllers ==========
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def get_books_api_controller(request: Request) -> Response | Tuple[list, int]:
    """API para obtener todos los libros"""
    try:
        books, status_code = get_books_service()

        if status_code == 200:
            return ApiResponse.list_response(items=books, total=len(books))
        else:
            return ApiResponse.error(
                message="Error al obtener los libros", status_code=status_code
            )
    except Exception as e:
        return ApiResponse.error(
            message="Error interno del servidor", details=str(e), status_code=500
        )


@jwt_required()
def get_book_api_controller(
    book_id: int, request: Request
) -> Response | Tuple[Optional[dict], int]:
    """API para obtener un libro específico"""
    try:
        result, status_code = get_book_service(book_id)

        if status_code == 404:
            return ApiResponse.error(message="Libro no encontrado", status_code=404)

        return ApiResponse.success(data=result, message="Libro obtenido exitosamente")
    except Exception as e:
        return ApiResponse.error(
            message="Error al obtener el libro", details=str(e), status_code=500
        )
