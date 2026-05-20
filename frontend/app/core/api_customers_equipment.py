from __future__ import annotations

from pathlib import Path
from typing import Any


class CustomerEquipmentApiMixin:
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
