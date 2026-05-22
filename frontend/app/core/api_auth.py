from __future__ import annotations

from typing import Any


class AuthApiMixin:
    def login(self, email: str, password: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

    def me(self, access_token: str) -> dict[str, Any]:
        return self._request("GET", "auth/me", access_token=access_token)

    def change_password(
        self,
        access_token: str,
        current_password: str,
        new_password: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "auth/change-password",
            access_token=access_token,
            json={
                "current_password": current_password,
                "new_password": new_password,
            },
        )

    def request_password_reset(self, email: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "auth/password-reset-requests",
            json={"email": email},
        )

    def authorize_backend_restart(
        self,
        *,
        operator_email: str,
        admin_email: str,
        admin_password: str,
        reason_type: str,
        custom_reason: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "auth/backend-restart/authorize",
            json={
                "operator_email": operator_email,
                "admin_email": admin_email,
                "admin_password": admin_password,
                "reason_type": reason_type,
                "custom_reason": custom_reason,
            },
        )

    def poll_backend_restart_notice(
        self,
        access_token: str,
        *,
        last_notice_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if last_notice_id:
            params["last_notice_id"] = last_notice_id
        return self._request(
            "GET",
            "auth/backend-restart/notice",
            access_token=access_token,
            params=params or None,
        )
