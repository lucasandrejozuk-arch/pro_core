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


def _create_user(
    db_session: Session,
    company: Company,
    role: UserRole,
    email: str,
    sector: Sector | None = None,
) -> User:
    user = User(
        company_id=company.id,
        sector_id=sector.id if sector else None,
        full_name=email.split("@", maxsplit=1)[0],
        email=email,
        password_hash=hash_password("Password123"),
        role=role,
        must_change_password=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_customer(client: TestClient, headers: dict[str, str], name: str) -> dict:
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": name,
            "email": f"{name.lower()}@example.com",
            "phone": "(11) 99999-9999",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_equipment(client: TestClient, headers: dict[str, str], customer_id: str) -> dict:
    response = client.post(
        "/api/v1/equipment",
        headers=headers,
        json={
            "customer_id": customer_id,
            "category": "Notebook",
            "description": "Teste de escopo",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_service_order(
    client: TestClient,
    headers: dict[str, str],
    technician_id: str,
    suffix: str,
) -> dict:
    customer = _create_customer(client, headers, f"Cliente{suffix}")
    equipment = _create_equipment(client, headers, customer["id"])
    response = client.post(
        "/api/v1/service-orders",
        headers=headers,
        json={
            "customer_id": customer["id"],
            "equipment_id": equipment["id"],
            "assigned_technician_id": technician_id,
            "problem_description": "Equipamento nao liga.",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_technician_only_accesses_own_service_orders(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    company: Company,
) -> None:
    sector = _create_sector(db_session, company, "Laboratorio")
    technician = _create_user(
        db_session,
        company,
        UserRole.TECHNICIAN,
        "tecnico.escopo@example.com",
        sector,
    )
    other_technician = _create_user(
        db_session,
        company,
        UserRole.TECHNICIAN,
        "tecnico.outro@example.com",
        sector,
    )
    own_order = _create_service_order(client, auth_headers, str(technician.id), "A")
    other_order = _create_service_order(client, auth_headers, str(other_technician.id), "B")
    technician_headers = _auth_headers(client, technician.email, "Password123")

    list_response = client.get("/api/v1/service-orders", headers=technician_headers)
    get_response = client.get(
        f"/api/v1/service-orders/{other_order['id']}",
        headers=technician_headers,
    )

    assert list_response.status_code == 200
    assert [order["id"] for order in list_response.json()] == [own_order["id"]]
    assert get_response.status_code == 403


def test_manager_only_accesses_service_orders_from_own_sector(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    company: Company,
) -> None:
    own_sector = _create_sector(db_session, company, "Suporte")
    other_sector = _create_sector(db_session, company, "Campo")
    manager = _create_user(
        db_session,
        company,
        UserRole.MANAGER,
        "gestor.suporte@example.com",
        own_sector,
    )
    own_technician = _create_user(
        db_session,
        company,
        UserRole.TECHNICIAN,
        "tecnico.suporte@example.com",
        own_sector,
    )
    other_technician = _create_user(
        db_session,
        company,
        UserRole.TECHNICIAN,
        "tecnico.campo@example.com",
        other_sector,
    )
    own_order = _create_service_order(client, auth_headers, str(own_technician.id), "C")
    other_order = _create_service_order(client, auth_headers, str(other_technician.id), "D")
    manager_headers = _auth_headers(client, manager.email, "Password123")

    list_response = client.get("/api/v1/service-orders", headers=manager_headers)
    get_response = client.get(
        f"/api/v1/service-orders/{other_order['id']}",
        headers=manager_headers,
    )
    create_outside_scope_response = client.post(
        "/api/v1/service-orders",
        headers=manager_headers,
        json={
            "customer_id": other_order["customer_id"],
            "equipment_id": other_order["equipment_id"],
            "assigned_technician_id": str(other_technician.id),
            "problem_description": "Tentativa fora do setor.",
        },
    )

    assert list_response.status_code == 200
    assert [order["id"] for order in list_response.json()] == [own_order["id"]]
    assert get_response.status_code == 403
    assert create_outside_scope_response.status_code == 403
