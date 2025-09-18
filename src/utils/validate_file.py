from src.utils.file_utils import ALLOWED_EXTENSIONS
import os

def validate_file(file, file_type):
    """
    Validate a file based on its type

    Args:
        file: The file object from request.files
        file_type: Type of file ('book' or 'cover')

    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or file.filename == "":
        return False, f"El archivo {file_type} es requerido y no puede estar vacío"

    # Get file extension
    ext = os.path.splitext(file.filename)[1].lower().replace(".", "")

    # Check if extension is allowed
    if ext not in ALLOWED_EXTENSIONS.get(file_type, []):
        allowed = ", ".join(ALLOWED_EXTENSIONS.get(file_type, []))
        return False, f"Formato no permitido: {ext}. Formatos permitidos: {allowed}"

    return True, None