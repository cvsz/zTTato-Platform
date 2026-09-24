"""zTTato API. All TikTok secrets stay server-side; a browser session is not a TikTok access token."""
import html
import os
import secrets
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import Settings, load_settings
from app.db import BrowserSession, LinkedAccount, MediaAsset, OAuthRequest, PublishJob, MIGRATION_HEAD, make_session_factory
from app.security import TokenCipher, browser_session, digest, new_browser_session, require_csrf
from app.tiktok import TikTokClient

WEB = Path(__file__).resolve().parent.parent / "web"
COOKIE = "zttato_session"
CSRF = "zttato_csrf"


class PublishInput(BaseModel):
    media_id: str
    mode: str
    idempotency_key: str = Field(min_length=16, max_length=128)
    caption: str = Field(default="", max_length=2200)
    privacy: str | None = None
    consent: bool
    disable_comment: bool = False
    disable_duet: bool = False
    disable_stitch: bool = False
    brand_content_toggle: bool = False
    brand_organic_toggle: bool = False
    is_aigc: bool = False


def create_app(settings: Settings | None = None) -> FastAPI:
    s = settings or load_settings()
    app = FastAPI(title="zTTato Creator", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(s.allowed_hosts))
    app.mount("/assets", StaticFiles(directory=WEB), name="assets")
    Path(s.media_dir).mkdir(parents=True, exist_ok=True)
    if s.database_url.startswith("sqlite:///"):
        Path(s.database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    engine, session_factory = make_session_factory(s.database_url, bootstrap=s.env != "production")
    cipher = TokenCipher(s.encryption_key)
    app.state.tiktok = TikTokClient(s)
    app.state.settings = s

    def db():
        with session_factory() as session:
            yield session

    def tiktok(request: Request) -> TikTokClient:
        return request.app.state.tiktok

    def current(request: Request, session: Session = Depends(db)) -> BrowserSession:
        return browser_session(request, session)

    def account(row: BrowserSession, session: Session, scope: str | None = None) -> LinkedAccount:
        found = session.scalar(select(LinkedAccount).where(LinkedAccount.session_id == row.id))
        if not found:
            raise HTTPException(401, "Connect your TikTok account first")
        if scope and scope not in found.scopes.split(","):
            raise HTTPException(403, "TikTok permission missing; reconnect with the requested scope")
        return found

    async def access(found: LinkedAccount, session: Session, client: TikTokClient) -> str:
        now = int(time.time())
        if found.access_expires_at > now + 120:
            return cipher.decrypt(found.access_cipher)
        if found.refresh_expires_at <= now + 120:
            raise HTTPException(401, "TikTok authorization expired; reconnect")
        tokens = await client.refresh(cipher.decrypt(found.refresh_cipher))
        if tokens.get("open_id") != found.open_id or not tokens.get("access_token"):
            raise HTTPException(502, "Unexpected refresh response; reconnect")
        found.access_cipher = cipher.encrypt(tokens["access_token"])
        found.refresh_cipher = cipher.encrypt(tokens.get("refresh_token") or cipher.decrypt(found.refresh_cipher))
        found.access_expires_at = now + int(tokens.get("expires_in", 3600))
        found.refresh_expires_at = now + int(tokens.get("refresh_expires_in", 0))
        found.scopes = tokens.get("scope", found.scopes)
        session.commit()
        return tokens["access_token"]

    def issue_cookies(response, raw: str, csrf: str):
        response.set_cookie(COOKIE, raw, max_age=86400, secure=s.secure_cookies, httponly=True, samesite="lax")
        response.set_cookie(CSRF, csrf, max_age=86400, secure=s.secure_cookies, httponly=False, samesite="lax")

    def safe_legal(page: str) -> str:
        original = (WEB / page).read_text("utf-8")
        values = {
            "{{LEGAL_ENTITY}}": html.escape(s.legal_entity or "Legal operator details pending"),
            "{{LEGAL_EMAIL}}": html.escape(s.legal_email or "Contact details pending"),
            "{{LEGAL_ADDRESS}}": html.escape(s.legal_address or "Address pending legal review"),
        }
        for old, new in values.items():
            original = original.replace(old, new)
        return original

    @app.middleware("http")
    async def hardened_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
            "img-src 'self' data:; connect-src 'self'; form-action 'self'"
        )
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith(("/api/", "/tiktok/")) else "public, max-age=300"
        if s.secure_cookies:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.get("/", include_in_schema=False)
    def homepage():
        return FileResponse(WEB / "index.html")

    @app.get("/dashboard", include_in_schema=False)
    def dashboard():
        return FileResponse(WEB / "dashboard.html")

    @app.get("/review-preview", include_in_schema=False)
    def review_preview():
        return FileResponse(WEB / "review-preview.html")

    @app.get("/privacy-policy", include_in_schema=False)
    def privacy_policy():
        return HTMLResponse(safe_legal("privacy-policy.html"))

    @app.get("/terms-of-service", include_in_schema=False)
    def terms_of_service():
        return HTMLResponse(safe_legal("terms-of-service.html"))

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready(session: Session = Depends(db)):
        try:
            session.execute(text("SELECT 1"))
            if s.env == "production":
                revision = session.scalar(text("SELECT version_num FROM alembic_version"))
                if revision != MIGRATION_HEAD:
                    raise HTTPException(503, "Database migration is not current")
        except SQLAlchemyError as exc:
            raise HTTPException(503, "Database is unavailable or migrations are missing") from exc
        return {"status": "ready"}

    @app.get("/api/session")
    def session_view(request: Request, session: Session = Depends(db)):
        try:
            row = browser_session(request, session)
            csrf = request.cookies.get(CSRF, "")
            if not csrf or not secrets.compare_digest(digest(csrf), row.csrf_hash):
                raise HTTPException(401)
            raw = request.cookies[COOKIE]
            response = JSONResponse({
                "connected": False, "scopes": [], "audited": s.app_audited,
                "legal_ready": bool(s.legal_entity and s.legal_email and s.legal_address),
            })
        except HTTPException:
            raw, csrf, row = new_browser_session(session)
            response = JSONResponse({
                "connected": False, "scopes": [], "audited": s.app_audited,
                "legal_ready": bool(s.legal_entity and s.legal_email and s.legal_address),
            })
        linked = session.scalar(select(LinkedAccount).where(LinkedAccount.session_id == row.id))
        if linked:
            response = JSONResponse({
                "connected": True, "scopes": linked.scopes.split(","),
                "audited": s.app_audited,
                "legal_ready": bool(s.legal_entity and s.legal_email and s.legal_address),
            })
        issue_cookies(response, raw, csrf)
        return response

    @app.get("/auth/tiktok/start")
    def start(request: Request, session: Session = Depends(db)):
        if not s.client_key or s.client_key.startswith("REPLACE_"):
            raise HTTPException(503, "TikTok Client Key is not configured")
        try:
            row = browser_session(request, session)
            raw, csrf = request.cookies[COOKIE], request.cookies.get(CSRF, "")
            if not csrf or digest(csrf) != row.csrf_hash:
                raise HTTPException(401)
        except HTTPException:
            raw, csrf, row = new_browser_session(session)
        state = secrets.token_urlsafe(32)
        session.add(OAuthRequest(state_hash=digest(state), session_id=row.id, expires_at=int(time.time()) + 600))
        session.commit()
        query = urlencode({
            "client_key": s.client_key, "response_type": "code", "scope": ",".join(s.scopes),
            "redirect_uri": s.redirect_uri, "state": state,
        })
        response = RedirectResponse(TikTokClient.AUTHORIZE + "?" + query, status_code=302)
        issue_cookies(response, raw, csrf)
        return response

    @app.get("/tiktok/callback")
    async def callback(
        request: Request, state: str = "", code: str = "", error: str = "",
        session: Session = Depends(db), client: TikTokClient = Depends(tiktok)
    ):
        if error:
            return RedirectResponse("/?error=authorization_denied", status_code=303)
        row = browser_session(request, session)
        if not state or not code:
            raise HTTPException(400, "Missing OAuth authorization response")
        pending = session.get(OAuthRequest, digest(state))
        if not pending or pending.session_id != row.id or pending.expires_at <= int(time.time()):
            raise HTTPException(403, "Invalid or expired OAuth state")
        session.delete(pending)
        session.commit()
        tokens = await client.exchange(code)
        required = ("open_id", "access_token", "refresh_token", "scope", "expires_in", "refresh_expires_in")
        if any(not tokens.get(key) for key in required):
            raise HTTPException(502, "Incomplete TikTok authorization response")
        now = int(time.time())
        found = session.scalar(select(LinkedAccount).where(LinkedAccount.session_id == row.id))
        if not found:
            found = LinkedAccount(
                session_id=row.id, open_id=tokens["open_id"], scopes=tokens["scope"],
                access_cipher="", refresh_cipher="", access_expires_at=0, refresh_expires_at=0
            )
            session.add(found)
        found.open_id = tokens["open_id"]
        found.scopes = tokens["scope"]
        found.access_cipher = cipher.encrypt(tokens["access_token"])
        found.refresh_cipher = cipher.encrypt(tokens["refresh_token"])
        found.access_expires_at = now + int(tokens["expires_in"])
        found.refresh_expires_at = now + int(tokens["refresh_expires_in"])
        session.commit()
        return RedirectResponse("/dashboard?connected=1", status_code=303)

    @app.get("/api/creator-info")
    async def creator_info(
        row: BrowserSession = Depends(current), session: Session = Depends(db),
        client: TikTokClient = Depends(tiktok)
    ):
        found = account(row, session, "video.publish")
        info = await client.creator_info(await access(found, session, client))
        return {
            "nickname": info.get("creator_nickname", ""), "username": info.get("creator_username", ""),
            "privacy_level_options": info.get("privacy_level_options", []),
            "comment_disabled": info.get("comment_disabled", False),
            "duet_disabled": info.get("duet_disabled", False),
            "stitch_disabled": info.get("stitch_disabled", False),
            "max_video_post_duration_sec": info.get("max_video_post_duration_sec"),
        }

    @app.post("/api/media")
    async def add_media(
        request: Request, file: UploadFile = File(...), session: Session = Depends(db),
        row: BrowserSession = Depends(current)
    ):
        require_csrf(request, row)
        account(row, session)
        if file.content_type not in ("video/mp4", "application/octet-stream"):
            raise HTTPException(415, "MP4 videos only")
        item_id = str(uuid.uuid4())
        path = Path(s.media_dir) / (item_id + ".mp4")
        size = 0
        try:
            with path.open("xb") as dest:
                os.chmod(path, 0o600)
                header = await file.read(12)
                if len(header) < 12 or header[4:8] != b"ftyp":
                    raise HTTPException(415, "Invalid MP4 file header")
                dest.write(header)
                size = len(header)
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > s.max_video_bytes:
                        raise HTTPException(413, "Video exceeds 64 MiB server upload limit")
                    dest.write(chunk)
        except Exception:
            path.unlink(missing_ok=True)
            raise
        finally:
            await file.close()
        asset = MediaAsset(id=item_id, session_id=row.id, filename=Path(file.filename or "video.mp4").name[:200],
                           size=size, path=str(path))
        session.add(asset)
        session.commit()
        return {"media_id": item_id, "filename": asset.filename, "size": size}

    @app.post("/api/publish")
    async def publish(
        request: Request, payload: PublishInput, row: BrowserSession = Depends(current),
        session: Session = Depends(db), client: TikTokClient = Depends(tiktok)
    ):
        require_csrf(request, row)
        if not payload.consent:
            raise HTTPException(422, "Explicit confirmation is required")
        if payload.mode not in ("draft", "direct"):
            raise HTTPException(422, "Choose draft or direct")
        earlier = session.scalar(select(PublishJob).where(
            PublishJob.session_id == row.id, PublishJob.idempotency_key == payload.idempotency_key
        ))
        if earlier:
            if earlier.media_id != payload.media_id or earlier.mode != payload.mode:
                raise HTTPException(409, "Idempotency key already belongs to a different request")
            return {"job_id": earlier.id, "status": earlier.status, "publish_id": earlier.publish_id,
                    "idempotent_replay": True}
        media = session.scalar(select(MediaAsset).where(
            MediaAsset.id == payload.media_id, MediaAsset.session_id == row.id
        ))
        if not media or not Path(media.path).is_file():
            raise HTTPException(404, "Upload a video first")
        required_scope = "video.publish" if payload.mode == "direct" else "video.upload"
        linked = account(row, session, required_scope)
        token = await access(linked, session, client)
        privacy = None
        if payload.mode == "direct":
            creator = await client.creator_info(token)
            options = creator.get("privacy_level_options", [])
            if payload.privacy not in options:
                raise HTTPException(422, "Privacy selection is unavailable for this creator")
            if not s.app_audited and payload.privacy != "SELF_ONLY":
                raise HTTPException(422, "Unaudited clients must use SELF_ONLY")
            if creator.get("comment_disabled") and not payload.disable_comment:
                raise HTTPException(422, "This creator has disabled comments")
            if creator.get("duet_disabled") and not payload.disable_duet:
                raise HTTPException(422, "This creator has disabled duets")
            if creator.get("stitch_disabled") and not payload.disable_stitch:
                raise HTTPException(422, "This creator has disabled stitches")
            privacy = payload.privacy
        job = PublishJob(id=str(uuid.uuid4()), session_id=row.id, idempotency_key=payload.idempotency_key,
                         media_id=media.id, mode=payload.mode, status="INITIATING")
        session.add(job)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            earlier = session.scalar(select(PublishJob).where(
                PublishJob.session_id == row.id, PublishJob.idempotency_key == payload.idempotency_key
            ))
            if earlier:
                return {"job_id": earlier.id, "status": earlier.status, "publish_id": earlier.publish_id,
                        "idempotent_replay": True}
            raise
        try:
            publish_id, upload_url = await client.init_video(
                token, mode=payload.mode, media_size=media.size, caption=payload.caption,
                privacy=privacy, disable_comment=payload.disable_comment,
                disable_duet=payload.disable_duet, disable_stitch=payload.disable_stitch,
                brand_content_toggle=payload.brand_content_toggle,
                brand_organic_toggle=payload.brand_organic_toggle, is_aigc=payload.is_aigc
            )
            job.publish_id = publish_id
            job.status = "TRANSFER_PENDING"
            session.commit()
            await client.upload_video(upload_url, media.path, media.size)
            job.status = "PROCESSING"
            session.commit()
        except Exception:
            job.status = "RECONCILIATION_REQUIRED" if job.publish_id else "INITIATION_FAILED"
            session.commit()
            raise
        return {"job_id": job.id, "status": job.status, "publish_id": job.publish_id,
                "note": "Draft uploads require the creator to finish posting inside TikTok." if payload.mode == "draft"
                else "TikTok is processing your consented direct post."}

    @app.get("/api/jobs/{job_id}")
    async def job_status(
        job_id: str, row: BrowserSession = Depends(current), session: Session = Depends(db),
        client: TikTokClient = Depends(tiktok)
    ):
        job = session.scalar(select(PublishJob).where(
            PublishJob.id == job_id, PublishJob.session_id == row.id
        ))
        if not job:
            raise HTTPException(404, "Job not found")
        now = int(time.time())
        if job.publish_id and (not job.checked_at or now - job.checked_at >= 30):
            linked = account(row, session)
            result = await client.status(await access(linked, session, client), job.publish_id)
            job.status = str(result.get("status", job.status))[:40]
            job.fail_reason = str(result.get("fail_reason", ""))[:160] or None
            job.checked_at = now
            session.commit()
        return {"job_id": job.id, "status": job.status, "fail_reason": job.fail_reason,
                "mode": job.mode, "publish_id": job.publish_id}

    @app.post("/api/disconnect")
    async def disconnect(
        request: Request, row: BrowserSession = Depends(current), session: Session = Depends(db),
        client: TikTokClient = Depends(tiktok)
    ):
        require_csrf(request, row)
        found = account(row, session)
        token = await access(found, session, client)
        await client.revoke(token)
        session.delete(found)
        session.commit()
        return {"disconnected": True}

    @app.delete("/api/my-data")
    async def delete_my_data(
        request: Request, row: BrowserSession = Depends(current), session: Session = Depends(db),
        client: TikTokClient = Depends(tiktok)
    ):
        require_csrf(request, row)
        found = session.scalar(select(LinkedAccount).where(LinkedAccount.session_id == row.id))
        if found:
            await client.revoke(await access(found, session, client))
            session.delete(found)
        jobs = session.scalars(select(PublishJob).where(PublishJob.session_id == row.id)).all()
        for job in jobs:
            session.delete(job)
        assets = session.scalars(select(MediaAsset).where(MediaAsset.session_id == row.id)).all()
        for asset in assets:
            Path(asset.path).unlink(missing_ok=True)
            session.delete(asset)
        states = session.scalars(select(OAuthRequest).where(OAuthRequest.session_id == row.id)).all()
        for state in states:
            session.delete(state)
        session.delete(row)
        session.commit()
        response = JSONResponse({"deleted": True})
        response.delete_cookie(COOKIE)
        response.delete_cookie(CSRF)
        return response

    return app


app = create_app()
