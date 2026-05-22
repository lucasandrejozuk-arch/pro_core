from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.core.config import Settings


def test_customer_requires_email_and_formatted_phone(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    missing_phone_response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={"name": "Cliente Sem Telefone", "email": "cliente@example.com"},
    )
    invalid_phone_response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente Telefone Invalido",
            "email": "cliente2@example.com",
            "phone": "11999999999",
        },
    )

    assert missing_phone_response.status_code == 422
    assert invalid_phone_response.status_code == 422


def test_equipment_supports_special_number_boards_and_components(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer_response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente Equipamento",
            "email": "cliente.equipamento@example.com",
            "phone": "(11) 99999-9999",
        },
    )
    assert customer_response.status_code == 201

    equipment_response = client.post(
        "/api/v1/equipment",
        headers=auth_headers,
        json={
            "customer_id": customer_response.json()["id"],
            "category": "Inversor",
            "brand": "Siemens",
            "model": "S120",
            "special_number": "A5E-0001",
            "serial_number": "SN-001",
            "description": "Equipamento completo",
        },
    )
    assert equipment_response.status_code == 201
    equipment = equipment_response.json()
    assert equipment["special_number"] == "A5E-0001"

    board_response = client.post(
        f"/api/v1/equipment/{equipment['id']}/boards",
        headers=auth_headers,
        json={
            "name": "Control Unit",
            "special_number": "CU-001",
            "serial_number": "B-001",
            "model": "CU320",
            "revision": "A",
            "notes": "Placa principal",
        },
    )
    assert board_response.status_code == 201
    board = board_response.json()

    component_response = client.post(
        f"/api/v1/equipment/{equipment['id']}/boards/{board['id']}/components",
        headers=auth_headers,
        json={
            "category": "Capacitor",
            "name": "C100",
            "quantity": "2",
            "part_number": "10uF/50V",
            "location": "Fonte",
            "notes": "Componente critico",
        },
    )
    assert component_response.status_code == 201

    get_response = client.get(f"/api/v1/equipment/{equipment['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    loaded_equipment = get_response.json()
    assert loaded_equipment["boards"][0]["name"] == "Control Unit"
    assert loaded_equipment["boards"][0]["components"][0]["name"] == "C100"


def test_equipment_import_rejects_csv_above_configured_limit(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "backend.app.api.v1.routes.equipment.get_settings",
        lambda: Settings(pro_core_max_upload_bytes=1024),
    )

    response = client.post(
        "/api/v1/equipment/import",
        headers=auth_headers,
        files={"file": ("catalog.csv", b"x" * 2048, "text/csv")},
    )

    assert response.status_code == 409
    assert "maximum size" in response.json()["detail"]


def test_equipment_hierarchy_crud_without_customer(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    equipment_response = client.post(
        "/api/v1/equipment",
        headers=auth_headers,
        json={
            "category": "Fonte",
            "brand": "Siemens",
            "model": "S120",
            "special_number": "A5E-0002",
            "unit_price": "1499.90",
            "description": "Cadastro independente de cliente",
        },
    )
    assert equipment_response.status_code == 201
    equipment = equipment_response.json()
    assert equipment["customer_id"] is None
    assert equipment["unit_price"] == "1499.90"

    update_response = client.patch(
        f"/api/v1/equipment/{equipment['id']}",
        headers=auth_headers,
        json={"brand": "Sinamics", "unit_price": "1599.90"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["brand"] == "Sinamics"
    assert update_response.json()["unit_price"] == "1599.90"

    board_response = client.post(
        f"/api/v1/equipment/{equipment['id']}/boards",
        headers=auth_headers,
        json={
            "name": "Control Unit",
            "special_number": "CU-320",
            "model": "CU320",
            "revision": "B",
            "unit_price": "980.00",
        },
    )
    assert board_response.status_code == 201
    board = board_response.json()
    assert board["unit_price"] == "980.00"

    board_update_response = client.patch(
        f"/api/v1/equipment/{equipment['id']}/boards/{board['id']}",
        headers=auth_headers,
        json={"revision": "C", "unit_price": "990.00"},
    )
    assert board_update_response.status_code == 200
    assert board_update_response.json()["revision"] == "C"

    component_response = client.post(
        f"/api/v1/equipment/{equipment['id']}/boards/{board['id']}/components",
        headers=auth_headers,
        json={
            "category": "CI",
            "name": "Driver IR",
            "part_number": "IR2110",
            "location": "U12",
            "unit_price": "12.50",
        },
    )
    assert component_response.status_code == 201
    component = component_response.json()
    assert component["unit_price"] == "12.50"

    component_update_response = client.patch(
        f"/api/v1/equipment/{equipment['id']}/boards/{board['id']}/components/{component['id']}",
        headers=auth_headers,
        json={"location": "U13", "unit_price": "13.50"},
    )
    assert component_update_response.status_code == 200
    assert component_update_response.json()["location"] == "U13"

    component_delete_response = client.delete(
        f"/api/v1/equipment/{equipment['id']}/boards/{board['id']}/components/{component['id']}",
        headers=auth_headers,
    )
    assert component_delete_response.status_code == 204

    board_delete_response = client.delete(
        f"/api/v1/equipment/{equipment['id']}/boards/{board['id']}",
        headers=auth_headers,
    )
    assert board_delete_response.status_code == 204

    equipment_delete_response = client.delete(
        f"/api/v1/equipment/{equipment['id']}",
        headers=auth_headers,
    )
    assert equipment_delete_response.status_code == 204


def test_service_order_accepts_independent_equipment_and_blocks_delete(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer_response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente OS",
            "email": "cliente.os@example.com",
            "phone": "(11) 97777-7777",
        },
    )
    assert customer_response.status_code == 201
    customer = customer_response.json()

    equipment_response = client.post(
        "/api/v1/equipment",
        headers=auth_headers,
        json={"category": "Inversor", "brand": "WEG", "model": "CFW"},
    )
    assert equipment_response.status_code == 201
    equipment = equipment_response.json()

    service_order_response = client.post(
        "/api/v1/service-orders",
        headers=auth_headers,
        json={
            "customer_id": customer["id"],
            "equipment_id": equipment["id"],
            "problem_description": "Falha intermitente.",
        },
    )
    assert service_order_response.status_code == 201

    delete_response = client.delete(
        f"/api/v1/equipment/{equipment['id']}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 409
