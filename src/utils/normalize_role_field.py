from functools import wraps

from flask import request


def get_request_data():
    """Read the request payload as a dict, preferring the normalized copy
    that ``normalize_role_field`` stashes on the request object. Falls
    back to parsing the JSON body or form data when the decorator did
    not run.
    """
    normalized = getattr(request, "_normalized_data", None)
    if normalized is not None:
        return normalized
    if request.is_json:
        return request.get_json() or {}
    return request.form.to_dict()


def normalize_role_field(fn):
    """Normalize the ``role`` field of the request payload.

    The normalized copy is stashed on the request as
    ``request._normalized_data`` so the controller can read it via
    :func:`get_request_data` without re-parsing. We do NOT replace
    ``request.form`` wholesale: doing so turns the Werkzeug MultiDict
    into a plain dict and any subsequent ``.to_dict()`` call inside the
    wrapped controller raises ``AttributeError``.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()
        if "role" in data and isinstance(data["role"], str):
            data["role"] = data["role"].upper()
        request._cached_json = data
        request._normalized_data = data
        return fn(*args, **kwargs)

    return wrapper
