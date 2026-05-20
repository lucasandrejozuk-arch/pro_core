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
