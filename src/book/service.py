from .validation import BookCreateSchema, BookUpdateSchema
from ..models.book import Book
from ..database.database import SessionLocal
from ..utils.file_utils import save_file, delete_file, update_file


def book_to_dict(book):
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "file_path": book.file_path,
        "cover_image": book.cover_image,
        "target_audience": book.target_audience,
    }


def create_book_service(data: BookCreateSchema, file, cover_image):
    db = SessionLocal()
    file_path = None
    cover_path = None

    try:
        # Save the main file
        file_path = save_file(file, "book")

        # Save the cover image if it exists
        if cover_image:
            cover_path = save_file(cover_image, "cover")

        # Create the record in the database
        book = Book(
            title=data.title,
            author=data.author,
            description=data.description,
            file_path=file_path,
            cover_image=cover_path,
            target_audience=data.target_audience,
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book_to_dict(book)
    except Exception as e:
        db.rollback()
        # Clean up files if an error occurred
        if file_path:
            delete_file(file_path)
        if cover_path:
            delete_file(cover_path)
        raise e
    finally:
        db.close()


def get_books_service(target_audience=None):
    db = SessionLocal()
    try:
        query = db.query(Book)
        if target_audience:
            query = query.filter(Book.target_audience == target_audience)
        books = query.all()
        return [book_to_dict(b) for b in books]
    finally:
        db.close()


def get_book_service(book_id: int):
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None
        return book_to_dict(book)
    finally:
        db.close()


def update_book_service(
    book_id: int, data: BookUpdateSchema, file=None, cover_image=None
):
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None

        # Update text fields
        if data.title is not None:
            book.title = data.title
        if data.author is not None:
            book.author = data.author
        if data.description is not None:
            book.description = data.description
        if data.target_audience is not None:
            book.target_audience = data.target_audience

        # Update the book file if a new one is provided
        if file:
            book.file_path = update_file(book.file_path, file, "book")

        # Update the cover image if a new one is provided
        if cover_image:
            book.cover_image = update_file(book.cover_image, cover_image, "cover")

        db.commit()
        db.refresh(book)
        return book_to_dict(book)
    finally:
        db.close()


def delete_book_service(book_id: int):
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return {"error": "Libro no encontrado"}

        # Save file paths before deleting the record
        file_path = book.file_path
        cover_image_path = book.cover_image

        # Delete the record from the database
        db.delete(book)
        db.commit()

        # Delete physical files
        files_deleted = []

        # Delete the book file
        if delete_file(file_path):
            files_deleted.append("libro")

        # Delete the cover image
        if delete_file(cover_image_path):
            files_deleted.append("portada")

        # Build the response message
        if files_deleted:
            return {
                "detail": f"Libro eliminado. Archivos eliminados: {', '.join(files_deleted)}"
            }
        else:
            return {
                "detail": "Libro eliminado de la base de datos. No se encontraron archivos físicos."
            }

    finally:
        db.close()
