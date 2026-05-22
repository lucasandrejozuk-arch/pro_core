from __future__ import annotations

from datetime import datetime


class ProCoreDataHelpersMixin:
    @staticmethod
    def _dependencies_from_service_orders(
        rows: list[dict],
    ) -> tuple[list[dict], list[dict], list[dict]]:
        customers: dict[str, dict] = {}
        equipment: dict[str, dict] = {}
        for row in rows:
            customer_id = str(row.get("customer_id") or "")
            if customer_id:
                customers[customer_id] = {
                    "id": customer_id,
                    "name": row.get("customer_name") or customer_id,
                    "email": row.get("customer_email") or "",
                }
            equipment_id = str(row.get("equipment_id") or "")
            if equipment_id:
                equipment[equipment_id] = {
                    "id": equipment_id,
                    "category": row.get("equipment_label") or equipment_id,
                    "brand": "",
                    "model": "",
                    "special_number": "",
                    "serial_number": "",
                }
        return list(customers.values()), list(equipment.values()), []

    def _dashboard_greeting(self) -> str:
        full_name = str(self.session.user.get("full_name") or "usuario")
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        return f"{greeting}, {full_name}. Acompanhe os indicadores operacionais do dia."

    @staticmethod
    def _to_decimal(value) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0
