from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.company import Company
from backend.app.models.enums import UserRole
from backend.app.models.sector import Sector
from backend.app.models.user import User


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_manager(db_session: Session, company: Company, sector: Sector) -> User:
    manager = User(
        company_id=company.id,
        sector_id=sector.id,
        full_name="Manager Test",
        email="manager.sector@example.com",
        password_hash=hash_password("Manager123"),
        role=UserRole.MANAGER,
        must_change_password=True,
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


def test_admin_can_create_update_and_list_sectors(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/sectors",
        headers=auth_headers,
        json={"name": "Laboratorio", "description": "Bancada tecnica"},
    )

    assert create_response.status_code == 201
    sector = create_response.json()
    assert sector["name"] == "Laboratorio"

    update_response = client.patch(
        f"/api/v1/sectors/{sector['id']}",
        headers=auth_headers,
        json={"description": "Atendimento tecnico interno"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Atendimento tecnico interno"

    list_response = client.get("/api/v1/sectors", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(item["id"] == sector["id"] for item in list_response.json())


def test_admin_cannot_create_duplicate_sector_name(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {"name": "Suporte"}
    first_response = client.post("/api/v1/sectors", headers=auth_headers, json=payload)
    second_response = client.post("/api/v1/sectors", headers=auth_headers, json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_manager_only_lists_own_sector_and_cannot_write_sectors(
    client: TestClient,
    db_session: Session,
    company: Company,
) -> None:
    own_sector = Sector(company_id=company.id, name="Laboratorio")
    other_sector = Sector(company_id=company.id, name="Campo")
    db_session.add_all([own_sector, other_sector])
    db_session.commit()
    db_session.refresh(own_sector)
    db_session.refresh(other_sector)
    manager = _create_manager(db_session, company, own_sector)
    manager_headers = _auth_headers(client, manager.email, "Manager123")

    list_response = client.get("/api/v1/sectors", headers=manager_headers)
    create_response = client.post(
        "/api/v1/sectors",
        headers=manager_headers,
        json={"name": "Nao permitido"},
    )

    assert list_response.status_code == 200
    assert [sector["id"] for sector in list_response.json()] == [str(own_sector.id)]
    assert create_response.status_code == 403
