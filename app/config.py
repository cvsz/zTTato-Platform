import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    env: str
    base_url: str
    allowed_hosts: tuple[str, ...]
    database_url: str
    encryption_key: str
    client_key: str
    client_secret: str
    scopes: tuple[str, ...]
    app_audited: bool
    legal_entity: str
    legal_email: str
    legal_address: str
    media_dir: str
    max_video_bytes: int

    @property
    def redirect_uri(self) -> str:
        return self.base_url.rstrip("/") + "/tiktok/callback"

    @property
    def secure_cookies(self) -> bool:
        return self.base_url.startswith("https://")


def load_settings() -> Settings:
    get = os.environ.get
    s = Settings(
        env=get("APP_ENV", "development").lower(),
        base_url=get("APP_BASE_URL", "http://localhost:8000").rstrip("/"),
        allowed_hosts=tuple(x.strip() for x in get("APP_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if x.strip()),
        database_url=get("DATABASE_URL", "sqlite:///./data/zttato.db"),
        encryption_key=get("APP_ENCRYPTION_KEY", ""),
        client_key=get("TIKTOK_CLIENT_KEY", ""),
        client_secret=get("TIKTOK_CLIENT_SECRET", ""),
        scopes=tuple(x.strip() for x in get("TIKTOK_SCOPES", "user.info.basic,video.upload,video.publish").split(",") if x.strip()),
        app_audited=get("TIKTOK_APP_AUDITED", "false").lower() == "true",
        legal_entity=get("LEGAL_ENTITY", ""),
        legal_email=get("LEGAL_CONTACT_EMAIL", ""),
        legal_address=get("LEGAL_POSTAL_ADDRESS", ""),
        media_dir=get("MEDIA_DIR", "./media"),
        max_video_bytes=int(get("MAX_VIDEO_BYTES", "67108864")),
    )
    u = urlparse(s.base_url)
    if u.scheme not in ("https", "http") or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise ValueError("APP_BASE_URL must be an absolute URL without credentials or query")
    if s.env == "production":
        if u.scheme != "https":
            raise ValueError("Production APP_BASE_URL must use HTTPS")
        if "sqlite" in s.database_url or not s.encryption_key or s.encryption_key.startswith("REPLACE_"):
            raise ValueError("Production requires PostgreSQL and a persistent APP_ENCRYPTION_KEY")
        required = [s.client_key, s.client_secret, s.legal_entity, s.legal_email, s.legal_address]
        if any(not x or x.startswith("REPLACE_") for x in required):
            raise ValueError("Production TikTok and legal operator fields must be configured")
    if s.max_video_bytes < 1024 or s.max_video_bytes > 67108864:
        raise ValueError("MAX_VIDEO_BYTES must be between 1 KiB and 64 MiB")
    return s
