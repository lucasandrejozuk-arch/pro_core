from __future__ import annotations

import json

import httpx

from frontend.app.core.api_client import ApiClient


def test_list_users_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/users"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"full_name": "Admin"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_users("token")

    assert response == [{"full_name": "Admin"}]


def test_list_user_resource_access_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/users/resource-access"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"email": "tech@example.com"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_user_resource_access("token")

    assert response == [{"email": "tech@example.com"}]


def test_update_user_resource_access_puts_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/api/v1/users/user-id/resource-access"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == {"allowed_resources": ["dashboard", "tools"]}
        return httpx.Response(
            200, json={"user_id": "user-id", "allowed_resources": ["dashboard", "tools"]}
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_user_resource_access("token", "user-id", ["dashboard", "tools"])

    assert response["allowed_resources"] == ["dashboard", "tools"]


def test_create_user_posts_payload() -> None:
    payload = {
        "full_name": "Tecnico Novo",
        "email": "tecnico@example.com",
        "role": "technician",
        "sector_id": None,
        "password": "Temp123",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/users"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "user-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_user("token", payload)

    assert response["id"] == "user-id"


def test_update_user_patches_payload() -> None:
    payload = {
        "full_name": "Tecnico Atualizado",
        "email": "tecnico@example.com",
        "role": "technician",
        "sector_id": None,
        "is_active": True,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/users/user-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "user-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_user("token", "user-id", payload)

    assert response["full_name"] == "Tecnico Atualizado"


def test_reset_user_password_posts_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/users/user-id/reset-password"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == {"new_password": "NovaSenha123"}
        return httpx.Response(200, json={"id": "user-id", "must_change_password": True})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.reset_user_password("token", "user-id", "NovaSenha123")

    assert response["must_change_password"] is True


def test_list_password_reset_requests_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/password-reset-requests"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"requester_email": "tecnico@example.com"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_password_reset_requests("token")

    assert response == [{"requester_email": "tecnico@example.com"}]


def test_resolve_password_reset_request_posts_new_password() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/password-reset-requests/request-id/resolve"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == {"new_password": "NovaSenha123"}
        return httpx.Response(200, json={"id": "request-id", "status": "resolved"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.resolve_password_reset_request(
        "token",
        "request-id",
        "NovaSenha123",
    )

    assert response["status"] == "resolved"


def test_cancel_password_reset_request_posts_cancel_action() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/password-reset-requests/request-id/cancel"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"id": "request-id", "status": "cancelled"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.cancel_password_reset_request("token", "request-id")

    assert response["status"] == "cancelled"


def test_list_sectors_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/sectors"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"name": "Laboratorio"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_sectors("token")

    assert response == [{"name": "Laboratorio"}]


def test_create_sector_posts_payload() -> None:
    payload = {"name": "Laboratorio", "description": "Bancada tecnica"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/sectors"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "sector-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_sector("token", payload)

    assert response["id"] == "sector-id"


def test_update_sector_patches_payload() -> None:
    payload = {"name": "Laboratorio", "description": "Atendimento interno"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/sectors/sector-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "sector-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_sector("token", "sector-id", payload)

    assert response["description"] == "Atendimento interno"


def test_get_settings_returns_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/settings"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(
            200,
            json={
                "company_name": "PRO CORE Test",
                "theme": "light",
                "backup_interval_hours": 24,
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.get_settings("token")

    assert response["theme"] == "light"


def test_get_appearance_settings_returns_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/settings/appearance"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(
            200,
            json={
                "brand_name": "Pro Assist",
                "brand_subtitle": "Laboratorio tecnico",
                "color_palette": "green",
                "primary_color": "#0f766e",
                "theme": "dark",
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.get_appearance_settings("token")

    assert response["brand_name"] == "Pro Assist"


def test_get_login_appearance_settings_is_public() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/settings/login-appearance"
        assert "Authorization" not in request.headers
        return httpx.Response(
            200,
            json={
                "brand_name": "Pro Assist",
                "brand_subtitle": "Laboratorio tecnico",
                "color_palette": "green",
                "primary_color": "#0f766e",
                "theme": "dark",
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.get_login_appearance_settings()

    assert response["brand_subtitle"] == "Laboratorio tecnico"


def test_update_settings_patches_payload() -> None:
    payload = {
        "company_name": "Assistencia Atualizada",
        "trade_name": "PRO CORE Lab",
        "document_number": "12345678000199",
        "email": "contato@example.com",
        "phone": "1133334444",
        "brand_name": "Pro Assist",
        "brand_subtitle": "Laboratorio tecnico",
        "color_palette": "green",
        "theme": "dark",
        "backup_enabled": True,
        "backup_interval_hours": 12,
        "backup_storage_path": "D:/pro-core/backups",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/settings"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload)

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_settings("token", payload)

    assert response["company_name"] == "Assistencia Atualizada"


def test_run_backup_posts_to_settings_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/settings/backup/run"
        assert request.headers["Authorization"] == "Bearer token"
        assert request.content == b""
        return httpx.Response(
            200,
            json={
                "file_name": "pro_core_20260514_063000.dump",
                "file_path": "backups/pro_core_20260514_063000.dump",
                "file_size_bytes": 1024,
                "validated": True,
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.run_backup("token")

    assert response["validated"] is True


def test_audit_list_calls_expected_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/audit-logs"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    assert client.list_audit_logs("token") == []


def test_list_tools_calls_tools_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/tools"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"id": "ohm", "name": "Lei de Ohm"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    assert client.list_tools("token")[0]["id"] == "ohm"
