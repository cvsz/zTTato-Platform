import hashlib
import hmac
import secrets
import time

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.db import BrowserSession


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class TokenCipher:
    def __init__(self, key: str):
        if not key:
            key = Fernet.generate_key().decode()
        self._fernet = Fernet(key.encode())

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except InvalidToken as exc:
            raise HTTPException(503, "Token key unavailable; reconnect TikTok") from exc


def new_browser_session(db: Session) -> tuple[str, str, BrowserSession]:
    raw, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    row = BrowserSession(id=digest(raw), csrf_hash=digest(csrf), expires_at=int(time.time()) + 86400)
    db.add(row)
    db.commit()
    return raw, csrf, row


def browser_session(request: Request, db: Session) -> BrowserSession:
    raw = request.cookies.get("zttato_session", "")
    if not raw:
        raise HTTPException(401, "Start a browser session")
    row = db.get(BrowserSession, digest(raw))
    if not row or row.expires_at <= int(time.time()):
        raise HTTPException(401, "Session expired")
    return row


def require_csrf(request: Request, row: BrowserSession) -> None:
    token = request.headers.get("x-csrf-token", "")
    if not token or not hmac.compare_digest(digest(token), row.csrf_hash):
        raise HTTPException(403, "Invalid CSRF token")
