from fastapi.testclient import TestClient

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

