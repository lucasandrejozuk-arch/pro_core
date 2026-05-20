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


def test_production_requires_strong_secret_key() -> None:
    with pytest.raises(ValidationError):
        Settings(pro_core_env="production")
