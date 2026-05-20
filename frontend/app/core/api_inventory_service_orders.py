from __future__ import annotations

from pathlib import Path
from typing import Any


class InventoryServiceOrderApiMixin:
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
