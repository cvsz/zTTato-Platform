"""Alembic environment: always obtain the database URL from the process environment."""
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db import Base

config = context.config
target_metadata = Base.metadata
url = os.environ.get("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL is required for migrations")
config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))


def run_migrations_offline() -> None:
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
