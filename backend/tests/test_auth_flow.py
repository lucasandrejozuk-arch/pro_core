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


def test_login_uses_dummy_password_check_for_missing_user(client: TestClient, monkeypatch) -> None:
    calls: list[str] = []

    def fake_verify_password_for_missing_user(password: str) -> None:
        calls.append(password)

    monkeypatch.setattr(
        "backend.app.services.users.verify_password_for_missing_user",
        fake_verify_password_for_missing_user,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "WrongPassword123"},
    )

    assert response.status_code == 401
    assert calls == ["WrongPassword123"]


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


def test_password_reset_request_is_rate_limited(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/password-reset-requests",
            json={"email": "missing@example.com"},
        )
        assert response.status_code == 200

    response = client.post(
        "/api/v1/auth/password-reset-requests",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 429


def test_backend_restart_authorization_requires_admin_password(
    client: TestClient,
    admin_user: User,
) -> None:
    response = client.post(
        "/api/v1/auth/backend-restart/authorize",
        json={
            "operator_email": admin_user.email,
            "admin_email": admin_user.email,
            "admin_password": "wrong",
            "reason_type": "maintenance",
        },
    )

    assert response.status_code == 403


def test_backend_restart_authorization_accepts_admin_with_reason_and_creates_notice(
    client: TestClient,
    admin_user: User,
) -> None:
    authorize_response = client.post(
        "/api/v1/auth/backend-restart/authorize",
        json={
            "operator_email": admin_user.email,
            "admin_email": admin_user.email,
            "admin_password": "OldPassword123",
            "reason_type": "hang",
        },
    )
    assert authorize_response.status_code == 200
    notice_id = authorize_response.json()["notice_id"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "OldPassword123"},
    )
    token = login_response.json()["access_token"]
    notice_response = client.get(
        "/api/v1/auth/backend-restart/notice",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert notice_response.status_code == 200
    body = notice_response.json()
    assert body["has_notice"] is True
    assert body["notice"]["id"] == notice_id
    assert body["notice"]["reason"] == "Backend travado"


def test_backend_restart_authorization_requires_delegated_permission(
    client: TestClient,
    admin_user: User,
    technician_user: User,
) -> None:
    denied_response = client.post(
        "/api/v1/auth/backend-restart/authorize",
        json={
            "operator_email": technician_user.email,
            "admin_email": admin_user.email,
            "admin_password": "OldPassword123",
            "reason_type": "maintenance",
        },
    )
    assert denied_response.status_code == 403


def test_backend_restart_authorization_allows_delegated_account_after_permission_grant(
    client: TestClient,
    auth_headers: dict[str, str],
    admin_user: User,
    technician_user: User,
) -> None:
    update_permissions = client.put(
        "/api/v1/auth/backend-restart/permissions",
        headers=auth_headers,
        json={"allowed_emails": [technician_user.email]},
    )
    assert update_permissions.status_code == 200
    assert update_permissions.json()["allowed_emails"] == [technician_user.email]

    authorize_response = client.post(
        "/api/v1/auth/backend-restart/authorize",
        json={
            "operator_email": technician_user.email,
            "admin_email": admin_user.email,
            "admin_password": "OldPassword123",
            "reason_type": "other",
            "custom_reason": "Manutencao no host da empresa",
        },
    )
    assert authorize_response.status_code == 200
    assert authorize_response.json()["reason"] == "Manutencao no host da empresa"


def test_backend_restart_authorization_has_three_second_cooldown(
    client: TestClient,
    admin_user: User,
) -> None:
    first_response = client.post(
        "/api/v1/auth/backend-restart/authorize",
        json={
            "operator_email": admin_user.email,
            "admin_email": admin_user.email,
            "admin_password": "OldPassword123",
            "reason_type": "maintenance",
        },
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/auth/backend-restart/authorize",
        json={
            "operator_email": admin_user.email,
            "admin_email": admin_user.email,
            "admin_password": "OldPassword123",
            "reason_type": "maintenance",
        },
    )
    assert second_response.status_code == 429
