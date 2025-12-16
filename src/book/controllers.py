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


# ========== HTML View Controllers ==========
def books_view_controller(_: Request):
    """Vista principal de libros"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("users.dashboard"))

        # Obtener todos los libros
        books, status_code = get_books_service()

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
            "teacher/books_view.html",
            user=user_dict,
            books=books,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("users.dashboard"))
    finally:
        db.close()


def read_book_controller(book_id: int):
    """Vista para leer/visualizar un libro ePub"""
    try:
        current_user_id = get_jwt_identity()
        db = SessionLocal()
        user = db.query(User).filter(User.id == current_user_id).first()

        if not user:
            return redirect(url_for("books.books_view"))

        # Obtener el libro
        book, status_code = get_book_service(book_id)

        if status_code != 200 or not book:
            return redirect(url_for("books.books_view"))

        # Preparar datos del usuario
        user_dict = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }

        return render_template(
            "teacher/book_reader.html",
            user=user_dict,
            book=book,
            accion_logout=True,
        )
    except Exception:
        return redirect(url_for("books.books_view"))
    finally:
        db.close()


def create_book_controller(request: Request):
    """Crear un nuevo libro"""
    try:
        current_user_id = get_jwt_identity()

        if request.method == "POST":
            # Obtener datos del formulario
            grade_level = request.form.get("grade_level")
            data = {
                "title": request.form.get("title"),
                "author": request.form.get("author"),
                "description": request.form.get("description", ""),
                "target_audience": request.form.get("target_audience", "student"),
                "grade_level": int(grade_level) if grade_level else None,
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
                pass
            else:
                pass

            return redirect(url_for("books.books_view"))

    except Exception:
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
                pass
            else:
                pass

            return redirect(url_for("books.books_view"))
        else:
            return redirect(url_for("books.books_view"))
    except Exception:
        return redirect(url_for("books.books_view"))


def delete_book_controller(book_id: int, request: Request):
    """Eliminar un libro"""
    try:
        _, status_code = delete_book_service(book_id)

        if status_code == 200:
            pass
        else:
            pass

        return redirect(url_for("books.books_view"))
    except Exception:
        return redirect(url_for("books.books_view"))


def download_book_controller(book_id: int, _: Request):
    """Descargar el archivo de un libro"""
    try:
        book_data, status_code = get_book_service(book_id)

        if status_code == 404:
            return redirect(url_for("books.books_view"))

        if not book_data or not book_data.get("file_path"):
            return redirect(url_for("books.books_view"))

        file_path = os.path.join("src", book_data["file_path"].lstrip("/"))

        if not os.path.exists(file_path):
            return redirect(url_for("books.books_view"))

        # Enviar el archivo con headers
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{book_data['title']}.epub",
            mimetype="application/epub+zip",
        )
    except Exception:
        return redirect(url_for("books.books_view"))


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
