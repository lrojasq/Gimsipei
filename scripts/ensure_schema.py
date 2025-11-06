import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.database import DATABASE_URL


def ensure_users_document(engine) -> None:
    with engine.begin() as conn:
        # Check column exists
        col = list(conn.execute(text("SHOW COLUMNS FROM users LIKE 'document'")))
        if not col:
            conn.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN document VARCHAR(20) NULL"
            )

        # Ensure unique constraint/index
        idx = list(
            conn.execute(
                text("SHOW INDEX FROM users WHERE Key_name='uq_users_document'")
            )
        )
        if not idx:
            # MySQL requires index/constraint creation this way
            conn.exec_driver_sql(
                "ALTER TABLE users ADD CONSTRAINT uq_users_document UNIQUE (document)"
            )


def main():
    engine = create_engine(DATABASE_URL)
    ensure_users_document(engine)
    print("Schema ensured: users.document present and unique.")


if __name__ == "__main__":
    main()
