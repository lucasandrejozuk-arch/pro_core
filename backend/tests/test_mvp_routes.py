from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.models.user import User


def create_customer(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente Teste",
            "email": "cliente@example.com",
            "phone": "(11) 99999-9999",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_equipment(
    client: TestClient,
    auth_headers: dict[str, str],
    customer_id: str,
) -> dict:
    response = client.post(
        "/api/v1/equipment",
        headers=auth_headers,
        json={
            "customer_id": customer_id,
            "category": "Notebook",
            "brand": "Dell",
            "model": "Latitude",
            "serial_number": "ABC123",
            "description": "Nao liga",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_customer_inventory_and_equipment_crud(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    customer = create_customer(client, auth_headers)

    inventory_response = client.post(
        "/api/v1/inventory",
        headers=auth_headers,
        json={
            "sku": "SSD-001",
            "name": "SSD 480GB",
            "category": "Armazenamento",
            "quantity": "10",
            "minimum_quantity": "2",
            "unit_cost": "180.50",
        },
    )
    assert inventory_response.status_code == 201
    assert inventory_response.json()["name"] == "SSD 480GB"

    equipment = create_equipment(client, auth_headers, customer["id"])
    assert equipment["customer_id"] == customer["id"]

    update_response = client.patch(
        f"/api/v1/customers/{customer['id']}",
        headers=auth_headers,
        json={"phone": "(11) 98888-8888"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["phone"] == "(11) 98888-8888"


def test_inventory_transformer_requires_key_technical_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/inventory",
        headers=auth_headers,
        json={
            "sku": "TRF-001",
            "name": "Transformador sem dados",
            "stock_group": "components",
            "category": "Transformadores",
            "quantity": "1",
            "minimum_quantity": "1",
            "unit_cost": "10",
            "technical_data": {"primary_voltage": "220V"},
        },
    )

    assert response.status_code == 422


def test_inventory_update_transformer_requires_key_technical_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/inventory",
        headers=auth_headers,
        json={
            "sku": "TRF-002",
            "name": "Transformador valido",
            "stock_group": "components",
            "category": "Transformadores",
            "quantity": "2",
            "minimum_quantity": "1",
            "unit_cost": "20",
            "technical_data": {
                "primary_voltage": "220V",
                "secondary_voltage": "24V",
                "power": "100VA",
            },
        },
    )
    assert create_response.status_code == 201
    item = create_response.json()

    update_response = client.patch(
        f"/api/v1/inventory/{item['id']}",
        headers=auth_headers,
        json={
            "technical_data": {
                "primary_voltage": "220V",
                "secondary_voltage": "24V",
            }
        },
    )

    assert update_response.status_code == 400


def test_list_technicians_returns_company_technicians(
    client: TestClient,
    auth_headers: dict[str, str],
    technician_user: User,
) -> None:
    response = client.get("/api/v1/users/technicians", headers=auth_headers)

    assert response.status_code == 200
    technicians = response.json()
    assert len(technicians) == 1
    assert technicians[0]["id"] == str(technician_user.id)
    assert technicians[0]["role"] == "technician"


def test_service_order_main_flow(
    client: TestClient,
    auth_headers: dict[str, str],
    technician_user: User,
) -> None:
    customer = create_customer(client, auth_headers)
    equipment = create_equipment(client, auth_headers, customer["id"])

    create_response = client.post(
        "/api/v1/service-orders",
        headers=auth_headers,
        json={
            "customer_id": customer["id"],
            "equipment_id": equipment["id"],
            "assigned_technician_id": str(technician_user.id),
            "problem_description": "Equipamento nao inicializa.",
        },
    )
    assert create_response.status_code == 201
    service_order = create_response.json()
    assert service_order["status"] == "assigned"

    diagnosis_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/diagnosis",
        headers=auth_headers,
        json={"technical_diagnosis": "SSD com falha."},
    )
    assert diagnosis_response.status_code == 200
    assert diagnosis_response.json()["status"] == "pending_quote"

    budget_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/budget-items",
        headers=auth_headers,
        json={
            "item_type": "service",
            "description": "Substituicao de SSD e reinstalacao",
            "quantity": "1",
            "unit_price": "250.00",
        },
    )
    assert budget_response.status_code == 201

    submit_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/submit-quote",
        headers=auth_headers,
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == "pending_approval"

    approve_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/approve",
        headers=auth_headers,
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    start_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/start",
        headers=auth_headers,
    )
    assert start_response.status_code == 200
    assert start_response.json()["status"] == "in_progress"

    complete_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/complete",
        headers=auth_headers,
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"
    assert complete_response.json()["closed_at"] is not None
