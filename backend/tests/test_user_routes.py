from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.company import Company
from backend.app.models.enums import UserRole
from backend.app.models.user import User


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_manager(db_session: Session, company: Company) -> User:
    manager = User(
        company_id=company.id,
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
            "password": "Temp123",
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
            "password": "Temp123",
        },
    )

    assert response.status_code == 403
