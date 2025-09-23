from flask import jsonify
from .service import (
    create_book_service,
    get_books_service,
    get_book_service,
    update_book_service,
    delete_book_service,
)
from .validation import BookCreateSchema, BookUpdateSchema
from src.database.database import SessionLocal
from src.models.user import User, UserRole


def create_book_controller(data: BookCreateSchema, file, cover_image):
    book = create_book_service(data, file, cover_image)
    return jsonify(book), 201


def get_books_controller(user_id):
    # Obtenemos el usuario y su rol para filtrar los libros según corresponda
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Si es estudiante, solo ve libros para estudiantes
        if user.role == UserRole.STUDENT:
            books = get_books_service(target_audience="STUDENT")
        else:
            # Administradores y docentes ven todos los libros
            books = get_books_service()
        return jsonify(books)
    finally:
        db.close()


def get_book_controller(book_id: int, user_id):
    # Verificamos el usuario y su rol
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        book = get_book_service(book_id)
        if not book:
            return jsonify({"error": "Libro no encontrado"}), 404

        # Si es estudiante, solo puede ver libros para estudiantes
        if user.role == UserRole.STUDENT and book["target_audience"] != "STUDENT":
            return jsonify({"error": "No autorizado"}), 403

        return jsonify(book)
    finally:
        db.close()


def update_book_controller(
    book_id: int, data: BookUpdateSchema, file=None, cover_image=None
):
    book = update_book_service(book_id, data, file, cover_image)
    if not book:
        return jsonify({"error": "Libro no encontrado"}), 404
    return jsonify(book)


def delete_book_controller(book_id: int):
    result = delete_book_service(book_id)
    return jsonify(result)
