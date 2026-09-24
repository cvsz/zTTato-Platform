"""Verify that a fresh schema can upgrade and downgrade without production data."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.db import MIGRATION_HEAD

ROOT = Path(__file__).resolve().parents[1]


def test_versioned_fresh_migration(tmp_path, monkeypatch):
    url = "sqlite:///" + str(tmp_path / "migration.db")
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    inspector = inspect(engine)
    assert "alembic_version" in inspector.get_table_names()
    assert set(("browser_sessions", "oauth_requests", "linked_accounts", "media_assets", "publish_jobs")) <= set(
        inspector.get_table_names()
    )
    with engine.connect() as connection:
        from sqlalchemy import text

        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == MIGRATION_HEAD
    engine.dispose()
    command.downgrade(cfg, "base")
    inspector = inspect(create_engine(url))
    assert "publish_jobs" not in inspector.get_table_names()
