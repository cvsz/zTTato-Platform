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


def test_tiktok_site_verification_endpoint(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    response = client.get("/tiktok/uploading/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "tiktok-developers-site-verification=9WurARgpbnJkdus0r4bfvSZydNYNxKUC"


def test_session_is_created_without_exposing_tiktok_token(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    response = client.get("/api/session")
    assert response.status_code == 200
    assert response.json()["connected"] is False
    assert "zttato_session" in response.cookies
    assert "access_token" not in response.text


def test_existing_session_cookie_is_not_reflected_into_response(tmp_path):
    client = TestClient(create_app(settings(tmp_path)))
    created = client.get("/api/session")
    assert "set-cookie" in created.headers

    reused = client.get("/api/session")
    assert reused.status_code == 200
    assert "set-cookie" not in reused.headers


def test_oauth_start_only_sets_server_generated_session_cookies(tmp_path):
    app_settings = replace(settings(tmp_path), client_key="client-key")
    client = TestClient(create_app(app_settings))

    created = client.get("/auth/tiktok/start", follow_redirects=False)
    assert created.status_code == 302
    assert "set-cookie" in created.headers

    reused = client.get("/auth/tiktok/start", follow_redirects=False)
    assert reused.status_code == 302
    assert "set-cookie" not in reused.headers


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


def test_production_rejects_host_mismatch(tmp_path):
    bad = replace(
        settings(tmp_path),
        env="production",
        base_url="https://zttato.zeaz.dev",
        allowed_hosts=("localhost",),
        database_url="postgresql+psycopg://user:password@db:5432/zttato",
        encryption_key="valid-test-key",
        client_key="client-key",
        client_secret="client-secret",
    )
    try:
        create_app(bad)
    except ValueError as exc:
        assert "APP_ALLOWED_HOSTS" in str(exc)
    else:
        raise AssertionError("host mismatch must fail closed")


def test_production_rejects_url_values_in_allowed_hosts(tmp_path):
    bad = replace(
        settings(tmp_path),
        env="production",
        base_url="https://zttato.zeaz.dev",
        allowed_hosts=("https://zttato.zeaz.dev",),
        database_url="postgresql+psycopg://user:password@db:5432/zttato",
        encryption_key="valid-test-key",
        client_key="client-key",
        client_secret="client-secret",
    )
    try:
        create_app(bad)
    except ValueError as exc:
        assert "hostnames only" in str(exc)
    else:
        raise AssertionError("URL-shaped allowed host must fail closed")
