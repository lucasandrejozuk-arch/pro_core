from __future__ import annotations

from fastapi.testclient import TestClient


def _create_customer(client: TestClient, auth_headers: dict[str, str], email: str) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente Excluir",
            "email": email,
            "phone": "(11) 98888-7777",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_equipment(
    client: TestClient,
    auth_headers: dict[str, str],
    customer_id: str | None = None,
) -> dict:
    payload = {
        "customer_id": customer_id,
        "category": "Fonte",
        "brand": "Siemens",
        "model": "S120",
    }
    response = client.post("/api/v1/equipment", headers=auth_headers, json=payload)
    assert response.status_code == 201
    return response.json()


def _create_service_order(
    client: TestClient,
    auth_headers: dict[str, str],
    customer_id: str,
    equipment_id: str,
) -> dict:
    response = client.post(
        "/api/v1/service-orders",
        headers=auth_headers,
        json={
            "customer_id": customer_id,
            "equipment_id": equipment_id,
            "problem_description": "Nao liga.",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_delete_customer_without_orders_detaches_equipment(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer = _create_customer(client, auth_headers, "delete.customer@example.com")
    equipment = _create_equipment(client, auth_headers, customer["id"])

    response = client.delete(f"/api/v1/customers/{customer['id']}", headers=auth_headers)

    assert response.status_code == 204
    equipment_response = client.get(f"/api/v1/equipment/{equipment['id']}", headers=auth_headers)
    assert equipment_response.status_code == 200
    assert equipment_response.json()["customer_id"] is None


def test_delete_customer_with_orders_returns_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer = _create_customer(client, auth_headers, "customer.with.os@example.com")
    equipment = _create_equipment(client, auth_headers)
    _create_service_order(client, auth_headers, customer["id"], equipment["id"])

    response = client.delete(f"/api/v1/customers/{customer['id']}", headers=auth_headers)

    assert response.status_code == 409
    assert "ordens de servico" in response.json()["detail"].lower()


def test_delete_inventory_and_service_order_routes(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer = _create_customer(client, auth_headers, "delete.routes@example.com")
    equipment = _create_equipment(client, auth_headers)
    service_order = _create_service_order(client, auth_headers, customer["id"], equipment["id"])

    inventory_response = client.post(
        "/api/v1/inventory",
        headers=auth_headers,
        json={"sku": "DEL-1", "name": "Peca removivel", "quantity": "3"},
    )
    assert inventory_response.status_code == 201
    inventory = inventory_response.json()

    inventory_delete = client.delete(f"/api/v1/inventory/{inventory['id']}", headers=auth_headers)
    service_order_delete = client.delete(
        f"/api/v1/service-orders/{service_order['id']}",
        headers=auth_headers,
    )

    assert inventory_delete.status_code == 204
    assert service_order_delete.status_code == 204


def test_delete_service_order_with_document_returns_no_server_error(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer = _create_customer(client, auth_headers, "delete.order.document@example.com")
    equipment = _create_equipment(client, auth_headers, customer["id"])
    service_order = _create_service_order(client, auth_headers, customer["id"], equipment["id"])

    upload_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={
            "service_order_id": service_order["id"],
            "document_type": "other",
        },
        files={"file": ("diagnostico.txt", b"conteudo", "text/plain")},
    )
    assert upload_response.status_code == 201

    delete_response = client.delete(
        f"/api/v1/service-orders/{service_order['id']}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204


def test_delete_sector_compat_route(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/sectors",
        headers=auth_headers,
        json={"name": "Temporario"},
    )
    assert create_response.status_code == 201
    sector = create_response.json()

    delete_response = client.post(
        f"/api/v1/sectors/{sector['id']}/delete",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204
