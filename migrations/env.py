import logging
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from src.database.database import Base, DATABASE_URL

# Import all models to ensure they are registered with Base.metadata
from src.models.user import User
from src.models.document import Document
from src.models.exercise import Exercise
from src.models.assignment import Assignment
from src.models.submission import Submission
from src.models.subject import Subject
from src.models.period import Period
from src.models.class_model import ClassModel
from src.models.class_view import ClassView
from src.models.resource import Resource

# this is the Alembic Config object
config = context.config

# Set sqlalchemy.url
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Setup logging
logging.basicConfig(level=logging.INFO)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
