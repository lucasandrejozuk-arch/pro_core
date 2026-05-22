from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.models.document import DocumentAttachment


def _create_customer(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente Documento",
            "email": "cliente.documento@example.com",
            "phone": "(11) 99999-9999",
        },
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


def _create_inventory_item(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/inventory",
        headers=auth_headers,
        json={
            "sku": "INV-DOC-001",
            "name": "Transformador 24V",
            "stock_group": "components",
            "category": "Transformadores",
            "quantity": "5",
            "minimum_quantity": "1",
            "unit_cost": "99.90",
            "technical_data": {
                "primary_voltage": "220V",
                "secondary_voltage": "24V",
                "power": "150VA",
            },
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


def test_upload_and_list_document_for_inventory_item(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    item = _create_inventory_item(client, auth_headers)

    upload_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={
            "inventory_item_id": item["id"],
            "document_type": "pdf",
        },
        files={"file": ("datasheet.pdf", b"pdf-content", "application/pdf")},
    )
    assert upload_response.status_code == 201
    document = upload_response.json()
    assert document["inventory_item_id"] == item["id"]

    list_response = client.get(
        "/api/v1/documents",
        headers=auth_headers,
        params={"inventory_item_id": item["id"]},
    )
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 1
    assert listed[0]["id"] == document["id"]


def test_upload_document_rejects_disallowed_file_type(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer = _create_customer(client, auth_headers)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={"customer_id": customer["id"], "document_type": "other"},
        files={"file": ("script.exe", b"conteudo", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_upload_document_rejects_files_above_configured_limit(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    customer = _create_customer(client, auth_headers)
    monkeypatch.setattr(
        "backend.app.services.documents.get_settings",
        lambda: Settings(pro_core_max_upload_bytes=1024),
    )

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={"customer_id": customer["id"], "document_type": "other"},
        files={"file": ("grande.txt", b"x" * 2048, "text/plain")},
    )

    assert response.status_code == 400
    assert "maximum size" in response.json()["detail"]


def test_download_document_rejects_storage_path_escape(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    customer = _create_customer(client, auth_headers)
    upload_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        data={"customer_id": customer["id"], "document_type": "other"},
        files={"file": ("diagnostico.txt", b"conteudo", "text/plain")},
    )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]
    document = db_session.get(DocumentAttachment, uuid.UUID(document_id))
    assert document is not None
    document.storage_path = "../outside.txt"
    db_session.add(document)
    db_session.commit()

    response = client.get(f"/api/v1/documents/{document_id}/download", headers=auth_headers)

    assert response.status_code == 404
