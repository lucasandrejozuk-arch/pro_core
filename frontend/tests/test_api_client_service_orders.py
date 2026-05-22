from __future__ import annotations

import json

import httpx
import pytest

from frontend.app.core.api_client import ApiClient, ApiError


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


def test_download_service_order_quote_returns_bytes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/service-orders/service-order-id/quote.pdf"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, content=b"%PDF-1.4")

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.download_service_order_quote("token", "service-order-id")

    assert response.startswith(b"%PDF")


def test_download_document_returns_bytes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/documents/document-id/download"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, content=b"%PDF-1.7")

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.download_document("token", "document-id")

    assert response.startswith(b"%PDF")


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


def test_list_documents_sends_inventory_item_filter() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/documents"
        assert request.url.params["inventory_item_id"] == "inventory-item-id"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"file_name": "datasheet.pdf"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_documents("token", inventory_item_id="inventory-item-id")

    assert response == [{"file_name": "datasheet.pdf"}]


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


def test_upload_document_posts_inventory_target(tmp_path) -> None:
    document_path = tmp_path / "datasheet.pdf"
    document_path.write_bytes(b"%PDF-1.4")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/documents"
        assert request.headers["Authorization"] == "Bearer token"
        body = request.content
        assert b"inventory-item-id" in body
        assert b"pdf" in body
        return httpx.Response(201, json={"id": "document-id", "file_name": "datasheet.pdf"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.upload_document(
        access_token="token",
        file_path=str(document_path),
        document_type="pdf",
        inventory_item_id="inventory-item-id",
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
