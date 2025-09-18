import os
from werkzeug.utils import secure_filename
import uuid

# Directories for file storage
BOOKS_DIR = "src/static/books"
COVERS_DIR = "src/static/covers"
os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    "book": ["epub"],
    "cover": ["jpg", "jpeg", "png", "webp"],
    "document": ["pdf", "doc", "docx"],
}


def save_file(file, file_type):
    """
    Save a file in the appropriate directory according to its type.

    Args:
        file: The Flask file object
        file_type: File type ('book', 'cover', etc.)

    Returns:
        The path of the saved file

    Raises:
        ValueError: If the file is invalid or the type is not supported
    """
    if file_type == "book":
        return save_file_locally(file, BOOKS_DIR, ALLOWED_EXTENSIONS["book"])
    elif file_type == "cover":
        return save_file_locally(file, COVERS_DIR, ALLOWED_EXTENSIONS["cover"])
    else:
        raise ValueError(f"Tipo de archivo no soportado: {file_type}")


def save_file_locally(file, folder, allowed_exts):
    """
    Save a file securely in the local file system

    Args:
        file: The Flask file object
        folder: Directory where to save the file
        allowed_exts: List of allowed extensions

    Returns:
        The path of the saved file

    Raises:
        ValueError: If the file is invalid or its extension is not allowed
    """
    if not file or not hasattr(file, "filename") or not file.filename:
        raise ValueError("Archivo no válido o vacío")

    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Nombre de archivo no válido")

    # Check the extension
    ext = os.path.splitext(filename)[1].lower().replace(".", "")
    if not ext:
        raise ValueError("Archivo sin extensión válida")

    if ext not in allowed_exts:
        raise ValueError(
            f"Formato no permitido: {ext}. Formatos permitidos: {', '.join(allowed_exts)}"
        )

    # Generate a unique filename to avoid overwrites
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(folder, unique_filename)

    # Save the file securely
    try:
        file.save(file_path)
        return file_path
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)  # Clean up partial file if failed
        raise ValueError(f"Error al guardar el archivo: {str(e)}")


def delete_file(file_path):
    """
    Delete a file from the file system

    Args:
        file_path: Path to the file to delete

    Returns:
        bool: True if the file was deleted, False if it did not exist or there was an error
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
    return False


def update_file(old_file_path, new_file, file_type):
    """
    Update a file: save the new one and delete the old one

    Args:
        old_file_path: Path to the old file
        new_file: New file object
        file_type: File type ('book', 'cover', etc.)

    Returns:
        The path of the saved new file
    """
    # Save the new file
    new_file_path = save_file(new_file, file_type)

    # Delete the old file
    delete_file(old_file_path)

    return new_file_path
