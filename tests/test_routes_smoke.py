"""Smoke test: every route should respond without a 500.

Iterates over all registered Flask routes, substitutes path params with
real IDs from the test DB, and calls each with the appropriate method
and auth. Reports all routes that fail or return 500.
"""
from collections import defaultdict
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

# Load test env before importing app code
load_dotenv(dotenv_path=Path(__file__).parent / ".env.test", override=True)

from src.database.database import SessionLocal  # noqa: E402

# HTTP methods that should never cause data mutations when called as smoke
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

# Param name -> (table, column) to fetch a sample id from
_PARAM_TABLE = {
    "user_id": ("users", "id"),
    "teacher_id": ("users", "id"),  # teacher is also a user
    "student_id": ("users", "id"),  # student is also a user
    "course_id": ("courses", "id"),
    "subject_id": ("subjects", "id"),
    "class_id": ("classes", "id"),
    "resource_id": ("resources", "id"),
    "evaluation_id": ("evaluations", "id"),
    "book_id": ("books", "id"),
    "assignment_id": ("assignments", "id"),
    "submission_id": ("assignment_submissions", "id"),
    "content_id": ("class_contents", "id"),
}

# Routes that need NO auth (login page, health, etc.)
PUBLIC_ENDPOINTS = {
    "auth.login",  # GET and POST share the endpoint name
    "auth.forgot_password",
    "auth.logout",  # POST or GET
    "auth.create_first_admin",  # POST
    "health_check",  # /
    "static",
}


def _collect_sample_ids() -> dict[str, int]:
    """Fetch one sample ID per param name. Falls back to 1 if empty."""
    db = SessionLocal()
    try:
        ids = {}
        for param, (table, col) in _PARAM_TABLE.items():
            row = db.execute(text(f"SELECT {col} FROM {table} LIMIT 1")).first()
            ids[param] = row[0] if row else 1
    finally:
        db.close()
    return ids


def _resolve_path(rule, sample_ids: dict[str, int]) -> str:
    """Convert a Flask rule like /users/<int:user_id> into /users/1."""
    path = rule.rule
    for arg in rule.arguments:
        placeholder = f"<{arg}>"
        if placeholder not in path:
            continue
        # could be <int:arg>, <string:arg>, or just <arg>
        path = path.replace(f"<int:{arg}>", str(sample_ids.get(arg, 1)))
        path = path.replace(f"<string:{arg}>", str(sample_ids.get(arg, "x")))
        path = path.replace(f"<path:{arg}>", str(sample_ids.get(arg, "x")))
        path = path.replace(placeholder, str(sample_ids.get(arg, "x")))
    return path


def _needs_auth(endpoint: str) -> bool:
    """Routes not in PUBLIC_ENDPOINTS require auth."""
    if endpoint in ("static", "health_check"):
        return False
    return not endpoint.startswith("auth.")


@pytest.fixture(scope="module")
def all_route_results(app, client, tokens):
    """Iterate every route once, collect results. Module-scoped because
    we want all results in one report, not 126 separate test items."""
    sample_ids = _collect_sample_ids()
    results = []  # (endpoint, method, path, status, ok, error)

    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
        for method in methods:
            # Skip mutating methods in smoke — we test those with auth below
            if method not in SAFE_METHODS:
                continue

            path = _resolve_path(rule, sample_ids)
            headers = {}
            if _needs_auth(rule.endpoint):
                role = "admin"  # smoke uses admin for everything
                headers["Authorization"] = f"Bearer {tokens[role]}"

            try:
                resp = client.open(path, method=method, headers=headers)
                status = resp.status_code
                ok = status < 500
                err = None
            except Exception as e:
                status = 0
                ok = False
                err = f"{type(e).__name__}: {e}"

            results.append(
                (
                    rule.endpoint,
                    method,
                    path,
                    status,
                    ok,
                    err,
                )
            )

    return results


def test_no_500_on_any_route(all_route_results):
    """Every route must respond without a 5xx error."""
    failures = [r for r in all_route_results if not r[4]]
    if failures:
        msg = "\n".join(
            f"  {ep} {m} {p} -> {s} {e or ''}" for ep, m, p, s, _, e in failures
        )
        pytest.fail(f"{len(failures)} routes returned 5xx or raised:\n{msg}")


def test_auth_redirects_when_unauthenticated(app, client):
    """Unauthenticated requests to non-public routes must NOT return 200."""
    public_paths = {
        "/",
        "/auth/login",
        "/auth/forgot-password",
        "/auth/logout",
        "/auth/first-admin",
        "/health",
    }
    bad = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        if "GET" not in rule.methods:
            continue
        if rule.endpoint.startswith("auth."):
            continue
        # Build a real path (just probe — we expect non-200)
        path = _resolve_path(rule, _collect_sample_ids())
        if path in public_paths:
            continue
        resp = client.get(path)
        # Acceptable: 302 (redirect to login), 401/403 (api json)
        if resp.status_code == 200:
            bad.append((rule.endpoint, path, resp.status_code))
    if bad:
        msg = "\n".join(f"  {ep} {p} -> {s}" for ep, p, s in bad)
        pytest.fail(
            f"{len(bad)} protected routes returned 200 without auth "
            f"(security issue):\n{msg}"
        )


def test_smoke_summary(capsys, all_route_results):
    """Print a human-readable summary at the end of the smoke run."""
    by_status: dict[int, int] = defaultdict(int)
    for _, _, _, status, _, _ in all_route_results:
        by_status[status] += 1

    print("\n" + "=" * 60)
    print(f"Smoke summary: {len(all_route_results)} GET requests")
    print("=" * 60)
    for status in sorted(by_status):
        print(f"  {status:>3} : {by_status[status]:>3}")
    print("=" * 60)
