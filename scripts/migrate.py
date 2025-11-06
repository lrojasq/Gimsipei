import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Ensure project root is on sys.path so 'src' imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.database import DATABASE_URL


MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "sql_migrations"
VERSION_TABLE = "sql_migration_version"


def ensure_version_table(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql(
            f"""
            CREATE TABLE IF NOT EXISTS {VERSION_TABLE} (
                version VARCHAR(255) NOT NULL PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """
        )


def get_applied_versions(engine):
    with engine.begin() as conn:
        try:
            res = conn.execute(text(f"SELECT version FROM {VERSION_TABLE}"))
            return {row[0] for row in res}
        except Exception:
            return set()


def apply_sql_file(engine, file_path: Path):
    sql = file_path.read_text(encoding="utf-8")
    # Split on semicolon newlines to allow multiple statements
    statements = [s.strip() for s in sql.split(";\n") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.exec_driver_sql(stmt)
            except Exception as e:
                # Ignore duplicate column/index errors to make it idempotent
                msg = str(e).lower()
                if "duplicate" in msg or "exists" in msg or "already" in msg:
                    continue
                raise


def main():
    engine = create_engine(DATABASE_URL)
    ensure_version_table(engine)
    applied = get_applied_versions(engine)

    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    pending = [f for f in files if f.stem not in applied]

    if not pending:
        print("No pending migrations.")
        return

    for f in pending:
        print(f"Applying migration: {f.name}")
        apply_sql_file(engine, f)
        with engine.begin() as conn:
            conn.exec_driver_sql(
                f"INSERT INTO {VERSION_TABLE} (version) VALUES (%s)",
                (f.stem,),
            )
    print("Migrations applied successfully.")


if __name__ == "__main__":
    main()
