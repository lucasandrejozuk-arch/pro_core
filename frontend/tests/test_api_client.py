from __future__ import annotations

import json

import httpx
import pytest

from frontend.app.core.api_client import ApiClient, ApiError


def test_login_posts_credentials_and_returns_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/auth/login"
        assert json.loads(request.content) == {
            "email": "admin@example.com",
            "password": "secret",
        }
        return httpx.Response(
            200,
            json={
                "access_token": "token",
                "token_type": "bearer",
                "must_change_password": True,
                "user": {"email": "admin@example.com"},
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.login("admin@example.com", "secret")

    assert response["access_token"] == "token"
    assert response["must_change_password"] is True


def test_me_sends_bearer_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"email": "admin@example.com"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.me("token")

    assert response["email"] == "admin@example.com"


def test_change_password_posts_expected_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        assert request.url.path == "/api/v1/auth/change-password"
        assert json.loads(request.content) == {
            "current_password": "old-password",
            "new_password": "new-password",
        }
        return httpx.Response(200, json={"must_change_password": False})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.change_password("token", "old-password", "new-password")

    assert response["must_change_password"] is False


def test_request_password_reset_posts_email() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/auth/password-reset-requests"
        assert json.loads(request.content) == {"email": "user@example.com"}
        return httpx.Response(200, json={"message": "Solicitacao enviada."})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.request_password_reset("user@example.com")

    assert response["message"] == "Solicitacao enviada."


def test_error_response_raises_api_error_with_backend_detail() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid email or password."})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ApiError) as exc_info:
        client.login("admin@example.com", "wrong")

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Invalid email or password."


def test_list_customers_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/customers"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"name": "Cliente Teste"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_customers("token")

    assert response == [{"name": "Cliente Teste"}]


def test_create_customer_posts_payload() -> None:
    payload = {
        "name": "Cliente Teste",
        "document_number": None,
        "email": "cliente@example.com",
        "phone": "11999999999",
        "address": None,
        "notes": None,
        "is_active": True,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/customers"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "customer-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_customer("token", payload)

    assert response["id"] == "customer-id"


def test_update_customer_patches_payload() -> None:
    payload = {"name": "Cliente Atualizado", "phone": "11888888888"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/customers/customer-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "customer-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_customer("token", "customer-id", payload)

    assert response["name"] == "Cliente Atualizado"


def test_create_equipment_posts_payload() -> None:
    payload = {
        "customer_id": "customer-id",
        "category": "Notebook",
        "brand": "Dell",
        "model": "Latitude",
        "serial_number": "ABC123",
        "description": "Nao liga",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/equipment"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "equipment-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_equipment("token", payload)

    assert response["id"] == "equipment-id"


def test_update_equipment_patches_payload() -> None:
    payload = {
        "customer_id": "customer-id",
        "category": "Desktop",
        "brand": None,
        "model": None,
        "serial_number": None,
        "description": None,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/equipment/equipment-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "equipment-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_equipment("token", "equipment-id", payload)

    assert response["category"] == "Desktop"


def test_create_inventory_item_posts_payload() -> None:
    payload = {
        "sku": "SSD-001",
        "name": "SSD 480GB",
        "category": "Armazenamento",
        "quantity": "10",
        "minimum_quantity": "2",
        "unit_cost": "180.50",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/inventory"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "item-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_inventory_item("token", payload)

    assert response["id"] == "item-id"


def test_update_inventory_item_patches_payload() -> None:
    payload = {
        "sku": "SSD-001",
        "name": "SSD 480GB",
        "category": "Armazenamento",
        "quantity": "8",
        "minimum_quantity": "2",
        "unit_cost": "175",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/inventory/item-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "item-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_inventory_item("token", "item-id", payload)

    assert response["quantity"] == "8"


def test_list_technicians_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/users/technicians"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"full_name": "Tecnico"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_technicians("token")

    assert response == [{"full_name": "Tecnico"}]


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


def test_update_settings_patches_payload() -> None:
    payload = {
        "company_name": "Assistencia Atualizada",
        "trade_name": "PRO CORE Lab",
        "document_number": "12345678000199",
        "email": "contato@example.com",
        "phone": "1133334444",
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


def test_get_report_returns_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/reports/customers"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(
            200,
            json={
                "module": "customers",
                "title": "Relatorio de Clientes",
                "total_records": 1,
                "columns": [{"key": "name", "label": "Nome"}],
                "rows": [{"name": "Cliente"}],
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.get_report("token", "customers")

    assert response["rows"][0]["name"] == "Cliente"


def test_export_report_downloads_bytes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/reports/customers/export"
        assert request.url.params["format"] == "csv"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, content=b"Nome\nCliente\n")

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.export_report("token", "customers", "csv")

    assert response == b"Nome\nCliente\n"


def test_create_service_order_posts_payload() -> None:
    payload = {
        "customer_id": "customer-id",
        "equipment_id": "equipment-id",
        "assigned_technician_id": "technician-id",
        "problem_description": "Nao liga.",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/service-orders"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "service-order-id", "code": "OS-000001"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_service_order("token", payload)

    assert response["code"] == "OS-000001"


def test_update_service_order_patches_payload() -> None:
    payload = {
        "assigned_technician_id": None,
        "problem_description": "Falha intermitente.",
        "technical_diagnosis": "Fonte com oscilacao.",
        "rejection_reason": None,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/service-orders/service-order-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "service-order-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_service_order("token", "service-order-id", payload)

    assert response["technical_diagnosis"] == "Fonte com oscilacao."


@pytest.mark.parametrize(
    ("method_name", "args", "path", "expected_json"),
    [
        (
            "register_service_order_diagnosis",
            ("service-order-id", "SSD com falha."),
            "/api/v1/service-orders/service-order-id/diagnosis",
            {"technical_diagnosis": "SSD com falha."},
        ),
        (
            "add_service_order_budget_item",
            (
                "service-order-id",
                {
                    "inventory_item_id": None,
                    "item_type": "service",
                    "description": "Substituicao de SSD",
                    "quantity": "1",
                    "unit_price": "250.00",
                },
            ),
            "/api/v1/service-orders/service-order-id/budget-items",
            {
                "inventory_item_id": None,
                "item_type": "service",
                "description": "Substituicao de SSD",
                "quantity": "1",
                "unit_price": "250.00",
            },
        ),
        (
            "submit_service_order_quote",
            ("service-order-id",),
            "/api/v1/service-orders/service-order-id/submit-quote",
            None,
        ),
        (
            "approve_service_order",
            ("service-order-id",),
            "/api/v1/service-orders/service-order-id/approve",
            None,
        ),
        (
            "reject_service_order",
            ("service-order-id", "Cliente recusou o orcamento."),
            "/api/v1/service-orders/service-order-id/reject",
            {"rejection_reason": "Cliente recusou o orcamento."},
        ),
        (
            "start_service_order",
            ("service-order-id",),
            "/api/v1/service-orders/service-order-id/start",
            None,
        ),
        (
            "complete_service_order",
            ("service-order-id",),
            "/api/v1/service-orders/service-order-id/complete",
            None,
        ),
    ],
)
def test_service_order_flow_actions_call_expected_endpoints(
    method_name: str,
    args: tuple,
    path: str,
    expected_json: dict | None,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == path
        assert request.headers["Authorization"] == "Bearer token"
        if expected_json is None:
            assert request.content == b""
        else:
            assert json.loads(request.content) == expected_json
        return httpx.Response(200, json={"id": "service-order-id", "status": "ok"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = getattr(client, method_name)("token", *args)

    assert response["id"] == "service-order-id"


def test_list_documents_sends_service_order_filter() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/documents"
        assert request.url.params["service_order_id"] == "service-order-id"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"file_name": "diagnostico.txt"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_documents("token", service_order_id="service-order-id")

    assert response == [{"file_name": "diagnostico.txt"}]


def test_upload_document_posts_multipart_payload(tmp_path) -> None:
    document_path = tmp_path / "diagnostico.txt"
    document_path.write_text("conteudo do diagnostico", encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/documents"
        assert request.headers["Authorization"] == "Bearer token"
        assert "multipart/form-data" in request.headers["Content-Type"]
        body = request.content
        assert b"diagnostico.txt" in body
        assert b"service-order-id" in body
        assert b"other" in body
        return httpx.Response(201, json={"id": "document-id", "file_name": "diagnostico.txt"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.upload_document(
        access_token="token",
        file_path=str(document_path),
        document_type="other",
        service_order_id="service-order-id",
    )

    assert response["id"] == "document-id"


def test_list_endpoint_rejects_unexpected_object_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "object"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ApiError) as exc_info:
        client.list_service_orders("token")

    assert exc_info.value.message == "Resposta inesperada do backend."
