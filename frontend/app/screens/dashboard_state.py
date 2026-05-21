from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtWidgets import QDialog, QVBoxLayout


def initialize_dashboard_state(self) -> None:
    self.active_module_key = "dashboard"
    self.current_rows: list[dict[str, Any]] = []
    self.all_rows: list[dict[str, Any]] = []
    self.current_columns: list[tuple[str, str]] = []
    self.equipment_visible_rows: list[dict[str, Any]] = []
    self.equipment_board_visible_rows: list[dict[str, Any]] = []
    self.equipment_component_visible_rows: list[dict[str, Any]] = []
    self.selected_customer_id: str | None = None
    self.selected_customer_document_path: str | None = None
    self.selected_equipment_id: str | None = None
    self.selected_equipment_board_id: str | None = None
    self.selected_equipment_component_id: str | None = None
    self.selected_inventory_item_id: str | None = None
    self.selected_service_order_id: str | None = None
    self.selected_sector_id: str | None = None
    self.selected_user_id: str | None = None
    self.selected_password_reset_request_id: str | None = None
    self.selected_password_reset_status: str | None = None
    self.selected_service_order_document_path: str | None = None
    self.current_tools: list[dict[str, Any]] = []
    self.current_settings: dict[str, Any] = {}
    self.current_selected_record: dict[str, Any] | None = None
    self.current_selected_summary = "Nenhum item selecionado."
    self.record_editor_dialog: QDialog | None = None
    self.record_details_dialog: QDialog | None = None
    self.record_editor_popup_layout: QVBoxLayout | None = None
    self.ui_scale_min = 0.82
    self.ui_scale_max = 1.18
    self.ui_scale_value = 1.0
    self.current_user_role = ""
    self.equipment_customers: list[dict[str, Any]] = []
    self.service_order_customers: list[dict[str, Any]] = []
    self.service_order_equipment: list[dict[str, Any]] = []
    self.service_order_technicians: list[dict[str, Any]] = []
    self.user_sectors: list[dict[str, Any]] = []
    self.current_user: dict[str, Any] = {}
    self.session_login_at: datetime | None = None
    self.sidebar_collapsed = False
    self.record_editor_collapsed = True
    self.record_editor_width = 720
    self.current_page = 1
    self.page_size = 10
    self.total_pages = 1
    self.admin_module_keys = (
        "sectors",
        "users",
        "password_resets",
        "audit_logs",
    )
    self.management_module_keys = ()
    self.dashboard_grid_columns = 4
