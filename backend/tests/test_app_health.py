import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.core.config import Settings
from backend.app.main import create_app


def test_health_check_returns_application_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "app": "PRO CORE",
        "version": "0.1.0",
        "environment": "development",
        "status": "ok",
    }
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Content-Security-Policy"].startswith("default-src 'self'")


def test_production_requires_strong_secret_key() -> None:
    with pytest.raises(ValidationError):
        Settings(pro_core_env="production")


def test_production_disables_interactive_api_docs(monkeypatch) -> None:
    monkeypatch.setenv("PRO_CORE_ENV", "production")
    monkeypatch.setenv("PRO_CORE_SECRET_KEY", "x" * 40)
    from backend.app.core.config import get_settings

    get_settings.cache_clear()
    try:
        client = TestClient(create_app())
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert "Strict-Transport-Security" in client.get("/health").headers
    finally:
        get_settings.cache_clear()
