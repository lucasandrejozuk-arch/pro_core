from __future__ import annotations

from fastapi.testclient import TestClient


def _create_customer(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={"name": "Cliente Documento"},
    )
    assert response.status_code == 201
    return response.json()


def _create_equipment(
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
        },
    )
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
            "problem_description": "Equipamento nao liga.",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_upload_list_download_and_embed_service_order_document(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer = _create_customer(client, auth_headers)
    equipment = _create_equipment(client, auth_headers, customer["id"])
    service_order = _create_service_order(client, auth_headers, customer["id"], equipment["id"])

    upload_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={
            "service_order_id": service_order["id"],
            "document_type": "other",
        },
        files={"file": ("diagnostico.txt", b"conteudo do diagnostico", "text/plain")},
    )
    assert upload_response.status_code == 201
    document = upload_response.json()
    assert document["file_name"] == "diagnostico.txt"
    assert document["service_order_id"] == service_order["id"]
    assert document["file_size_bytes"] == len(b"conteudo do diagnostico")

    list_response = client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"service_order_id": service_order["id"]},
    )
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == document["id"]

    download_response = client.get(
        f"/api/v1/documents/{document['id']}/download",
        headers=auth_headers,
    )
    assert download_response.status_code == 200
    assert download_response.content == b"conteudo do diagnostico"

    service_orders_response = client.get("/api/v1/service-orders", headers=auth_headers)
    assert service_orders_response.status_code == 200
    service_orders = service_orders_response.json()
    assert service_orders[0]["documents"][0]["id"] == document["id"]


def test_upload_document_requires_target(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={"document_type": "other"},
        files={"file": ("sem_destino.txt", b"conteudo", "text/plain")},
    )

    assert response.status_code == 400
