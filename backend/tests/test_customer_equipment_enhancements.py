from __future__ import annotations

from fastapi.testclient import TestClient


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
