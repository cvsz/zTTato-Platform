from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def settings(tmp_path: Path) -> Settings:
    return Settings(
        env="test",
        base_url="http://testserver",
        allowed_hosts=("testserver",),
        database_url="sqlite:///" + str(tmp_path / "test.db"),
        encryption_key="",
        client_key="REPLACE_TEST",
        client_secret="REPLACE_TEST",
        scopes=("user.info.basic", "video.upload", "video.publish"),
        app_audited=False,
        legal_entity="Example Operator",
        legal_email="privacy@example.test",
        legal_address="Example Address",
        media_dir=str(tmp_path / "media"),
        max_video_bytes=1024 * 1024,
    )


def test_public_pages_and_headers(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    for path in ("/", "/dashboard", "/review-preview", "/privacy-policy", "/terms-of-service"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_session_is_created_without_exposing_tiktok_token(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    response = client.get("/api/session")
    assert response.status_code == 200
    assert response.json()["connected"] is False
    assert "zttato_session" in response.cookies
    assert "access_token" not in response.text


def test_oauth_start_fails_closed_without_real_client_key(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    response = client.get("/auth/tiktok/start", follow_redirects=False)
    assert response.status_code == 503


def test_readiness_uses_database(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_production_readiness_fails_without_migration(tmp_path):
    app = create_app(replace(settings(tmp_path), env="production"))
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 503
