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


def _create_sector(db_session: Session, company: Company, name: str) -> Sector:
    sector = Sector(company_id=company.id, name=name)
    db_session.add(sector)
    db_session.commit()
    db_session.refresh(sector)
    return sector


def _create_manager(db_session: Session, company: Company, sector: Sector | None = None) -> User:
    manager = User(
        company_id=company.id,
        sector_id=sector.id if sector else None,
        full_name="Manager Test",
        email="manager@example.com",
        password_hash=hash_password("Manager123"),
        role=UserRole.MANAGER,
        must_change_password=True,
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


def _create_technician(
    db_session: Session,
    company: Company,
    email: str,
    sector: Sector | None = None,
) -> User:
    technician = User(
        company_id=company.id,
        sector_id=sector.id if sector else None,
        full_name=email.split("@", maxsplit=1)[0],
        email=email,
        password_hash=hash_password("Tech123"),
        role=UserRole.TECHNICIAN,
        must_change_password=True,
    )
    db_session.add(technician)
    db_session.commit()
    db_session.refresh(technician)
    return technician


def test_admin_can_create_update_list_and_reset_user_password(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "full_name": "Tecnico Novo",
            "email": "tecnico.novo@example.com",
            "role": "technician",
            "password": "Temp1234",
        },
    )
    assert create_response.status_code == 201
    created_user = create_response.json()
    assert created_user["role"] == "technician"
    assert created_user["must_change_password"] is True

    list_response = client.get("/api/v1/users", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(user["id"] == created_user["id"] for user in list_response.json())

    technicians_response = client.get("/api/v1/users/technicians", headers=auth_headers)
    assert technicians_response.status_code == 200
    assert any(user["id"] == created_user["id"] for user in technicians_response.json())

    update_response = client.patch(
        f"/api/v1/users/{created_user['id']}",
        headers=auth_headers,
        json={"full_name": "Tecnico Atualizado", "is_active": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Tecnico Atualizado"

    reset_response = client.post(
        f"/api/v1/users/{created_user['id']}/reset-password",
        headers=auth_headers,
        json={"new_password": "NovaSenha123"},
    )
    assert reset_response.status_code == 200
    assert reset_response.json()["must_change_password"] is True

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "tecnico.novo@example.com", "password": "NovaSenha123"},
    )
    assert login_response.status_code == 200


def test_manager_cannot_create_admin_user(
    client: TestClient,
    db_session: Session,
    company: Company,
) -> None:
    manager = _create_manager(db_session, company)
    manager_headers = _auth_headers(client, manager.email, "Manager123")

    response = client.post(
        "/api/v1/users",
        headers=manager_headers,
        json={
            "full_name": "Admin Indevido",
            "email": "admin.indevido@example.com",
            "role": "admin",
            "password": "Temp1234",
        },
    )

    assert response.status_code == 403


def test_admin_can_assign_user_to_company_sector(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    company: Company,
) -> None:
    sector = _create_sector(db_session, company, "Bancada")

    response = client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "full_name": "Tecnico Setorizado",
            "email": "tecnico.setor@example.com",
            "role": "technician",
            "sector_id": str(sector.id),
            "password": "Temp1234",
        },
    )

    assert response.status_code == 201
    assert response.json()["sector_id"] == str(sector.id)


def test_admin_created_without_sector_uses_administrativo_sector(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "full_name": "Admin Setor Padrao",
            "email": "admin.setor@example.com",
            "role": "admin",
            "password": "AdminTemp123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "admin"
    assert body["sector_id"] is not None
    assert body["sector_name"] == "Administrativo"


def test_manager_creates_and_lists_only_technicians_from_own_sector(
    client: TestClient,
    db_session: Session,
    company: Company,
) -> None:
    own_sector = _create_sector(db_session, company, "Laboratorio")
    other_sector = _create_sector(db_session, company, "Campo")
    manager = _create_manager(db_session, company, own_sector)
    outside_technician = _create_technician(
        db_session,
        company,
        "tecnico.campo@example.com",
        other_sector,
    )
    manager_headers = _auth_headers(client, manager.email, "Manager123")

    create_response = client.post(
        "/api/v1/users",
        headers=manager_headers,
        json={
            "full_name": "Tecnico Local",
            "email": "tecnico.local@example.com",
            "role": "technician",
            "sector_id": str(other_sector.id),
            "password": "Temp1234",
        },
    )

    assert create_response.status_code == 201
    created_user = create_response.json()
    assert created_user["sector_id"] == str(own_sector.id)

    list_response = client.get("/api/v1/users", headers=manager_headers)
    assert list_response.status_code == 200
    listed_ids = {user["id"] for user in list_response.json()}
    assert created_user["id"] in listed_ids
    assert str(outside_technician.id) not in listed_ids


def test_manager_cannot_update_user_outside_own_sector(
    client: TestClient,
    db_session: Session,
    company: Company,
) -> None:
    own_sector = _create_sector(db_session, company, "Suporte")
    other_sector = _create_sector(db_session, company, "Campo")
    manager = _create_manager(db_session, company, own_sector)
    outside_technician = _create_technician(
        db_session,
        company,
        "tecnico.fora@example.com",
        other_sector,
    )
    manager_headers = _auth_headers(client, manager.email, "Manager123")

    response = client.patch(
        f"/api/v1/users/{outside_technician.id}",
        headers=manager_headers,
        json={"full_name": "Tecnico Invadido"},
    )

    assert response.status_code == 403


def test_admin_can_list_and_update_resource_access(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "full_name": "Tecnico Acesso",
            "email": "tecnico.acesso@example.com",
            "role": "technician",
            "password": "Temp1234",
        },
    )
    assert create_response.status_code == 201
    created_user_id = create_response.json()["id"]

    list_response = client.get("/api/v1/users/resource-access", headers=auth_headers)
    assert list_response.status_code == 200
    target = next(record for record in list_response.json() if record["user_id"] == created_user_id)
    assert "service_orders" in target["default_resources"]

    update_response = client.put(
        f"/api/v1/users/{created_user_id}/resource-access",
        headers=auth_headers,
        json={"allowed_resources": ["dashboard", "service_orders", "tools"]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["allowed_resources"] == [
        "dashboard",
        "service_orders",
        "tools",
    ]


def test_manager_resource_access_scope_is_limited_to_sector_technicians(
    client: TestClient,
    db_session: Session,
    company: Company,
) -> None:
    own_sector = _create_sector(db_session, company, "Laboratorio")
    other_sector = _create_sector(db_session, company, "Campo")
    manager = _create_manager(db_session, company, own_sector)
    local_tech = _create_technician(db_session, company, "local.tech@example.com", own_sector)
    outside_tech = _create_technician(db_session, company, "outside.tech@example.com", other_sector)
    manager_headers = _auth_headers(client, manager.email, "Manager123")

    list_response = client.get("/api/v1/users/resource-access", headers=manager_headers)
    assert list_response.status_code == 200
    listed_ids = {record["user_id"] for record in list_response.json()}
    assert str(local_tech.id) in listed_ids
    assert str(outside_tech.id) not in listed_ids

    update_response = client.put(
        f"/api/v1/users/{outside_tech.id}/resource-access",
        headers=manager_headers,
        json={"allowed_resources": ["dashboard"]},
    )
    assert update_response.status_code == 403
