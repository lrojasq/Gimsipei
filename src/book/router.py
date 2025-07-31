from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.utils.decorator_role_required import role_required
from src.models.user import UserRole
from .controllers import (
    create_book_controller,
    get_books_controller,
    get_book_controller,
    update_book_controller,
    delete_book_controller,
)
from .validation import BookCreateSchema, BookUpdateSchema
from pydantic import ValidationError
import traceback
from src.utils.validate_file import validate_file

book_bp = Blueprint("books", __name__, url_prefix="/books")


@book_bp.route("/", methods=["POST"])
@jwt_required()
@role_required(UserRole.ADMIN)
def create_book():
    """Endpoint to create books"""
    try:
        # Check if there are data in the form
        if not request.form:
            return jsonify({"error": "No se recibieron datos del formulario"}), 400

        # Check and validate the form data
        data = BookCreateSchema(**request.form)

        # Check if there are attached files
        if "file" not in request.files:
            return jsonify({"error": "No se envió el archivo del libro"}), 400

        # Validate book file
        file = request.files["file"]
        is_valid, error_message = validate_file(file, "book")
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Check the cover image (optional)
        cover_image = None
        if "cover_image" in request.files and request.files["cover_image"].filename:
            cover_image = request.files["cover_image"]
            is_valid, error_message = validate_file(cover_image, "cover")
            if not is_valid:
                return jsonify({"error": error_message}), 400

        return create_book_controller(data, file, cover_image)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        traceback.print_exc()  # Print the stack trace in the server logs
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@book_bp.route("/", methods=["GET"])
@jwt_required()
def list_books():
    """Get all books filtered by user role"""
    user_id = get_jwt_identity()
    return get_books_controller(user_id)


@book_bp.route("/<int:book_id>", methods=["GET"])
@jwt_required()
def get_book(book_id):
    """Get a specific book by ID"""
    user_id = get_jwt_identity()
    return get_book_controller(book_id, user_id)


@book_bp.route("/<int:book_id>", methods=["PUT"])
@jwt_required()
@role_required(UserRole.ADMIN)
def update_book(book_id):
    """Update a book by ID"""
    try:
        # Validate form data
        data = BookUpdateSchema(**request.form)

        # Validate files if provided
        file = None
        cover_image = None

        if "file" in request.files and request.files["file"].filename:
            file = request.files["file"]
            is_valid, error_message = validate_file(file, "book")
            if not is_valid:
                return jsonify({"error": error_message}), 400

        if "cover_image" in request.files and request.files["cover_image"].filename:
            cover_image = request.files["cover_image"]
            is_valid, error_message = validate_file(cover_image, "cover")
            if not is_valid:
                return jsonify({"error": error_message}), 400

        return update_book_controller(book_id, data, file, cover_image)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@book_bp.route("/<int:book_id>", methods=["DELETE"])
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_book(book_id):
    """Delete a book by ID"""
    return delete_book_controller(book_id)
