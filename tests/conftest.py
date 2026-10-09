"""Test fixtures and environment setup.

CRITICAL: load_dotenv(override=True) MUST run before any import of
config, src.database, or main — otherwise the engine is built with the
production .env values.
"""
from pathlib import Path

# Load test env FIRST, before any app imports
from dotenv import load_dotenv

_TEST_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_TEST_DIR / ".env.test", override=True)

# Now safe to import the app
import pytest  # noqa: E402

from src.database.database import Base, SessionLocal, engine  # noqa: E402


def _drop_and_create_schema() -> None:
    """Drop and recreate all tables. Idempotent across runs."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def app():
    """Flask app, imported lazily so the test env is already loaded."""
    from main import app as flask_app

    _drop_and_create_schema()
    return flask_app


@pytest.fixture(scope="session", autouse=True)
def seed_db(app):
    """Seed the test DB once per session."""
    from tests import seed

    seed.seed_all()
    yield
    # No teardown — data lives on for the next run inspection if needed


@pytest.fixture(scope="session")
def client(app):
    """Flask test client (session-scoped)."""
    return app.test_client()


def _login(client, username: str, password: str) -> str:
    r = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert r.status_code == 200, (
        f"Login failed for {username!r}: {r.status_code} "
        f"{r.get_data(as_text=True)[:300]}"
    )
    return r.get_json()["access_token"]


@pytest.fixture(scope="session")
def tokens(client):
    """Dict of {role: jwt_access_token} for admin, teacher, student."""
    return {
        "admin": _login(client, "admin_01", "Test1234!"),
        "teacher": _login(client, "teacher_01", "Test1234!"),
        "student": _login(client, "student_01", "Test1234!"),
    }


@pytest.fixture(scope="session")
def db_session():
    """A SQLAlchemy session bound to the test engine. Use sparingly."""
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
