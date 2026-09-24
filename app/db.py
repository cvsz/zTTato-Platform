import time

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

MIGRATION_HEAD = "20260924_01"


class Base(DeclarativeBase):
    pass


class BrowserSession(Base):
    __tablename__ = "browser_sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    csrf_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()))


class OAuthRequest(Base):
    __tablename__ = "oauth_requests"
    state_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("browser_sessions.id"), index=True)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)


class LinkedAccount(Base):
    __tablename__ = "linked_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("browser_sessions.id"), unique=True, index=True)
    open_id: Mapped[str] = mapped_column(String(128), nullable=False)
    scopes: Mapped[str] = mapped_column(Text, default="")
    access_cipher: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_cipher: Mapped[str] = mapped_column(Text, nullable=False)
    access_expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
    refresh_expires_at: Mapped[int] = mapped_column(Integer, nullable=False)


class MediaAsset(Base):
    __tablename__ = "media_assets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("browser_sessions.id"), index=True)
    filename: Mapped[str] = mapped_column(String(200), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()))


class PublishJob(Base):
    __tablename__ = "publish_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("browser_sessions.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    media_id: Mapped[str] = mapped_column(ForeignKey("media_assets.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String(12), nullable=False)
    publish_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="INITIATING")
    fail_reason: Mapped[str | None] = mapped_column(String(160), nullable=True)
    checked_at: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()))
    __table_args__ = (UniqueConstraint("session_id", "idempotency_key", name="uq_publish_once"),)


def make_session_factory(database_url: str, *, bootstrap: bool = True):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
    if bootstrap:
        Base.metadata.create_all(engine)  # Local development and isolated tests only.
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
