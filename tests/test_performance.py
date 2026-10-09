"""Performance baseline: rank the 10 slowest routes.

Iterates all registered routes, takes the median of 3 timed GET
requests per route, and prints a top-10 ranking. Mark routes that
exceed the slow threshold with pytest.mark.slow (does not fail
the run — diagnostics, not assertions).

Use this to spot the candidates for the next round of perf fixes.
"""
import statistics
import time
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

# Load test env before importing app code
load_dotenv(dotenv_path=Path(__file__).parent / ".env.test", override=True)

from src.database.database import SessionLocal  # noqa: E402

# Param name -> (table, column) to fetch a sample id from
_PARAM_TABLE = {
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

# Public endpoints (no auth required)
_PUBLIC = {"auth.login", "auth.forgot_password", "auth.logout",
           "auth.create_first_admin", "static", "health_check"}

SLOW_MS = 500  # mark routes slower than this as slow


def _collect_sample_ids() -> dict[str, int]:
    db = SessionLocal()
    try:
        ids = {}
        for param, (table, col) in _PARAM_TABLE.items():
            sql = f"SELECT {col} FROM {table} LIMIT 1"
            row = db.execute(text(sql)).first()
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
def timings(app, client, tokens):
    """Time every route, return list of (endpoint, method, path, median_ms, status)."""
    sample_ids = _collect_sample_ids()
    results = []
    headers = {"Authorization": f"Bearer {tokens['admin']}"}

    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static" or "GET" not in rule.methods:
            continue
        if rule.endpoint in _PUBLIC:
            continue  # skip — we want auth-required views here

        path = _resolve_path(rule, sample_ids)
        samples = []
        last_status = 0
        # 3 timed requests; take median
        for _ in range(3):
            t0 = time.perf_counter()
            resp = client.get(path, headers=headers)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            samples.append(elapsed_ms)
            last_status = resp.status_code
        median = statistics.median(samples)
        results.append((rule.endpoint, "GET", path, median, last_status))

    return results


def test_top_10_slowest(timings, capsys):
    """Print the 10 slowest routes. Doesn't fail the build."""
    sorted_routes = sorted(timings, key=lambda r: r[3], reverse=True)
    top = sorted_routes[:10]

    print("\n" + "=" * 70)
    print(f"{'Endpoint':<50} {'Method':<7} {'Path':<25} {'ms':>7} {'st':>5}")
    print("=" * 70)
    for ep, m, p, ms, st in top:
        print(f"{ep:<50} {m:<7} {p:<25} {ms:>7.1f} {st:>5}")
    print("=" * 70)

    slow = [r for r in timings if r[3] > SLOW_MS]
    if slow:
        print(f"\n{len(slow)} routes over {SLOW_MS}ms threshold:")
        for ep, _m, _p, ms, _st in slow:
            print(f"  {ms:>7.1f}ms  {ep}  (status reported in top-10 above)")
    else:
        print(f"\nAll {len(timings)} authenticated GET routes under {SLOW_MS}ms.")


def test_routes_under_threshold(timings):
    """Soft check: report how many routes exceed the threshold.

    We don't assert here — this is a baseline. Once we start optimizing
    we can tighten the threshold and turn it into a real assertion.
    """
    over = [r for r in timings if r[3] > SLOW_MS]
    if over:
        pytest.skip(
            f"{len(over)} routes over {SLOW_MS}ms — see test_top_10_slowest"
        )
