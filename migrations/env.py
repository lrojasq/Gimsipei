from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Importar Base y todos los modelos para que Alembic los detecte
from src.database.database import Base, DATABASE_URL
from src.models import *  # noqa: F401, F403

# Configuración de Alembic
config = context.config

# Configurar logging desde alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Establecer la URL de la base de datos desde nuestro config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Metadata de los modelos para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'.
    
    Genera SQL sin conectarse a la base de datos.
    Útil para revisar los cambios antes de aplicarlos.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo 'online'.
    
    Se conecta a la base de datos y aplica los cambios.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
