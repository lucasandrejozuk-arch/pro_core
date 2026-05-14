from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.models.user import User


def _auth_headers(client: TestClient, user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "OldPassword123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_can_read_and_update_system_settings(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    get_response = client.get("/api/v1/settings", headers=auth_headers)
    assert get_response.status_code == 200
    settings = get_response.json()
    assert settings["company_name"] == "PRO CORE Test"
    assert settings["theme"] == "light"
    assert settings["backup_interval_hours"] == 24
    assert settings["backup_storage_path"] == "backups"

    update_response = client.patch(
        "/api/v1/settings",
        headers=auth_headers,
        json={
            "company_name": "Assistencia Atualizada",
            "trade_name": "PRO CORE Lab",
            "document_number": "12345678000199",
            "email": "contato@example.com",
            "phone": "1133334444",
            "theme": "dark",
            "backup_enabled": False,
            "backup_interval_hours": 12,
            "backup_storage_path": "D:/pro-core/backups",
        },
    )
    assert update_response.status_code == 200
    updated_settings = update_response.json()
    assert updated_settings["company_name"] == "Assistencia Atualizada"
    assert updated_settings["theme"] == "dark"
    assert updated_settings["backup_enabled"] is False
    assert updated_settings["backup_interval_hours"] == 12
    assert updated_settings["backup_storage_path"] == "D:/pro-core/backups"

    second_get_response = client.get("/api/v1/settings", headers=auth_headers)
    assert second_get_response.status_code == 200
    assert second_get_response.json()["theme"] == "dark"


def test_technician_cannot_access_system_settings(
    client: TestClient,
    technician_user: User,
) -> None:
    technician_headers = _auth_headers(client, technician_user)

    response = client.get("/api/v1/settings", headers=technician_headers)

    assert response.status_code == 403


def test_admin_can_run_manual_backup(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    def fake_run_database_backup(db, company_id):
        return {
            "file_name": "pro_core_20260514_063000.dump",
            "file_path": "backups/pro_core_20260514_063000.dump",
            "file_size_bytes": 1024,
            "created_at": datetime(2026, 5, 14, 6, 30, tzinfo=UTC),
            "validated": True,
        }

    monkeypatch.setattr(
        "backend.app.api.v1.routes.settings.run_database_backup",
        fake_run_database_backup,
    )

    response = client.post("/api/v1/settings/backup/run", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["file_name"] == "pro_core_20260514_063000.dump"
    assert body["validated"] is True
