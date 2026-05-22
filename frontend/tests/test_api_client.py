from __future__ import annotations

import json

import httpx
import pytest

from frontend.app.core.api_client import ApiClient, ApiError


def test_login_posts_credentials_and_returns_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/auth/login"
        assert json.loads(request.content) == {
            "email": "admin@example.com",
            "password": "secret",
        }
        return httpx.Response(
            200,
            json={
                "access_token": "token",
                "token_type": "bearer",
                "must_change_password": True,
                "user": {"email": "admin@example.com"},
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.login("admin@example.com", "secret")

    assert response["access_token"] == "token"
    assert response["must_change_password"] is True


def test_me_sends_bearer_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"email": "admin@example.com"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.me("token")

    assert response["email"] == "admin@example.com"


def test_change_password_posts_expected_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        assert request.url.path == "/api/v1/auth/change-password"
        assert json.loads(request.content) == {
            "current_password": "old-password",
            "new_password": "new-password",
        }
        return httpx.Response(200, json={"must_change_password": False})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.change_password("token", "old-password", "new-password")

    assert response["must_change_password"] is False


def test_request_password_reset_posts_email() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/auth/password-reset-requests"
        assert json.loads(request.content) == {"email": "user@example.com"}
        return httpx.Response(200, json={"message": "Solicitacao enviada."})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.request_password_reset("user@example.com")

    assert response["message"] == "Solicitacao enviada."


def test_authorize_backend_restart_posts_required_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/auth/backend-restart/authorize"
        assert json.loads(request.content) == {
            "operator_email": "tech@example.com",
            "admin_email": "admin@example.com",
            "admin_password": "secret",
            "reason_type": "maintenance",
            "custom_reason": None,
        }
        return httpx.Response(
            200,
            json={
                "message": "Reinicio autorizado e aviso global registrado.",
                "notice_id": "notice-1",
                "reason": "Manutencao programada",
                "created_at": "2026-05-21T00:00:00+00:00",
            },
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.authorize_backend_restart(
        operator_email="tech@example.com",
        admin_email="admin@example.com",
        admin_password="secret",
        reason_type="maintenance",
    )

    assert response["notice_id"] == "notice-1"


def test_poll_backend_restart_notice_sends_last_notice_id_query_param() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/auth/backend-restart/notice"
        assert request.url.params.get("last_notice_id") == "notice-1"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"has_notice": False, "notice": None})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.poll_backend_restart_notice("token", last_notice_id="notice-1")

    assert response["has_notice"] is False


def test_error_response_raises_api_error_with_backend_detail() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid email or password."})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ApiError) as exc_info:
        client.login("admin@example.com", "wrong")

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Email ou senha invalidos."
    assert exc_info.value.display_message == "Erro 401: Email ou senha invalidos."


def test_server_error_does_not_expose_internal_detail() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            json={"detail": "sqlalchemy.exc.IntegrityError: database path C:\\app\\db.sqlite"},
        )

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ApiError) as exc_info:
        client.list_customers("token")

    assert exc_info.value.message == (
        "Falha interna no servidor. Tente novamente ou acione o suporte."
    )


def test_list_customers_returns_list_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v1/customers"
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json=[{"name": "Cliente Teste"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_customers("token")

    assert response == [{"name": "Cliente Teste"}]


def test_idempotent_requests_retry_after_transient_connect_error() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ConnectError("offline", request=request)
        return httpx.Response(200, json=[{"name": "Cliente Teste"}])

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.list_customers("token")

    assert calls["count"] == 2
    assert response == [{"name": "Cliente Teste"}]


def test_request_rejects_invalid_json_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>invalid</html>")

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ApiError) as exc_info:
        client.list_customers("token")

    assert exc_info.value.message == "Resposta invalida do backend."


def test_create_customer_posts_payload() -> None:
    payload = {
        "name": "Cliente Teste",
        "email": "cliente@example.com",
        "phone": "(11) 99999-9999",
        "address": None,
        "notes": None,
        "is_active": True,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/customers"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(201, json=payload | {"id": "customer-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.create_customer("token", payload)

    assert response["id"] == "customer-id"


def test_update_customer_patches_payload() -> None:
    payload = {"name": "Cliente Atualizado", "phone": "(11) 98888-8888"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/v1/customers/customer-id"
        assert request.headers["Authorization"] == "Bearer token"
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=payload | {"id": "customer-id"})

    client = ApiClient(
        "http://testserver/api/v1",
        transport=httpx.MockTransport(handler),
    )

    response = client.update_customer("token", "customer-id", payload)

    assert response["name"] == "Cliente Atualizado"
