"""Initial persistent TikTok creator data schema.

Revision ID: 20260924_01
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "20260924_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "browser_sessions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("csrf_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
    )
    op.create_table(
        "oauth_requests",
        sa.Column("state_hash", sa.String(length=64), primary_key=True),
        sa.Column("session_id", sa.String(length=64), sa.ForeignKey("browser_sessions.id"), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
    )
    op.create_index("ix_oauth_requests_session_id", "oauth_requests", ["session_id"])
    op.create_table(
        "linked_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(length=64), sa.ForeignKey("browser_sessions.id"), nullable=False),
        sa.Column("open_id", sa.String(length=128), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column("access_cipher", sa.Text(), nullable=False),
        sa.Column("refresh_cipher", sa.Text(), nullable=False),
        sa.Column("access_expires_at", sa.Integer(), nullable=False),
        sa.Column("refresh_expires_at", sa.Integer(), nullable=False),
    )
    op.create_index("ix_linked_accounts_session_id", "linked_accounts", ["session_id"], unique=True)
    op.create_table(
        "media_assets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=64), sa.ForeignKey("browser_sessions.id"), nullable=False),
        sa.Column("filename", sa.String(length=200), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
    )
    op.create_index("ix_media_assets_session_id", "media_assets", ["session_id"])
    op.create_table(
        "publish_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=64), sa.ForeignKey("browser_sessions.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("media_id", sa.String(length=36), sa.ForeignKey("media_assets.id"), nullable=False),
        sa.Column("mode", sa.String(length=12), nullable=False),
        sa.Column("publish_id", sa.String(length=160)),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("fail_reason", sa.String(length=160)),
        sa.Column("checked_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.UniqueConstraint("session_id", "idempotency_key", name="uq_publish_once"),
    )
    op.create_index("ix_publish_jobs_session_id", "publish_jobs", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_publish_jobs_session_id", table_name="publish_jobs")
    op.drop_table("publish_jobs")
    op.drop_index("ix_media_assets_session_id", table_name="media_assets")
    op.drop_table("media_assets")
    op.drop_index("ix_linked_accounts_session_id", table_name="linked_accounts")
    op.drop_table("linked_accounts")
    op.drop_index("ix_oauth_requests_session_id", table_name="oauth_requests")
    op.drop_table("oauth_requests")
    op.drop_table("browser_sessions")
