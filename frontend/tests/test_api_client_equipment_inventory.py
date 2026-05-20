from __future__ import annotations

import json

import httpx

from frontend.app.core.api_client import ApiClient


def test_create_equipment_posts_payload() -> None:
    payload = {
        "customer_id": "customer-id",
        "category": "Notebook",
        "brand": "Dell",
        "model": "Latitude",
        "special_number": "A5E123",
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
        "special_number": None,
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


def test_create_equipment_board_posts_payload() -> None:
    payload = {
        "name": "Placa Principal",
        "special_number": "A5E-001",
        "serial_number": "SER-001",
        "model": "CU320",
        "revision": "A",
        "notes": None,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/equipment/equipment-id/boards"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "board-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_equipment_board("token", "equipment-id", payload)

    assert response["id"] == "board-id"


def test_create_equipment_board_component_posts_payload() -> None:
    payload = {
        "category": "Capacitor",
        "name": "C100",
        "quantity": "2",
        "part_number": "10uF",
        "location": "Fonte",
        "notes": None,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/equipment/equipment-id/boards/board-id/components"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "component-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_equipment_board_component(
        "token",
        "equipment-id",
        "board-id",
        payload,
    )

    assert response["id"] == "component-id"


def test_equipment_delete_methods_send_delete_requests() -> None:
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert request.headers["Authorization"] == "Bearer token"
        paths.append(request.url.path)
        return httpx.Response(204)

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    assert client.delete_equipment("token", "equipment-id") is None
    assert client.delete_equipment_board("token", "equipment-id", "board-id") is None
    assert (
        client.delete_equipment_board_component(
            "token",
            "equipment-id",
            "board-id",
            "component-id",
        )
        is None
    )
    assert paths == [
        "/api/v1/equipment/equipment-id",
        "/api/v1/equipment/equipment-id/boards/board-id",
        "/api/v1/equipment/equipment-id/boards/board-id/components/component-id",
    ]


def test_business_delete_methods_send_delete_requests() -> None:
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert request.headers["Authorization"] == "Bearer token"
        paths.append(request.url.path)
        return httpx.Response(204)

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    assert client.delete_customer("token", "customer-id") is None
    assert client.delete_inventory_item("token", "item-id") is None
    assert client.delete_service_order("token", "os-id") is None
    assert client.delete_sector("token", "sector-id") is None
    assert client.delete_user("token", "user-id") is None
    assert client.delete_audit_log("token", "log-id") is None
    assert paths == [
        "/api/v1/customers/customer-id",
        "/api/v1/inventory/item-id",
        "/api/v1/service-orders/os-id",
        "/api/v1/sectors/sector-id",
        "/api/v1/users/user-id",
        "/api/v1/audit-logs/log-id",
    ]


def test_equipment_nested_update_methods_send_patch_requests() -> None:
    payload = {"unit_price": "12.50"}
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        paths.append(request.url.path)
        return httpx.Response(200, json=payload | {"id": "updated-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    client.update_equipment_board("token", "equipment-id", "board-id", payload)
    client.update_equipment_board_component(
        "token",
        "equipment-id",
        "board-id",
        "component-id",
        payload,
    )

    assert paths == [
        "/api/v1/equipment/equipment-id/boards/board-id",
        "/api/v1/equipment/equipment-id/boards/board-id/components/component-id",
    ]


def test_equipment_import_export_and_defect_case_methods(tmp_path) -> None:
    csv_path = tmp_path / "equipment.csv"
    csv_path.write_text("Tipo;Marca\nFonte;Siemens\n", encoding="utf-8")
    expected_paths = [
        ("GET", "/api/v1/equipment/export"),
        ("POST", "/api/v1/equipment/import"),
        ("GET", "/api/v1/equipment/equipment-id/defect-cases"),
        ("POST", "/api/v1/equipment/equipment-id/defect-cases"),
        ("PATCH", "/api/v1/equipment/equipment-id/defect-cases/case-id"),
        ("DELETE", "/api/v1/equipment/equipment-id/defect-cases/case-id"),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        method, path = expected_paths.pop(0)
        assert request.method == method
        assert request.url.path == path
        assert request.headers["Authorization"] == "Bearer token"
        if path.endswith("/export"):
            assert request.url.params["format"] == "csv"
            return httpx.Response(200, content=b"Tipo\nFonte\n")
        if path.endswith("/import"):
            assert request.url.params["replace"] == "false"
            assert b"equipment.csv" in request.content
            return httpx.Response(200, json={"processed_rows": 1})
        if method == "GET":
            assert request.url.params["query"] == "falha"
            return httpx.Response(200, json=[{"id": "case-id"}])
        if method == "POST":
            assert json.loads(request.content)["title"] == "Falha"
            return httpx.Response(201, json={"id": "case-id", "title": "Falha"})
        if method == "PATCH":
            assert json.loads(request.content)["solution"] == "OK"
            return httpx.Response(200, json={"id": "case-id", "solution": "OK"})
        return httpx.Response(204)

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    assert client.export_equipment("token", "csv") == b"Tipo\nFonte\n"
    assert client.import_equipment("token", str(csv_path))["processed_rows"] == 1
    defect_cases = client.list_equipment_defect_cases("token", "equipment-id", "falha")
    created_case = client.create_equipment_defect_case(
        "token",
        "equipment-id",
        {"title": "Falha"},
    )
    updated_case = client.update_equipment_defect_case(
        "token",
        "equipment-id",
        "case-id",
        {"solution": "OK"},
    )
    assert defect_cases[0]["id"] == "case-id"
    assert created_case["id"] == "case-id"
    assert updated_case["solution"] == "OK"
    assert client.delete_equipment_defect_case("token", "equipment-id", "case-id") is None
    assert expected_paths == []


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
