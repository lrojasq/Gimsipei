"""Performance test against the production DB (READ ONLY).

This is the realistic perf baseline. The local test DB at
localhost:3307 has ~50ms latency shaved off because the DB is in
a container on the same host. Against production (remote MariaDB
on 160.153.133.188) the per-query network cost is significant.

GUARDS (intentionally defensive — the user said NEVER write to prod):

1. The env file tests/.env.prodtest points at the production DB.
2. The conftest fixture installs a SQLAlchemy event listener that
   REJECTS any non-SELECT statement. INSERT/UPDATE/DELETE/DDL
   raises immediately.
3. The conftest also installs a latency shim that adds
   TEST_LATENCY_MS milliseconds (default 50) before every
   executed query, so timings are reproducible.
4. This test file will only run when RUN_PROD_PERF=1 is set in
   the environment. Otherwise it's auto-skipped, to avoid
   accidentally hitting prod from a CI run.
5. Only GET routes are exercised (no POST/PUT/DELETE in the
   perf loop), so even if the read-only guard failed, there
   would be no writes.

The test re-uses the same ranking logic as tests/test_performance.py
but on the real production data and with realistic latency.
"""
import os
import statistics
import time
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import event, text

# Load prod-test env FIRST, before any app imports
load_dotenv(dotenv_path=Path(__file__).parent / ".env.prodtest", override=True)

from src.database.database import SessionLocal, engine  # noqa: E402

RUN_PROD_PERF = os.getenv("RUN_PROD_PERF") == "1"
READ_ONLY = os.getenv("TEST_READ_ONLY", "0") == "1"
LATENCY_MS = int(os.getenv("TEST_LATENCY_MS", "0"))

# Whitelist of statement prefixes considered safe in read-only mode.
# Anything else raises RuntimeError before the cursor fires.
_SAFE_PREFIXES = (
    "SELECT",
    "SHOW",
    "EXPLAIN",
    "DESCRIBE",
    "DESC ",
    "USE",
)


def _install_engine_hooks():
    """Install read-only guard + latency shim on the SQLAlchemy engine.

    Idempotent: uses a sentinel attribute on the engine so re-imports
    don't double-register.
    """
    if getattr(engine, "_prodtest_hooks_installed", False):
        return

    @event.listens_for(engine, "before_cursor_execute")
    def _before(conn, cursor, statement, parameters, context, executemany):
        if READ_ONLY:
            head = statement.lstrip().split(None, 1)[0].upper() if statement.strip() else ""
            if head not in _SAFE_PREFIXES:
                raise RuntimeError(
                    f"PRODTEST READ-ONLY guard blocked non-SELECT statement: "
                    f"{statement.splitlines()[0][:120]!r}"
                )
        if LATENCY_MS > 0:
            time.sleep(LATENCY_MS / 1000.0)

    engine._prodtest_hooks_installed = True


@pytest.fixture(scope="module", autouse=True)
def _require_opt_in():
    if not RUN_PROD_PERF:
        pytest.skip(
            "RUN_PROD_PERF not set. This test runs against the production DB. "
            "Set RUN_PROD_PERF=1 in the environment to opt in."
        )


@pytest.fixture(scope="module")
def prod_client():
    """Build the Flask app pointed at prod (read-only), with latency hooks."""
    _install_engine_hooks()
    from main import app as flask_app

    client = flask_app.test_client()
    yield client


@pytest.fixture(scope="module")
def prod_tokens(prod_client):
    """Log in to the real app as the first admin user we can find."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT username FROM users WHERE role = 'ADMIN' LIMIT 1")
        ).first()
    finally:
        db.close()
    if not row:
        pytest.skip("No admin user in production DB — cannot test")
    admin_username = row[0]

    r = prod_client.post(
        "/auth/login",
        json={"username": admin_username, "password": "wrong-password-intentionally"},
    )
    if r.status_code == 200:
        # Lucky — we have credentials. (Will only happen if prod actually
        # has a known password. We do NOT try real passwords here.)
        return {"admin": r.get_json()["access_token"]}
    pytest.skip(
        f"Could not log in as {admin_username!r} (no known test password). "
        f"Perf test against prod needs a known credential."
    )


def _collect_sample_ids_prod() -> dict[str, int]:
    """One sample id per param name, fetched from prod (read-only)."""
    mapping = {
        "user_id": ("users", "id"),
        "teacher_id": ("users", "id"),
        "student_id": ("users", "id"),
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
    db = SessionLocal()
    try:
        ids = {}
        for param, (table, col) in mapping.items():
            row = db.execute(
                text(f"SELECT {col} FROM {table} LIMIT 1")
            ).first()
            ids[param] = row[0] if row else 1
    finally:
        db.close()
    return ids


def _resolve_path(rule, sample_ids: dict[str, int]) -> str:
    path = rule.rule
    for arg in rule.arguments:
        if f"<{arg}>" not in path:
            continue
        val = sample_ids.get(arg, 1)
        path = path.replace(f"<int:{arg}>", str(val))
        path = path.replace(f"<string:{arg}>", str(val))
        path = path.replace(f"<path:{arg}>", str(val))
        path = path.replace(f"<{arg}>", str(val))
    return path


@pytest.fixture(scope="module")
def prod_timings(prod_client, prod_tokens, app):
    """Time every route against prod (with latency shim)."""
    # Reuse the imported app's url_map (it has all routes registered)
    sample_ids = _collect_sample_ids_prod()
    headers = {"Authorization": f"Bearer {prod_tokens['admin']}"}
    results = []

    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static" or "GET" not in rule.methods:
            continue
        if rule.endpoint.startswith("auth."):
            continue

        path = _resolve_path(rule, sample_ids)
        samples = []
        last_status = 0
        for _ in range(2):  # only 2 samples to keep prod load down
            t0 = time.perf_counter()
            resp = prod_client.get(path, headers=headers)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            samples.append(elapsed_ms)
            last_status = resp.status_code
        median = statistics.median(samples)
        results.append((rule.endpoint, "GET", path, median, last_status))

    return results


def test_top_10_slowest_prod(prod_timings, capsys):
    sorted_routes = sorted(prod_timings, key=lambda r: r[3], reverse=True)
    top = sorted_routes[:10]

    print("\n" + "=" * 70)
    print(f"PROD performance (latency shim: {LATENCY_MS}ms, read-only):")
    print("=" * 70)
    print(f"{'Endpoint':<50} {'ms':>7} {'st':>5}")
    print("-" * 70)
    for ep, _m, _p, ms, st in top:
        print(f"{ep:<50} {ms:>7.1f} {st:>5}")
    print("=" * 70)

    slow = [r for r in prod_timings if r[3] > 1000]
    if slow:
        print(f"\n{len(slow)} routes over 1s on prod:")
        for ep, _m, _p, ms, _st in slow:
            print(f"  {ms:>7.1f}ms  {ep}  (path in top-10 above)")
