from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from src.utils.decorator_role_required import role_required
from src.models.user import UserRole

from .controllers import (
    books_view_controller,
    read_book_controller,
    create_book_controller,
    update_book_controller,
    delete_book_controller,
    download_book_controller,
    get_books_api_controller,
    get_book_api_controller,
)

book_bp = Blueprint("books", __name__, url_prefix="/books")


# ========== HTML View Routes ==========
@book_bp.route("", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def books_view():
    """Vista principal de libros"""
    return books_view_controller(request)


@book_bp.route("/<int:book_id>/read", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def read_book(book_id):
    """Vista para leer/visualizar un libro ePub"""
    return read_book_controller(book_id)


@book_bp.route("/create", methods=["GET", "POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.STUDENT])
def create_book():
    """Crear nuevo libro"""
    return create_book_controller(request)


@book_bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
@jwt_required()
@role_required([UserRole.TEACHER])
def update_book(book_id):
    """Actualizar libro"""
    return update_book_controller(book_id, request)


@book_bp.route("/<int:book_id>/delete", methods=["POST"])
@jwt_required()
@role_required([UserRole.TEACHER, UserRole.ADMIN])
def delete_book(book_id):
    """Eliminar libro"""
    return delete_book_controller(book_id, request)


@book_bp.route("/<int:book_id>/download", methods=["GET"])
@jwt_required()
@role_required([UserRole.TEACHER])
def download_book(book_id):
    """Descargar archivo del libro"""
    return download_book_controller(book_id, request)


# ========== API Routes ==========
@book_bp.route("/api", methods=["GET"])
def get_books_api():
    """API para obtener todos los libros"""
    return get_books_api_controller(request)


@book_bp.route("/api/<int:book_id>", methods=["GET"])
def get_book_api(book_id):
    """API para obtener un libro específico"""
    return get_book_api_controller(book_id, request)
