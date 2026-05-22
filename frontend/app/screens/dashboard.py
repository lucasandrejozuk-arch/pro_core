from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
)

from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
    confirm_destructive_action,
)
from frontend.app.screens.dashboard_layout import build_dashboard_layout
from frontend.app.screens.dashboard_mixins_1 import DashboardMixin1
from frontend.app.screens.dashboard_mixins_1_context import DashboardContextMenuMixin
from frontend.app.screens.dashboard_mixins_2 import DashboardMixin2
from frontend.app.screens.dashboard_mixins_2_forms import DashboardRecordFormsMixin
from frontend.app.screens.dashboard_mixins_2_tools import DashboardToolTabsMixin
from frontend.app.screens.dashboard_mixins_3 import DashboardMixin3
from frontend.app.screens.dashboard_mixins_3_admin_forms import DashboardAdminFormsMixin
from frontend.app.screens.dashboard_mixins_3_operational_forms import DashboardOperationalFormsMixin
from frontend.app.screens.dashboard_mixins_4 import DashboardMixin4
from frontend.app.screens.dashboard_mixins_4_state import DashboardFormStateMixin
from frontend.app.screens.dashboard_mixins_5 import DashboardMixin5
from frontend.app.screens.dashboard_mixins_5_equipment import DashboardEquipmentMixin
from frontend.app.screens.dashboard_mixins_5_support import DashboardEquipmentSupportMixin
from frontend.app.screens.dashboard_mixins_6 import DashboardMixin6
from frontend.app.screens.dashboard_mixins_6_admin import DashboardAdminActionsMixin
from frontend.app.screens.dashboard_mixins_6_formatting import DashboardFormattingMixin
from frontend.app.screens.dashboard_mixins_7 import DashboardMixin7
from frontend.app.screens.dashboard_state import initialize_dashboard_state

__all__ = [
    "DashboardWindow",
    "EquipmentAssetDialog",
    "EquipmentDefectCasesDialog",
    "QFileDialog",
    "QMessageBox",
    "confirm_destructive_action",
]


class DashboardWindow(
    DashboardMixin1,
    DashboardContextMenuMixin,
    DashboardMixin2,
    DashboardRecordFormsMixin,
    DashboardToolTabsMixin,
    DashboardMixin3,
    DashboardOperationalFormsMixin,
    DashboardAdminFormsMixin,
    DashboardMixin4,
    DashboardFormStateMixin,
    DashboardMixin5,
    DashboardEquipmentMixin,
    DashboardEquipmentSupportMixin,
    DashboardMixin6,
    DashboardAdminActionsMixin,
    DashboardFormattingMixin,
    DashboardMixin7,
    QWidget,
):
    logout_requested = Signal()
    exit_requested = Signal()
    module_selected = Signal(str)
    refresh_requested = Signal()
    customer_create_requested = Signal(dict)
    customer_update_requested = Signal(str, dict)
    customer_delete_requested = Signal(str)
    customer_document_upload_requested = Signal(str, str, str)
    equipment_create_requested = Signal(dict)
    equipment_update_requested = Signal(str, dict)
    equipment_delete_requested = Signal(str)
    equipment_board_create_requested = Signal(str, dict)
    equipment_board_update_requested = Signal(str, str, dict)
    equipment_board_delete_requested = Signal(str, str)
    equipment_component_create_requested = Signal(str, str, dict)
    equipment_component_update_requested = Signal(str, str, str, dict)
    equipment_component_delete_requested = Signal(str, str, str)
    equipment_defect_cases_requested = Signal(str)
    equipment_import_requested = Signal(str, bool)
    equipment_export_requested = Signal(str, str)
    inventory_create_requested = Signal(dict)
    inventory_update_requested = Signal(str, dict)
    inventory_delete_requested = Signal(str)
    inventory_document_download_requested = Signal(str, str)
    sector_create_requested = Signal(dict)
    sector_update_requested = Signal(str, dict)
    sector_delete_requested = Signal(str)
    service_order_create_requested = Signal(dict)
    service_order_update_requested = Signal(str, dict)
    service_order_delete_requested = Signal(str)
    service_order_diagnosis_requested = Signal(str, str)
    service_order_budget_item_requested = Signal(str, dict)
    service_order_submit_quote_requested = Signal(str)
    service_order_approve_requested = Signal(str)
    service_order_reject_requested = Signal(str, str)
    service_order_start_requested = Signal(str)
    service_order_complete_requested = Signal(str)
    service_order_document_upload_requested = Signal(str, str, str)
    user_create_requested = Signal(dict)
    user_update_requested = Signal(str, dict)
    user_delete_requested = Signal(str)
    user_password_reset_requested = Signal(str, str)
    user_resource_access_update_requested = Signal(str, list, list)
    password_reset_resolve_requested = Signal(str, str)
    password_reset_cancel_requested = Signal(str)
    settings_update_requested = Signal(dict)
    ui_scale_changed = Signal(float)
    backup_run_requested = Signal()
    backend_restart_requested = Signal()
    customer_portal_open_requested = Signal()
    audit_delete_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        initialize_dashboard_state(self)
        build_dashboard_layout(self)
        self._apply_compact_density()
        self._install_input_guards()
        self.apply_display_profile()
        self._set_record_editor_open(False)
        self._mark_active_nav(self.active_module_key)

    def request_exit(self) -> None:
        answer = QMessageBox.question(
            self,
            "Fechar programa",
            "Deseja realmente fechar o PRO CORE?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.exit_requested.emit()
