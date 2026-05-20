from fastapi.testclient import TestClient

from backend.app.core.security import hash_password
from backend.app.models.user import User


def test_password_hash_uses_test_cost_for_fast_suite() -> None:
    password_hash = hash_password("OldPassword123")

    assert password_hash.startswith("$2b$04$")


def test_login_returns_token_and_user_data(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email.upper(), "password": "OldPassword123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["must_change_password"] is True
    assert body["user"]["email"] == "admin@example.com"
    assert body["user"]["role"] == "admin"
    assert body["user"]["sector_name"] == "Administrativo"
    assert "service_orders:*" in body["user"]["permissions"]


def test_me_requires_valid_token(client: TestClient, admin_user: User) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "OldPassword123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert "audit_logs:view" in response.json()["permissions"]


def test_change_password_clears_required_password_change_flag(
    client: TestClient,
    admin_user: User,
) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "OldPassword123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
        },
    )

    assert response.status_code == 200
    assert response.json()["must_change_password"] is False

    second_login_response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "NewPassword123"},
    )

    assert second_login_response.status_code == 200
    assert second_login_response.json()["must_change_password"] is False


def test_login_rejects_invalid_password(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrong"},
    )

    assert response.status_code == 401


def test_login_rate_limits_repeated_invalid_passwords(
    client: TestClient,
    admin_user: User,
) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "wrong"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "wrong"},
    )

    assert response.status_code == 429
