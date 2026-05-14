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
    password: str,
    sector: Sector | None = None,
) -> User:
    user = User(
        company_id=company.id,
        sector_id=sector.id if sector else None,
        full_name=email.split("@", maxsplit=1)[0],
        email=email,
        password_hash=hash_password(password),
        role=role,
        must_change_password=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_public_password_reset_request_uses_generic_response(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/password-reset-requests",
        json={"email": "nao.existe@example.com"},
    )

    assert response.status_code == 200
    assert "solicitacao foi enviada" in response.json()["message"]


def test_manager_password_reset_request_is_sent_to_admin_and_resolved(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    company: Company,
) -> None:
    sector = _create_sector(db_session, company, "Laboratorio")
    manager = _create_user(
        db_session,
        company,
        UserRole.MANAGER,
        "gestor.reset@example.com",
        "Manager123",
        sector,
    )

    request_response = client.post(
        "/api/v1/auth/password-reset-requests",
        json={"email": manager.email},
    )
    list_response = client.get("/api/v1/password-reset-requests", headers=auth_headers)

    assert request_response.status_code == 200
    assert list_response.status_code == 200
    requests = list_response.json()
    assert len(requests) == 1
    assert requests[0]["requester_email"] == manager.email
    assert requests[0]["recipient_role"] == "admin"

    resolve_response = client.post(
        f"/api/v1/password-reset-requests/{requests[0]['id']}/resolve",
        headers=auth_headers,
        json={"new_password": "NovaSenha123"},
    )
    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "resolved"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": manager.email, "password": "NovaSenha123"},
    )
    assert login_response.status_code == 200


def test_operator_password_reset_request_is_sent_to_sector_manager(
    client: TestClient,
    db_session: Session,
    company: Company,
) -> None:
    sector = _create_sector(db_session, company, "Bancada")
    manager = _create_user(
        db_session,
        company,
        UserRole.MANAGER,
        "gestor.bancada@example.com",
        "Manager123",
        sector,
    )
    technician = _create_user(
        db_session,
        company,
        UserRole.TECHNICIAN,
        "tecnico.reset@example.com",
        "Tech123",
        sector,
    )
    manager_headers = _auth_headers(client, manager.email, "Manager123")

    request_response = client.post(
        "/api/v1/auth/password-reset-requests",
        json={"email": technician.email},
    )
    list_response = client.get("/api/v1/password-reset-requests", headers=manager_headers)

    assert request_response.status_code == 200
    assert list_response.status_code == 200
    requests = list_response.json()
    assert len(requests) == 1
    assert requests[0]["requester_email"] == technician.email
    assert requests[0]["recipient_role"] == "manager"
    assert requests[0]["recipient_sector_id"] == str(sector.id)

    resolve_response = client.post(
        f"/api/v1/password-reset-requests/{requests[0]['id']}/resolve",
        headers=manager_headers,
        json={"new_password": "TecnicoNova123"},
    )
    assert resolve_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": technician.email, "password": "TecnicoNova123"},
    )
    assert login_response.status_code == 200
