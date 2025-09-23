from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from src.models.user import User
from src.database.database import SessionLocal
from src.utils.api_response import ApiResponse
from typing import Union, List


# Decorator to validate roles
def role_required(roles_param: Union[object, List[object]]):
    """
    Decorator to validate roles. It uses the verify_jwt_in_request function to validate the JWT token.
    It uses the get_jwt_identity function to get the user id.
    It uses the SessionLocal class to get the user from the database.
    It uses the ApiResponse class to return the error response.

    Args:
        roles_param: A single role or a list of roles that are allowed to access the endpoint
    """
    # Convert single role to list for consistent handling
    roles = [roles_param] if not isinstance(roles_param, list) else roles_param

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            """
            Wrapper to validate roles.
            """
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            db = SessionLocal()
            user = db.query(User).get(user_id)
            db.close()
            if not user or user.role not in roles:
                return ApiResponse.error(message="No autorizado", status_code=403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
