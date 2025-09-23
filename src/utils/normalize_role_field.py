from functools import wraps
from flask import request


def normalize_role_field(fn):
    """
    Normalize the role field if it exists in the request and is a string.
    """	
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Detect if the request is JSON or form-data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        # Normalize the role field if it exists
        if "role" in data and isinstance(data["role"], str):
            data["role"] = data["role"].upper()
        # Override the get_json method to return the normalized data
        request._cached_json = data
        # Update the form as well
        request.form = data
        return fn(*args, **kwargs)

    return wrapper
