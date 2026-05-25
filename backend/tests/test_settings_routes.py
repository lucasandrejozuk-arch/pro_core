from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.models.company import Company
from backend.app.models.user import User
from backend.app.services.configuration import set_setting_value


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
    assert settings["brand_name"] is None
    assert settings["color_palette"] == "blue"
    assert settings["primary_color"] == "#25636f"
    assert settings["language"] == "pt-BR"
    assert settings["login_cover_preset"] == "original"
    assert settings["login_cover_image_data_url"] is None
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
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "amber",
            "theme": "dark",
            "language": "en-US",
            "login_cover_preset": "precision_grid",
            "backup_enabled": False,
            "backup_interval_hours": 12,
            "backup_storage_path": "D:/pro-core/backups",
        },
    )
    assert update_response.status_code == 200
    updated_settings = update_response.json()
    assert updated_settings["company_name"] == "Assistencia Atualizada"
    assert updated_settings["brand_name"] == "Pro Assist"
    assert updated_settings["brand_subtitle"] == "Laboratorio tecnico"
    assert updated_settings["color_palette"] == "amber"
    assert updated_settings["primary_color"] == "#f2b84b"
    assert updated_settings["theme"] == "dark"
    assert updated_settings["language"] == "en-US"
    assert updated_settings["login_cover_preset"] == "precision_grid"
    assert updated_settings["login_cover_image_data_url"] is None
    assert updated_settings["backup_enabled"] is False
    assert updated_settings["backup_interval_hours"] == 12
    assert updated_settings["backup_storage_path"] == "D:/pro-core/backups"

    second_get_response = client.get("/api/v1/settings", headers=auth_headers)
    assert second_get_response.status_code == 200
    assert second_get_response.json()["theme"] == "dark"
    assert second_get_response.json()["color_palette"] == "amber"
    assert second_get_response.json()["primary_color"] == "#f2b84b"


def test_technician_cannot_access_system_settings(
    client: TestClient,
    technician_user: User,
) -> None:
    technician_headers = _auth_headers(client, technician_user)

    response = client.get("/api/v1/settings", headers=technician_headers)

    assert response.status_code == 403


def test_authenticated_users_can_read_appearance_settings(
    client: TestClient,
    technician_user: User,
) -> None:
    technician_headers = _auth_headers(client, technician_user)

    response = client.get("/api/v1/settings/appearance", headers=technician_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["theme"] == "light"
    assert body["color_palette"] == "blue"
    assert body["primary_color"] == "#25636f"
    assert body["language"] == "pt-BR"
    assert body["login_cover_preset"] == "original"
    assert body["login_cover_image_data_url"] is None


def test_login_appearance_is_public_and_uses_admin_branding(
    client: TestClient,
    db_session,
    company,
) -> None:
    set_setting_value(db_session, company.id, "ui.brand_name", "Pro Assist")
    set_setting_value(db_session, company.id, "ui.brand_subtitle", "Laboratorio tecnico")
    db_session.commit()

    response = client.get("/api/v1/settings/login-appearance")

    assert response.status_code == 200
    body = response.json()
    assert body["brand_name"] == "Pro Assist"
    assert body["brand_subtitle"] == "Laboratorio tecnico"
    assert body["color_palette"] == "blue"
    assert body["theme"] == "light"
    assert body["language"] == "pt-BR"
    assert body["login_cover_preset"] == "original"
    assert body["login_cover_image_data_url"] is None


def test_login_appearance_prefers_most_recently_customized_active_company(
    client: TestClient,
    db_session,
    company,
) -> None:
    older_company = company
    newer_company = Company(name="PRO CORE Branch")
    db_session.add(newer_company)
    db_session.commit()
    db_session.refresh(newer_company)

    set_setting_value(db_session, older_company.id, "ui.brand_name", "Marca Antiga")
    set_setting_value(db_session, older_company.id, "ui.brand_subtitle", "Laboratorio antigo")
    db_session.commit()

    set_setting_value(db_session, newer_company.id, "ui.brand_name", "Marca Atual")
    set_setting_value(db_session, newer_company.id, "ui.brand_subtitle", "Laboratorio atual")
    db_session.commit()

    response = client.get("/api/v1/settings/login-appearance")

    assert response.status_code == 200
    body = response.json()
    assert body["brand_name"] == "Marca Atual"
    assert body["brand_subtitle"] == "Laboratorio atual"


def test_admin_can_store_custom_login_cover(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    image_data_url = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhg"
        "GAWjR9awAAAABJRU5ErkJggg=="
    )

    response = client.patch(
        "/api/v1/settings",
        headers=auth_headers,
        json={
            "login_cover_preset": "custom",
            "login_cover_image_data_url": image_data_url,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["login_cover_preset"] == "custom"
    assert body["login_cover_image_data_url"] == image_data_url


def test_settings_reject_invalid_login_cover_payload(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/api/v1/settings",
        headers=auth_headers,
        json={
            "login_cover_preset": "custom",
            "login_cover_image_data_url": "data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=",
        },
    )

    assert response.status_code == 422


def test_settings_reject_invalid_color_palette(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/api/v1/settings",
        headers=auth_headers,
        json={"color_palette": "purple"},
    )

    assert response.status_code == 422


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
