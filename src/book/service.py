import os
from datetime import datetime
from typing import Optional, Tuple

from werkzeug.utils import secure_filename

from ..database.database import SessionLocal
from ..models.book import Book


def book_to_dict(book):
    """Convertir objeto Book a diccionario"""
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description or "",
        "file_path": book.file_path,
        "cover_image": book.cover_image,
        "target_audience": book.target_audience,
        "grade_level": book.grade_level,
    }


def create_book_service(
    data: dict, file=None, cover_image=None, created_by_user_id=None
) -> Tuple[Optional[dict], int]:
    """Crear un nuevo libro"""
    db = SessionLocal()
    file_path = None
    cover_path = None

    try:
        # Procesar archivo del libro si existe
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            upload_folder = os.path.join("src", "static", "uploads", "books")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            file_path = f"/static/uploads/books/{filename}"

        # Procesar imagen de portada si existe
        if cover_image and cover_image.filename:
            filename = secure_filename(cover_image.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            upload_folder = os.path.join("src", "static", "uploads", "books", "covers")
            os.makedirs(upload_folder, exist_ok=True)
            cover_path = os.path.join(upload_folder, filename)
            cover_image.save(cover_path)
            cover_path = f"/static/uploads/books/covers/{filename}"

        # Crear el registro en la base de datos
        book = Book(
            title=data.get("title"),
            author=data.get("author"),
            description=data.get("description", ""),
            file_path=file_path,
            cover_image=cover_path,
            target_audience=data.get("target_audience", "student"),
            grade_level=data.get("grade_level"),
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        return {
            "message": "Libro creado exitosamente",
            "book": book_to_dict(book),
        }, 201
    except Exception as e:
        db.rollback()
        # Limpiar archivos si ocurrió un error
        if file_path and os.path.exists(file_path.lstrip("/")):
            try:
                os.remove(os.path.join("src", file_path.lstrip("/")))
            except Exception:
                pass
        if cover_path and os.path.exists(cover_path.lstrip("/")):
            try:
                os.remove(os.path.join("src", cover_path.lstrip("/")))
            except Exception:
                pass
        import traceback

        traceback.print_exc()
        return {"error": f"Error al crear el libro: {str(e)}"}, 500
    finally:
        db.close()


def get_books_service(target_audience=None) -> Tuple[Optional[list], int]:
    """Obtener todos los libros, opcionalmente filtrados por audiencia"""
    db = SessionLocal()
    try:
        query = db.query(Book)
        if target_audience:
            query = query.filter(Book.target_audience == target_audience)
        books = query.all()
        return [book_to_dict(b) for b in books], 200
    finally:
        db.close()


def get_book_service(book_id: int) -> Tuple[Optional[dict], int]:
    """Obtener un libro específico"""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None, 404
        return book_to_dict(book), 200
    finally:
        db.close()


def update_book_service(
    book_id: int, data: dict, file=None, cover_image=None
) -> Tuple[Optional[dict], int]:
    """Actualizar un libro"""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return {"error": "Libro no encontrado"}, 404

        # Actualizar campos de texto
        if data.get("title") is not None:
            book.title = data["title"]
        if data.get("author") is not None:
            book.author = data["author"]
        if data.get("description") is not None:
            book.description = data["description"]
        if data.get("target_audience") is not None:
            book.target_audience = data["target_audience"]

        # Actualizar archivo del libro si se proporciona uno nuevo
        if file and file.filename:
            # Eliminar archivo anterior si existe
            if book.file_path:
                old_path = os.path.join("src", book.file_path.lstrip("/"))
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception:
                        pass

            # Guardar nuevo archivo
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            upload_folder = os.path.join("src", "static", "uploads", "books")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            book.file_path = f"/static/uploads/books/{filename}"

        # Actualizar imagen de portada si se proporciona una nueva
        if cover_image and cover_image.filename:
            # Eliminar imagen anterior si existe
            if book.cover_image:
                old_path = os.path.join("src", book.cover_image.lstrip("/"))
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception:
                        pass

            # Guardar nueva imagen
            filename = secure_filename(cover_image.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            upload_folder = os.path.join("src", "static", "uploads", "books", "covers")
            os.makedirs(upload_folder, exist_ok=True)
            cover_path = os.path.join(upload_folder, filename)
            cover_image.save(cover_path)
            book.cover_image = f"/static/uploads/books/covers/{filename}"

        db.commit()
        db.refresh(book)
        return {
            "message": "Libro actualizado exitosamente",
            "book": book_to_dict(book),
        }, 200
    except Exception as e:
        db.rollback()
        import traceback

        traceback.print_exc()
        return {"error": f"Error al actualizar el libro: {str(e)}"}, 500
    finally:
        db.close()


def delete_book_service(book_id: int) -> Tuple[Optional[dict], int]:
    """Eliminar un libro"""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return {"error": "Libro no encontrado"}, 404

        # Guardar rutas de archivos antes de eliminar el registro
        file_path = book.file_path
        cover_image_path = book.cover_image

        # Eliminar el registro de la base de datos
        db.delete(book)
        db.commit()

        # Eliminar archivos físicos
        files_deleted = []

        # Eliminar archivo del libro
        if file_path:
            full_path = os.path.join("src", file_path.lstrip("/"))
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    files_deleted.append("libro")
                except Exception as e:
                    print(f"Error al eliminar archivo: {str(e)}")

        # Eliminar imagen de portada
        if cover_image_path:
            full_path = os.path.join("src", cover_image_path.lstrip("/"))
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    files_deleted.append("portada")
                except Exception as e:
                    print(f"Error al eliminar imagen: {str(e)}")

        return {
            "message": "Libro eliminado exitosamente",
            "files_deleted": files_deleted,
        }, 200

    except Exception as e:
        db.rollback()
        import traceback

        traceback.print_exc()
        return {"error": f"Error al eliminar el libro: {str(e)}"}, 500
    finally:
        db.close()
