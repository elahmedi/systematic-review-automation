from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["OPENAI_API_KEY"] = "test"

from risk_of_bias import web
from risk_of_bias.config import Settings
from risk_of_bias.types._framework_types import Framework


def fake_run_framework(
    manuscript: Path,
    framework,
    model: str,
    verbose: bool = False,
    temperature: float = 0.2,
    api_key: str | None = None,
) -> Framework:
    result = Framework(name="Test Framework")
    result.manuscript = Path(manuscript).name
    return result


def test_index_returns_form():
    client = TestClient(web.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "<form" in response.text
    assert '<select id="model"' in response.text


def test_analyze_and_download(tmp_path, monkeypatch):
    monkeypatch.setattr(web, "run_framework", fake_run_framework)

    client = TestClient(web.app)

    pdf = tmp_path / "manuscript.pdf"
    pdf.write_bytes(b"dummy")

    with pdf.open("rb") as f:
        response = client.post(
            "/analyze",
            data={"model": "dummy-model"},
            files={"file": ("manuscript.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    assert "Download Results" in response.text
    assert "JSON" in response.text

    match = re.search(r"/download/(\w+)/result.json", response.text)
    assert match
    file_id = match.group(1)

    download_resp = client.get(f"/download/{file_id}/result.json")
    assert download_resp.status_code == 200
    assert download_resp.headers["content-type"] == "application/json"


def test_login_page_renders():
    """Test that the login page renders correctly."""
    client = TestClient(web.app)
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign in" in response.text or "Sign In" in response.text
    assert '<form action="/login"' in response.text
    assert 'name="username"' in response.text
    assert 'name="password"' in response.text


def test_login_page_shows_error():
    """Test that the login page shows an error when requested."""
    client = TestClient(web.app)
    response = client.get("/login?error=1")
    assert response.status_code == 200
    assert "Invalid username or password" in response.text


def test_auth_disabled_allows_access():
    """Test that when auth is disabled, all endpoints are accessible."""
    # Default settings have auth disabled (no username/password set)
    client = TestClient(web.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "<form" in response.text


def test_auth_enabled_redirects_to_login(monkeypatch):
    """Test that when auth is enabled, unauthenticated users are redirected."""
    # Create settings with auth enabled
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)

    client = TestClient(web.app, follow_redirects=False)
    response = client.get("/")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_success_sets_cookie(monkeypatch):
    """Test that successful login sets a session cookie."""
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)

    client = TestClient(web.app, follow_redirects=False)
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "session_token" in response.cookies


def test_login_failure_redirects_with_error(monkeypatch):
    """Test that failed login redirects to login page with error."""
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)

    client = TestClient(web.app, follow_redirects=False)
    response = client.post(
        "/login",
        data={"username": "wronguser", "password": "wrongpass"},
    )
    assert response.status_code == 303
    assert "error=1" in response.headers["location"]


def test_logout_clears_cookie(monkeypatch):
    """Test that logout clears the session cookie."""
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)

    client = TestClient(web.app, follow_redirects=False)

    # First login to get a cookie
    login_response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
    )
    assert "session_token" in login_response.cookies

    # Now logout
    logout_response = client.get(
        "/logout",
        cookies={"session_token": login_response.cookies["session_token"]},
    )
    assert logout_response.status_code == 303
    assert logout_response.headers["location"] == "/login"


def test_authenticated_user_can_access_index(monkeypatch):
    """Test that an authenticated user can access the index page."""
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)

    client = TestClient(web.app, follow_redirects=False)

    # Login first
    login_response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
    )

    # Access index with session cookie
    response = client.get(
        "/",
        cookies={"session_token": login_response.cookies["session_token"]},
    )
    assert response.status_code == 200
    assert "<form" in response.text
    # Should have logout button when auth is enabled
    assert "Sign Out" in response.text


def test_analyze_requires_auth_when_enabled(tmp_path, monkeypatch):
    """Test that the analyze endpoint requires authentication when enabled."""
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)
    monkeypatch.setattr(web, "run_framework", fake_run_framework)

    client = TestClient(web.app, follow_redirects=False)

    pdf = tmp_path / "manuscript.pdf"
    pdf.write_bytes(b"dummy")

    # Try without authentication
    with pdf.open("rb") as f:
        response = client.post(
            "/analyze",
            data={"model": "dummy-model"},
            files={"file": ("manuscript.pdf", f, "application/pdf")},
        )
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_download_requires_auth_when_enabled(monkeypatch):
    """Test that the download endpoint requires authentication when enabled."""
    test_settings = Settings(
        web_username="testuser",
        web_password="testpass",
        web_secret_key="testsecret",
    )
    monkeypatch.setattr(web, "settings", test_settings)

    client = TestClient(web.app, follow_redirects=False)

    response = client.get("/download/fakeid/result.json")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_session_token_verification():
    """Test that session token verification works correctly."""
    # Test with valid token
    token = web._create_session_token("testuser")
    username = web._verify_session_token(token)
    assert username == "testuser"

    # Test with invalid token
    assert web._verify_session_token("invalid:token:signature") is None
    assert web._verify_session_token("malformed") is None
    assert web._verify_session_token("") is None
