from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.models.sector import Sector
from backend.app.models.user import User
from backend.tests.conftest import create_user


def _auth_headers(client: TestClient, user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "OldPassword123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_equipment_defect_cases_crud_and_catalog_export(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    equipment_response = client.post(
        "/api/v1/equipment",
        headers=auth_headers,
        json={"category": "Fonte", "brand": "Siemens", "model": "S120"},
    )
    assert equipment_response.status_code == 201
    equipment = equipment_response.json()

    board_response = client.post(
        f"/api/v1/equipment/{equipment['id']}/boards",
        headers=auth_headers,
        json={"name": "Control Unit", "model": "CU320"},
    )
    assert board_response.status_code == 201
    board = board_response.json()

    create_response = client.post(
        f"/api/v1/equipment/{equipment['id']}/defect-cases",
        headers=auth_headers,
        json={
            "board_id": board["id"],
            "title": "Falha de comunicacao",
            "symptom": "Sem comunicacao no barramento",
            "root_cause": "Conector oxidado",
            "solution": "Limpeza e reaperto",
            "notes": "Recorrente",
        },
    )
    assert create_response.status_code == 201
    defect_case = create_response.json()
    assert defect_case["title"] == "Falha de comunicacao"

    list_response = client.get(
        f"/api/v1/equipment/{equipment['id']}/defect-cases",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert list_response.json()[0]["root_cause"] == "Conector oxidado"

    update_response = client.patch(
        f"/api/v1/equipment/{equipment['id']}/defect-cases/{defect_case['id']}",
        headers=auth_headers,
        json={"solution": "Substituicao do conector"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["solution"] == "Substituicao do conector"

    csv_response = client.get(
        "/api/v1/equipment/export",
        headers=auth_headers,
        params={"format": "csv"},
    )
    assert csv_response.status_code == 200
    assert "Falha de comunicacao" in csv_response.content.decode("utf-8-sig")

    pdf_response = client.get(
        "/api/v1/equipment/export",
        headers=auth_headers,
        params={"format": "pdf"},
    )
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF")

    delete_response = client.delete(
        f"/api/v1/equipment/{equipment['id']}/defect-cases/{defect_case['id']}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204


def test_equipment_csv_import_creates_hierarchy_and_defect_case(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    content = (
        "Tipo;Marca;Modelo;Objeto Nome;Componente Dados;Caso Titulo;Caso Sintoma\n"
        "Inversor;WEG;CFW;Placa Potencia;IGBT;Falha de disparo;Sem pulso\n"
    ).encode("utf-8-sig")

    response = client.post(
        "/api/v1/equipment/import",
        headers=auth_headers,
        files={"file": ("equipamentos.csv", content, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["processed_rows"] == 1
    assert response.json()["created_defect_cases"] == 1

    equipment_response = client.get("/api/v1/equipment", headers=auth_headers)
    assert equipment_response.status_code == 200
    equipment = equipment_response.json()[0]
    assert equipment["boards"][0]["components"][0]["name"] == "IGBT"
    assert equipment["defect_cases"][0]["title"] == "Falha de disparo"


def test_technician_cannot_access_customer_module(
    client: TestClient,
    technician_user: User,
) -> None:
    technician_headers = _auth_headers(client, technician_user)

    response = client.get("/api/v1/customers", headers=technician_headers)

    assert response.status_code == 403


def test_tools_catalog_is_filtered_by_role_and_sector(
    client: TestClient,
    auth_headers: dict[str, str],
    technician_user: User,
    db_session: Session,
    company,
) -> None:
    admin_response = client.get("/api/v1/tools", headers=auth_headers)
    assert admin_response.status_code == 200
    admin_tool_ids = {tool["id"] for tool in admin_response.json()}
    assert {"ohm", "markup", "sla"}.issubset(admin_tool_ids)

    technician_headers = _auth_headers(client, technician_user)
    technician_response = client.get("/api/v1/tools", headers=technician_headers)
    assert technician_response.status_code == 200
    technician_tool_ids = {tool["id"] for tool in technician_response.json()}
    assert "ohm" in technician_tool_ids
    assert "markup" not in technician_tool_ids

    finance_sector = Sector(company_id=company.id, name="Financeiro")
    db_session.add(finance_sector)
    db_session.commit()
    db_session.refresh(finance_sector)
    finance_user = create_user(
        db_session,
        company,
        UserRole.TECHNICIAN,
        "financeiro@example.com",
        "Financeiro",
        finance_sector,
    )
    finance_response = client.get("/api/v1/tools", headers=_auth_headers(client, finance_user))
    assert finance_response.status_code == 200
    finance_tool_ids = {tool["id"] for tool in finance_response.json()}
    assert "markup" in finance_tool_ids
    assert "ohm" not in finance_tool_ids
