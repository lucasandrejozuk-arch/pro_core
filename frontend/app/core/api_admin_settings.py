from __future__ import annotations

from typing import Any

from frontend.app.core.api_errors import ApiError


class AdminSettingsApiMixin:
    def list_technicians(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "users/technicians", access_token=access_token)

    def list_users(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "users", access_token=access_token)

    def list_user_resource_access(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "users/resource-access", access_token=access_token)

    def update_user_resource_access(
        self,
        access_token: str,
        user_id: str,
        allowed_resources: list[str],
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"users/{user_id}/resource-access",
            access_token=access_token,
            json={"allowed_resources": allowed_resources},
        )

    def create_user(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "users",
            access_token=access_token,
            json=payload,
        )

    def update_user(
        self,
        access_token: str,
        user_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"users/{user_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_user(self, access_token: str, user_id: str) -> None:
        self._request("DELETE", f"users/{user_id}", access_token=access_token)

    def reset_user_password(
        self,
        access_token: str,
        user_id: str,
        new_password: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"users/{user_id}/reset-password",
            access_token=access_token,
            json={"new_password": new_password},
        )

    def list_password_reset_requests(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list(
            "GET",
            "password-reset-requests",
            access_token=access_token,
        )

    def resolve_password_reset_request(
        self,
        access_token: str,
        request_id: str,
        new_password: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"password-reset-requests/{request_id}/resolve",
            access_token=access_token,
            json={"new_password": new_password},
        )

    def cancel_password_reset_request(
        self,
        access_token: str,
        request_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"password-reset-requests/{request_id}/cancel",
            access_token=access_token,
        )

    def list_sectors(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "sectors", access_token=access_token)

    def create_sector(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "sectors",
            access_token=access_token,
            json=payload,
        )

    def update_sector(
        self,
        access_token: str,
        sector_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"sectors/{sector_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_sector(self, access_token: str, sector_id: str) -> None:
        try:
            self._request("DELETE", f"sectors/{sector_id}", access_token=access_token)
        except ApiError as exc:
            if exc.status_code != 405:
                raise
            self._request("POST", f"sectors/{sector_id}/delete", access_token=access_token)

    def get_settings(self, access_token: str) -> dict[str, Any]:
        return self._request("GET", "settings", access_token=access_token)

    def get_appearance_settings(self, access_token: str) -> dict[str, Any]:
        return self._request("GET", "settings/appearance", access_token=access_token)

    def get_login_appearance_settings(self) -> dict[str, Any]:
        return self._request("GET", "settings/login-appearance")

    def update_settings(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "PATCH",
            "settings",
            access_token=access_token,
            json=payload,
        )

    def run_backup(self, access_token: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "settings/backup/run",
            access_token=access_token,
        )

    def list_audit_logs(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "audit-logs", access_token=access_token)

    def delete_audit_log(self, access_token: str, log_id: str) -> None:
        self._request("DELETE", f"audit-logs/{log_id}", access_token=access_token)

    def list_tools(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "tools", access_token=access_token)
