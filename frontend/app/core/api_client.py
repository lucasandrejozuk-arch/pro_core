from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

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

    def list_customers(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "customers", access_token=access_token)

    def create_customer(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "customers",
            access_token=access_token,
            json=payload,
        )

    def update_customer(
        self,
        access_token: str,
        customer_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"customers/{customer_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_customer(self, access_token: str, customer_id: str) -> None:
        self._request("DELETE", f"customers/{customer_id}", access_token=access_token)

    def list_equipment(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "equipment", access_token=access_token)

    def create_equipment(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "equipment",
            access_token=access_token,
            json=payload,
        )

    def update_equipment(
        self,
        access_token: str,
        equipment_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"equipment/{equipment_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_equipment(self, access_token: str, equipment_id: str) -> None:
        self._request(
            "DELETE",
            f"equipment/{equipment_id}",
            access_token=access_token,
        )

    def export_equipment(self, access_token: str, export_format: str) -> bytes:
        return self._download(
            "GET",
            "equipment/export",
            access_token=access_token,
            params={"format": export_format},
        )

    def import_equipment(
        self,
        access_token: str,
        file_path: str,
        replace: bool = False,
    ) -> dict[str, Any]:
        path = Path(file_path)
        with path.open("rb") as upload_file:
            return self._request(
                "POST",
                "equipment/import",
                access_token=access_token,
                params={"replace": str(replace).lower()},
                files={"file": (path.name, upload_file, "text/csv")},
            )

    def create_equipment_board(
        self,
        access_token: str,
        equipment_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"equipment/{equipment_id}/boards",
            access_token=access_token,
            json=payload,
        )

    def update_equipment_board(
        self,
        access_token: str,
        equipment_id: str,
        board_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"equipment/{equipment_id}/boards/{board_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_equipment_board(
        self,
        access_token: str,
        equipment_id: str,
        board_id: str,
    ) -> None:
        self._request(
            "DELETE",
            f"equipment/{equipment_id}/boards/{board_id}",
            access_token=access_token,
        )

    def create_equipment_board_component(
        self,
        access_token: str,
        equipment_id: str,
        board_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"equipment/{equipment_id}/boards/{board_id}/components",
            access_token=access_token,
            json=payload,
        )

    def update_equipment_board_component(
        self,
        access_token: str,
        equipment_id: str,
        board_id: str,
        component_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"equipment/{equipment_id}/boards/{board_id}/components/{component_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_equipment_board_component(
        self,
        access_token: str,
        equipment_id: str,
        board_id: str,
        component_id: str,
    ) -> None:
        self._request(
            "DELETE",
            f"equipment/{equipment_id}/boards/{board_id}/components/{component_id}",
            access_token=access_token,
        )

    def list_equipment_defect_cases(
        self,
        access_token: str,
        equipment_id: str,
        query: str = "",
    ) -> list[dict[str, Any]]:
        return self._request_list(
            "GET",
            f"equipment/{equipment_id}/defect-cases",
            access_token=access_token,
            params={"query": query},
        )

    def create_equipment_defect_case(
        self,
        access_token: str,
        equipment_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"equipment/{equipment_id}/defect-cases",
            access_token=access_token,
            json=payload,
        )

    def update_equipment_defect_case(
        self,
        access_token: str,
        equipment_id: str,
        case_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"equipment/{equipment_id}/defect-cases/{case_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_equipment_defect_case(
        self,
        access_token: str,
        equipment_id: str,
        case_id: str,
    ) -> None:
        self._request(
            "DELETE",
            f"equipment/{equipment_id}/defect-cases/{case_id}",
            access_token=access_token,
        )

    def list_inventory(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "inventory", access_token=access_token)

    def create_inventory_item(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "inventory",
            access_token=access_token,
            json=payload,
        )

    def update_inventory_item(
        self,
        access_token: str,
        item_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"inventory/{item_id}",
            access_token=access_token,
            json=payload,
        )

    def delete_inventory_item(self, access_token: str, item_id: str) -> None:
        self._request("DELETE", f"inventory/{item_id}", access_token=access_token)

    def list_service_orders(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "service-orders", access_token=access_token)

    def create_service_order(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "service-orders",
            access_token=access_token,
            json=payload,
        )

    def delete_service_order(self, access_token: str, service_order_id: str) -> None:
        self._request(
            "DELETE",
            f"service-orders/{service_order_id}",
            access_token=access_token,
        )

    def update_service_order(
        self,
        access_token: str,
        service_order_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"service-orders/{service_order_id}",
            access_token=access_token,
            json=payload,
        )

    def register_service_order_diagnosis(
        self,
        access_token: str,
        service_order_id: str,
        technical_diagnosis: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/diagnosis",
            access_token=access_token,
            json={"technical_diagnosis": technical_diagnosis},
        )

    def add_service_order_budget_item(
        self,
        access_token: str,
        service_order_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/budget-items",
            access_token=access_token,
            json=payload,
        )

    def submit_service_order_quote(
        self,
        access_token: str,
        service_order_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/submit-quote",
            access_token=access_token,
        )

    def approve_service_order(self, access_token: str, service_order_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/approve",
            access_token=access_token,
        )

    def reject_service_order(
        self,
        access_token: str,
        service_order_id: str,
        rejection_reason: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/reject",
            access_token=access_token,
            json={"rejection_reason": rejection_reason},
        )

    def start_service_order(self, access_token: str, service_order_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/start",
            access_token=access_token,
        )

    def complete_service_order(self, access_token: str, service_order_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"service-orders/{service_order_id}/complete",
            access_token=access_token,
        )

    def download_service_order_quote(self, access_token: str, service_order_id: str) -> bytes:
        return self._download(
            "GET",
            f"service-orders/{service_order_id}/quote.pdf",
            access_token=access_token,
        )

    def list_documents(
        self,
        access_token: str,
        service_order_id: str | None = None,
        customer_id: str | None = None,
        equipment_id: str | None = None,
    ) -> list[dict[str, Any]]:
        params = {
            key: value
            for key, value in {
                "service_order_id": service_order_id,
                "customer_id": customer_id,
                "equipment_id": equipment_id,
            }.items()
            if value
        }
        return self._request_list(
            "GET",
            "documents",
            access_token=access_token,
            params=params,
        )

    def upload_document(
        self,
        access_token: str,
        file_path: str,
        document_type: str,
        service_order_id: str | None = None,
        customer_id: str | None = None,
        equipment_id: str | None = None,
    ) -> dict[str, Any]:
        path = Path(file_path)
        data = {
            key: value
            for key, value in {
                "document_type": document_type,
                "service_order_id": service_order_id,
                "customer_id": customer_id,
                "equipment_id": equipment_id,
            }.items()
            if value
        }
        with path.open("rb") as upload_file:
            return self._request(
                "POST",
                "documents",
                access_token=access_token,
                data=data,
                files={"file": (path.name, upload_file, "application/octet-stream")},
            )

    def list_technicians(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "users/technicians", access_token=access_token)

    def list_users(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "users", access_token=access_token)

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

    def list_financial_records(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "financial-records", access_token=access_token)

    def create_financial_record(self, access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request(
            "POST",
            "financial-records",
            access_token=access_token,
            json=payload,
        )

    def mark_financial_record_paid(self, access_token: str, record_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"financial-records/{record_id}/mark-paid",
            access_token=access_token,
        )

    def cancel_financial_record(self, access_token: str, record_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"financial-records/{record_id}/cancel",
            access_token=access_token,
        )

    def delete_financial_record(self, access_token: str, record_id: str) -> None:
        self._request("DELETE", f"financial-records/{record_id}", access_token=access_token)

    def list_audit_logs(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "audit-logs", access_token=access_token)

    def list_notifications(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "notifications", access_token=access_token)

    def list_tools(self, access_token: str) -> list[dict[str, Any]]:
        return self._request_list("GET", "tools", access_token=access_token)

    def get_report(self, access_token: str, module_key: str) -> dict[str, Any]:
        return self._request("GET", f"reports/{module_key}", access_token=access_token)

    def export_report(
        self,
        access_token: str,
        module_key: str,
        report_format: str,
    ) -> bytes:
        return self._download(
            "GET",
            f"reports/{module_key}/export",
            access_token=access_token,
            params={"format": report_format},
        )

    def _request_list(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        data = self._request(method, path, access_token=access_token, **kwargs)
        if not isinstance(data, list):
            raise ApiError("Resposta inesperada do backend.")

        return data

    def _request(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> Any:
        headers = dict(kwargs.pop("headers", {}))
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self._client.request(method, path, headers=headers, **kwargs)
        except httpx.ConnectError as exc:
            raise ApiError("Nao foi possivel conectar ao backend.") from exc
        except httpx.TimeoutException as exc:
            raise ApiError("Tempo limite excedido ao conectar ao backend.") from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"Falha de comunicacao com o backend: {exc}") from exc

        if response.is_error:
            raise ApiError(self._extract_error_message(response), response.status_code)

        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    def _download(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> bytes:
        headers = dict(kwargs.pop("headers", {}))
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self._client.request(method, path, headers=headers, **kwargs)
        except httpx.ConnectError as exc:
            raise ApiError("Nao foi possivel conectar ao backend.") from exc
        except httpx.TimeoutException as exc:
            raise ApiError("Tempo limite excedido ao conectar ao backend.") from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"Falha de comunicacao com o backend: {exc}") from exc

        if response.is_error:
            raise ApiError(self._extract_error_message(response), response.status_code)

        return response.content

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            return response.text or "Erro inesperado do backend."

        detail = body.get("detail")
        if isinstance(detail, str):
            return detail

        if isinstance(detail, list) and detail:
            first_error = detail[0]
            if isinstance(first_error, dict) and "msg" in first_error:
                return str(first_error["msg"])

        return "Erro inesperado do backend."
