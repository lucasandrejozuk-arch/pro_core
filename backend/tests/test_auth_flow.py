from fastapi.testclient import TestClient

from backend.app.models.user import User


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
