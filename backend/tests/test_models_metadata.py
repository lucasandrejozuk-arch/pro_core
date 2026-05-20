import backend.app.models  # noqa: F401
from backend.app.db.base import Base


def test_core_tables_are_registered() -> None:
    expected_tables = {
        "app_settings",
        "audit_logs",
        "backup_policies",
        "companies",
        "customers",
        "document_attachments",
        "equipment",
        "equipment_board_components",
        "equipment_boards",
        "inventory_items",
        "sectors",
        "service_order_budget_items",
        "service_order_events",
        "service_orders",
        "users",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))
