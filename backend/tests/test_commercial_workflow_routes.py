from __future__ import annotations

from fastapi.testclient import TestClient

from backend.tests.test_mvp_routes import create_customer, create_equipment


def _create_order_waiting_approval(
    client: TestClient,
    auth_headers: dict[str, str],
    technician_id: str,
) -> dict:
    customer = create_customer(client, auth_headers)
    equipment = create_equipment(client, auth_headers, customer["id"])
    create_response = client.post(
        "/api/v1/service-orders",
        headers=auth_headers,
        json={
            "customer_id": customer["id"],
            "equipment_id": equipment["id"],
            "assigned_technician_id": technician_id,
            "priority": "high",
            "problem_description": "Nao inicializa.",
        },
    )
    assert create_response.status_code == 201
    service_order = create_response.json()

    diagnosis_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/diagnosis",
        headers=auth_headers,
        json={"technical_diagnosis": "Fonte danificada."},
    )
    assert diagnosis_response.status_code == 200

    budget_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/budget-items",
        headers=auth_headers,
        json={
            "item_type": "service",
            "description": "Substituicao da fonte",
            "quantity": "1",
            "unit_price": "300.00",
        },
    )
    assert budget_response.status_code == 201

    submit_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/submit-quote",
        headers=auth_headers,
    )
    assert submit_response.status_code == 200
    return submit_response.json()


def test_service_order_tracks_timeline_and_audit_log(
    client: TestClient,
    auth_headers: dict[str, str],
    technician_user,
) -> None:
    service_order = _create_order_waiting_approval(client, auth_headers, str(technician_user.id))

    assert service_order["priority"] == "high"
    assert service_order["quote_sent_at"] is not None
    assert [event["event_type"] for event in service_order["events"]] == [
        "created",
        "diagnosis_registered",
        "budget_item_added",
        "quote_sent",
    ]

    approve_response = client.post(
        f"/api/v1/service-orders/{service_order['id']}/approve",
        headers=auth_headers,
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["approval_source"] == "staff"

    audit_response = client.get("/api/v1/audit-logs", headers=auth_headers)
    assert audit_response.status_code == 200
    assert any(log["action"] == "service_order.created" for log in audit_response.json())


def test_customer_portal_login_approve_and_quote_pdf(
    client: TestClient,
    auth_headers: dict[str, str],
    technician_user,
) -> None:
    service_order = _create_order_waiting_approval(client, auth_headers, str(technician_user.id))

    login_response = client.post(
        "/api/v1/customer-portal/login",
        json={"service_order_code": service_order["code"], "email": "cliente@example.com"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    portal_headers = {"Authorization": f"Bearer {token}"}

    pdf_response = client.get("/api/v1/customer-portal/quote.pdf", headers=portal_headers)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"

    approve_response = client.post(
        "/api/v1/customer-portal/approve",
        headers=portal_headers,
        json={"decision_name": "Cliente Teste"},
    )
    assert approve_response.status_code == 200
    body = approve_response.json()
    assert body["status"] == "approved"
    assert body["events"][-1]["source"] == "customer"


def test_customer_portal_rejects_invalid_access(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customer-portal/login",
        json={"service_order_code": "OS-999999", "email": "cliente@example.com"},
    )

    assert response.status_code == 401


def test_customer_portal_login_rate_limits_invalid_access(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/customer-portal/login",
            json={"service_order_code": "OS-999999", "email": "cliente@example.com"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/v1/customer-portal/login",
        json={"service_order_code": "OS-999999", "email": "cliente@example.com"},
    )

    assert response.status_code == 429
