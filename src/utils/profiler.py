import logging
import os
import time

from flask import Flask, request

logger = logging.getLogger("profiler")

_profiling_enabled = os.getenv("PROFILING") == "1"


def init_profiler(app: Flask) -> None:
    """Register request profiling hooks on the given Flask app.

    No-op unless PROFILING=1 is set in the environment.
    """

    if not _profiling_enabled:
        return

    @app.before_request
    def _start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def _log_response(response):
        start = getattr(request, "_start_time", None)
        if start is not None:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s -> %s (%.1fms)",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )
        return response

    @app.teardown_request
    def _log_error(exc):
        if exc is not None and getattr(request, "_start_time", None) is not None:
            duration_ms = (time.perf_counter() - request._start_time) * 1000
            logger.error(
                "ERROR %s %s (%.1fms)",
                request.method,
                request.path,
                duration_ms,
            )
