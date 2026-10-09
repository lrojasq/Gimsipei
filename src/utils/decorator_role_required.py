from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from src.utils.api_response import ApiResponse


# Decorator to validate roles
def role_required(roles_param: object | list[object]):
    """
    Decorator to validate roles against the role claim embedded in the
    JWT at login time (additional_claims={"role": user.role.name}).

    We previously hit the DB to re-read the user and check their role.
    That made role_required cost an extra query per request — measurable
    in production where each query pays ~360ms of network latency.
    Controllers that actually need the user object (most of them) still
    fetch it via get_user_service after this decorator runs, so the
    "user still exists" check is not lost. The trade-off is that a
    role change takes effect at the next token refresh (max 2h) instead
    of immediately, which is acceptable for a school-management app.
    """
    # Convert single role to list, then to a set of role names
    role_names = {
        r.name if hasattr(r, "name") else str(r)
        for r in ([roles_param] if not isinstance(roles_param, list) else roles_param)
    }

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_role = get_jwt().get("role")
            if user_role not in role_names:
                return ApiResponse.error(message="No autorizado", status_code=403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
