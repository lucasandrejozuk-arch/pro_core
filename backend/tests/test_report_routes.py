from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.models.user import User


def _create_customer(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=auth_headers,
        json={
            "name": "Cliente Relatorio",
            "email": "cliente.relatorio@example.com",
            "phone": "11999999999",
        },
    )
    assert response.status_code == 201
    return response.json()


def _auth_headers(client: TestClient, user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "OldPassword123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_can_view_report(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _create_customer(client, auth_headers)

    response = client.get("/api/v1/reports/customers", headers=auth_headers)

    assert response.status_code == 200
    report = response.json()
    assert report["module"] == "customers"
    assert report["total_records"] == 1
    assert report["rows"][0]["name"] == "Cliente Relatorio"


def test_admin_can_export_report_formats(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    _create_customer(client, auth_headers)

    csv_response = client.get(
        "/api/v1/reports/customers/export",
        headers=auth_headers,
        params={"format": "csv"},
    )
    assert csv_response.status_code == 200
    assert "Cliente Relatorio" in csv_response.content.decode("utf-8-sig")

    xlsx_response = client.get(
        "/api/v1/reports/customers/export",
        headers=auth_headers,
        params={"format": "xlsx"},
    )
    assert xlsx_response.status_code == 200
    assert xlsx_response.content.startswith(b"PK")

    pdf_response = client.get(
        "/api/v1/reports/customers/export",
        headers=auth_headers,
        params={"format": "pdf"},
    )
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF")


def test_technician_cannot_access_reports(
    client: TestClient,
    technician_user: User,
) -> None:
    technician_headers = _auth_headers(client, technician_user)

    response = client.get("/api/v1/reports/customers", headers=technician_headers)

    assert response.status_code == 403
