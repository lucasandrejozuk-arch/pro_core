# ruff: noqa: F401, F821, E501
from __future__ import annotations

import math
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QResizeEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.display import DisplayProfile, detect_display_profile
from frontend.app.core.grid import GRID_COLUMNS, add_layout, add_widget, create_grid, span_for_items
from frontend.app.core.icons import build_icon
from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
)
from frontend.app.themes.styles import COLOR_PALETTE_OPTIONS, DEFAULT_COLOR_PALETTE
from frontend.app.widgets import DashboardKpiCard, create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin4:
    def _build_settings_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("CONFIGURACOES DO SISTEMA")
        title.setObjectName("sectionTitle")

        self.settings_company_name_input = QLineEdit()
        self.settings_company_name_input.setPlaceholderText("Razao social")

        self.settings_trade_name_input = QLineEdit()
        self.settings_trade_name_input.setPlaceholderText("Nome fantasia")

        self.settings_document_input = QLineEdit()
        self.settings_document_input.setPlaceholderText("Documento")

        self.settings_email_input = QLineEdit()
        self.settings_email_input.setPlaceholderText("Email")

        self.settings_phone_input = QLineEdit()
        self.settings_phone_input.setPlaceholderText("Telefone")

        self.settings_brand_name_input = QLineEdit()
        self.settings_brand_name_input.setPlaceholderText("Nome exibido no sistema")

        self.settings_brand_subtitle_input = QLineEdit()
        self.settings_brand_subtitle_input.setPlaceholderText("Subtitulo da empresa")

        self.settings_color_palette_combo = QComboBox()
        self._populate_color_palette_combo(self.settings_color_palette_combo)

        self.settings_theme_combo = QComboBox()
        self.settings_theme_combo.addItem("Claro", "light")
        self.settings_theme_combo.addItem("Escuro", "dark")

        self.settings_ui_scale_label = QLabel("100%")
        self.settings_ui_scale_label.setObjectName("mutedText")
        self.settings_ui_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.settings_ui_scale_slider.setMinimum(82)
        self.settings_ui_scale_slider.setMaximum(118)
        self.settings_ui_scale_slider.setValue(100)
        self.settings_ui_scale_slider.valueChanged.connect(self._handle_ui_scale_slider_changed)

        self.settings_backup_enabled_checkbox = QCheckBox("Backup automatico ativo")
        self.settings_backup_enabled_checkbox.setChecked(True)

        self.settings_backup_interval_input = QLineEdit()
        self.settings_backup_interval_input.setPlaceholderText("Intervalo em horas")

        self.settings_backup_path_input = QLineEdit()
        self.settings_backup_path_input.setPlaceholderText("Pasta de backup")

        self.settings_backup_last_run_label = QLabel("Ultimo backup: nunca")
        self.settings_backup_last_run_label.setObjectName("mutedText")

        company_layout = QFormLayout()
        company_layout.setSpacing(10)
        company_layout.addRow("Empresa", self.settings_company_name_input)
        company_layout.addRow("Nome fantasia", self.settings_trade_name_input)
        company_layout.addRow("Documento", self.settings_document_input)
        company_layout.addRow("Email", self.settings_email_input)
        company_layout.addRow("Telefone", self.settings_phone_input)

        company_panel = QFrame()
        company_panel.setObjectName("formSubPanel")
        company_panel_layout = QVBoxLayout(company_panel)
        company_panel_layout.setContentsMargins(12, 12, 12, 12)
        company_panel_layout.setSpacing(8)
        company_title = QLabel("DADOS DA EMPRESA")
        company_title.setObjectName("formGroupTitle")
        company_panel_layout.addWidget(company_title)
        company_panel_layout.addLayout(company_layout)

        branding_layout = QFormLayout()
        branding_layout.setSpacing(10)
        branding_layout.addRow("Nome exibido", self.settings_brand_name_input)
        branding_layout.addRow("Subtitulo", self.settings_brand_subtitle_input)
        branding_layout.addRow("Paleta", self.settings_color_palette_combo)

        branding_panel = QFrame()
        branding_panel.setObjectName("formSubPanel")
        branding_panel_layout = QVBoxLayout(branding_panel)
        branding_panel_layout.setContentsMargins(12, 12, 12, 12)
        branding_panel_layout.setSpacing(8)
        branding_title = QLabel("PERSONALIZACAO")
        branding_title.setObjectName("formGroupTitle")
        branding_panel_layout.addWidget(branding_title)
        branding_panel_layout.addLayout(branding_layout)

        operation_layout = QFormLayout()
        operation_layout.setSpacing(10)
        operation_layout.addRow("Tema", self.settings_theme_combo)
        scale_row = QHBoxLayout()
        scale_row.addWidget(self.settings_ui_scale_slider, 1)
        scale_row.addWidget(self.settings_ui_scale_label)
        operation_layout.addRow("Escala da interface", scale_row)
        operation_layout.addRow("", self.settings_backup_enabled_checkbox)
        operation_layout.addRow("Intervalo", self.settings_backup_interval_input)
        operation_layout.addRow("Destino", self.settings_backup_path_input)

        operation_panel = QFrame()
        operation_panel.setObjectName("formSubPanel")
        operation_panel_layout = QVBoxLayout(operation_panel)
        operation_panel_layout.setContentsMargins(12, 12, 12, 12)
        operation_panel_layout.setSpacing(8)
        operation_title = QLabel("CONFIGURACOES GERAIS")
        operation_title.setObjectName("formGroupTitle")
        operation_panel_layout.addWidget(operation_title)
        operation_panel_layout.addLayout(operation_layout)

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, company_panel, 0, 0, 6)
        add_widget(fields_layout, branding_panel, 0, 6, 6)
        add_widget(fields_layout, operation_panel, 1)

        settings_details_title = QLabel("RESUMO OPERACIONAL")
        settings_details_title.setObjectName("formGroupTitle")
        self.settings_full_summary = create_summary_text()

        self.settings_form_status = QLabel("")
        self.settings_form_status.setObjectName("mutedText")

        self.settings_save_button = QPushButton("Salvar configuracoes")
        self.settings_save_button.clicked.connect(self._request_settings_save)

        self.settings_run_backup_button = QPushButton("Executar backup agora")
        self.settings_run_backup_button.setObjectName("secondaryButton")
        self.settings_run_backup_button.clicked.connect(self.backup_run_requested.emit)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.settings_run_backup_button)
        actions.addWidget(self.settings_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addLayout(fields_layout)
        layout.addWidget(settings_details_title)
        layout.addWidget(self.settings_full_summary)
        layout.addWidget(self.settings_backup_last_run_label)
        layout.addWidget(self.settings_form_status)
        layout.addLayout(actions)

        return panel

    def _build_admin_area_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("AREA ADMINISTRATIVA")
        title.setObjectName("sectionTitle")
        description = QLabel("Usuarios, setores, solicitacoes de senha e logs de auditoria.")
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        self.admin_area_actions_layout = create_grid(spacing=10, margins=(0, 0, 0, 0))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(self.admin_area_actions_layout)
        layout.addStretch()
        return panel

    def render_admin_area(self) -> None:
        self._set_active_module("admin_area")
        self._clear_layout(self.admin_area_actions_layout)
        allowed_modules = [
            module_key
            for module_key in self._allowed_admin_modules()
            if module_key in {"sectors", "users", "password_resets", "audit_logs"}
        ]
        if not allowed_modules:
            label = QLabel("Seu perfil nao possui acesso a area administrativa.")
            label.setObjectName("mutedText")
            self.admin_area_actions_layout.addWidget(label, 0, 0, 1, GRID_COLUMNS)
            return
        for index, module_key in enumerate(allowed_modules):
            button = QPushButton(self.module_labels[module_key])
            button.setObjectName("adminMenuButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, key=module_key: self.module_selected.emit(key)
            )
            self.admin_area_actions_layout.addWidget(button, index // 2, (index % 2) * 6, 1, 6)

    def _build_audit_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("LOGS E AUDITORIA")
        title.setObjectName("sectionTitle")
        self.audit_full_summary = create_summary_text()
        self.audit_form_status = QLabel("")
        self.audit_form_status.setObjectName("mutedText")
        self.audit_delete_button = QPushButton("Excluir log")
        self.audit_delete_button.setObjectName("dangerButton")
        self.audit_delete_button.setEnabled(False)
        self.audit_delete_button.clicked.connect(self._request_audit_delete)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.audit_delete_button)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.audit_full_summary)
        layout.addWidget(self.audit_form_status)
        layout.addLayout(actions)
        return panel

    def clear_customer_form(self) -> None:
        self.selected_customer_id = None
        self.selected_customer_document_path = None
        self.customer_name_input.clear()
        self.customer_email_input.clear()
        self.customer_phone_input.clear()
        self.customer_address_input.clear()
        self.customer_notes_input.clear()
        self.customer_document_path_input.clear()
        self.customer_active_checkbox.setChecked(True)
        self.customer_full_summary.setPlainText("Novo registro de cliente.")
        self.customer_form_status.setText("Novo cliente.")
        self.customer_delete_button.setEnabled(False)
        self.table.clearSelection()

    def set_customer_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.customer_form_status, message, is_error)

    def set_customer_form_loading(self, is_loading: bool) -> None:
        has_selection = bool(self.selected_customer_id)
        self.customer_save_button.setEnabled(not is_loading)
        self.customer_new_button.setEnabled(not is_loading)
        self.customer_delete_button.setEnabled(not is_loading and has_selection)
        self.customer_save_button.setText("Salvando..." if is_loading else "Salvar cliente")

    def set_customer_document_upload_loading(self, is_loading: bool) -> None:
        self.customer_select_document_button.setEnabled(not is_loading)
        self.customer_upload_document_button.setEnabled(
            not is_loading and bool(self.selected_customer_id)
        )
        self.customer_upload_document_button.setText(
            "Enviando..." if is_loading else "Enviar anexo"
        )

    def set_equipment_customers(self, customers: list[dict[str, Any]]) -> None:
        self.equipment_customers = customers

    def clear_equipment_form(self) -> None:
        self.selected_equipment_id = None
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.equipment_visible_rows = []
        self.equipment_board_visible_rows = []
        self.equipment_component_visible_rows = []
        if hasattr(self, "equipment_search_input"):
            self.equipment_search_input.clear()
            self.board_search_input.clear()
            self.component_search_input.clear()
            self.equipment_table.clearSelection()
            self.equipment_boards_table.setRowCount(0)
            self.equipment_components_table.setRowCount(0)
            self.equipment_full_summary.setPlainText(
                "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
            )
            self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
            self.component_full_summary.setPlainText(
                "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
            )
            self.equipment_context_label.setText("_SELECIONE UM EQUIPAMENTO_")
            self.board_context_label.setText("_SELECIONE UM OBJETO VINCULADO_")
            self._update_equipment_action_state()
        self.equipment_form_status.setText("Selecione ou cadastre um equipamento.")
        self.table.clearSelection()

    def set_equipment_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.equipment_form_status, message, is_error)

    def set_equipment_form_loading(self, is_loading: bool) -> None:
        self.equipment_new_button.setEnabled(not is_loading)
        self.equipment_edit_button.setEnabled(not is_loading and bool(self.selected_equipment_id))
        self.equipment_remove_button.setEnabled(not is_loading and bool(self.selected_equipment_id))
        self.equipment_defect_cases_button.setEnabled(
            not is_loading and bool(self.selected_equipment_id)
        )
        self.equipment_import_button.setEnabled(not is_loading)
        self.equipment_export_csv_button.setEnabled(not is_loading)
        self.equipment_export_pdf_button.setEnabled(not is_loading)
        self.equipment_new_button.setText("Salvando..." if is_loading else "+Equipamento")

    def set_equipment_object_loading(self, is_loading: bool) -> None:
        has_equipment = bool(self.selected_equipment_id)
        has_board = bool(self.selected_equipment_board_id)
        self.board_add_button.setEnabled(not is_loading and has_equipment)
        self.board_edit_button.setEnabled(not is_loading and has_board)
        self.board_remove_button.setEnabled(not is_loading and has_board)
        self.component_add_button.setEnabled(not is_loading and has_board)
        self.component_edit_button.setEnabled(
            not is_loading and bool(self.selected_equipment_component_id)
        )
        self.component_remove_button.setEnabled(
            not is_loading and bool(self.selected_equipment_component_id)
        )
        self.board_add_button.setText("Salvando..." if is_loading else "+Objeto Vinculado")
        self.component_add_button.setText("Salvando..." if is_loading else "+Componente")

    def clear_inventory_form(self) -> None:
        self.selected_inventory_item_id = None
        self.inventory_sku_input.clear()
        self.inventory_name_input.clear()
        self.inventory_category_input.clear()
        self.inventory_quantity_input.setText("0")
        self.inventory_minimum_quantity_input.setText("0")
        self.inventory_unit_cost_input.setText("0")
        self.inventory_full_summary.setPlainText("Novo registro de estoque.")
        self._set_inventory_stock_status("Status: novo item.", "info")
        self.inventory_form_status.setText("Novo item de estoque.")
        self.inventory_delete_button.setEnabled(False)
        self.table.clearSelection()

    def set_inventory_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.inventory_form_status, message, is_error)

    def set_inventory_form_loading(self, is_loading: bool) -> None:
        has_selection = bool(self.selected_inventory_item_id)
        self.inventory_save_button.setEnabled(not is_loading)
        self.inventory_new_button.setEnabled(not is_loading)
        self.inventory_delete_button.setEnabled(not is_loading and has_selection)
        self.inventory_save_button.setText("Salvando..." if is_loading else "Salvar item")

    def _set_inventory_stock_status(self, message: str, level: str) -> None:
        self.inventory_stock_status.setText(message)
        self.inventory_stock_status.setProperty("level", level)
        self.inventory_stock_status.style().unpolish(self.inventory_stock_status)
        self.inventory_stock_status.style().polish(self.inventory_stock_status)

    def set_service_order_dependencies(
        self,
        customers: list[dict[str, Any]],
        equipment: list[dict[str, Any]],
        technicians: list[dict[str, Any]],
    ) -> None:
        current_customer_id = self.service_order_customer_combo.currentData()
        current_technician_id = self.service_order_technician_combo.currentData()

        self.service_order_customers = customers
        self.service_order_equipment = equipment
        self.service_order_technicians = technicians

        self.service_order_customer_combo.blockSignals(True)
        self.service_order_customer_combo.clear()
        for customer in customers:
            self.service_order_customer_combo.addItem(
                str(customer.get("name") or "Cliente sem nome"),
                str(customer["id"]),
            )
        self.service_order_customer_combo.blockSignals(False)

        self.service_order_technician_combo.clear()
        self.service_order_technician_combo.addItem("Sem tecnico", "")
        for technician in technicians:
            self.service_order_technician_combo.addItem(
                str(technician.get("full_name") or technician.get("email") or "Tecnico"),
                str(technician["id"]),
            )

        if current_customer_id:
            self._select_combo_value(self.service_order_customer_combo, str(current_customer_id))
        if current_technician_id:
            self._select_combo_value(
                self.service_order_technician_combo, str(current_technician_id)
            )

        self._refresh_service_order_equipment_combo()

        if not customers:
            self.set_service_order_form_status("Cadastre um cliente antes da OS.", is_error=True)
        elif not equipment:
            self.set_service_order_form_status(
                "Cadastre um equipamento antes da OS.", is_error=True
            )

    def clear_service_order_form(self) -> None:
        self.selected_service_order_id = None
        if self.service_order_customer_combo.count() > 0:
            self.service_order_customer_combo.setCurrentIndex(0)
        if self.service_order_technician_combo.count() > 0:
            self.service_order_technician_combo.setCurrentIndex(0)
        self._refresh_service_order_equipment_combo()
        self._select_combo_value(self.service_order_priority_combo, "normal")
        self.service_order_sla_input.clear()
        self.service_order_problem_input.clear()
        self.service_order_diagnosis_input.clear()
        self.service_order_rejection_input.clear()
        if self.service_order_budget_type_combo.count() > 0:
            self.service_order_budget_type_combo.setCurrentIndex(0)
        self.service_order_budget_description_input.clear()
        self.service_order_budget_quantity_input.setText("1")
        self.service_order_budget_unit_price_input.setText("0")
        if self.service_order_document_type_combo.count() > 0:
            self.service_order_document_type_combo.setCurrentIndex(0)
        self.selected_service_order_document_path = None
        self.service_order_document_path_input.clear()
        self.service_order_current_status.setText("Status: nova")
        self.service_order_budget_summary.setText("Orcamento: nenhum item.")
        self.service_order_documents_summary.setText("Anexos: nenhum arquivo.")
        self.service_order_full_summary.setPlainText("Novo registro de ordem de servico.")
        self._update_service_order_workflow(None)
        self._set_service_order_flow_buttons_enabled(False)
        self.service_order_form_status.setText("Nova ordem de servico.")
        self.service_order_delete_button.setEnabled(False)
        self.table.clearSelection()

    def set_service_order_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.service_order_form_status, message, is_error)

    def set_service_order_form_loading(self, is_loading: bool) -> None:
        self.service_order_save_button.setEnabled(not is_loading)
        self.service_order_new_button.setEnabled(not is_loading)
        self.service_order_delete_button.setEnabled(
            not is_loading and bool(self.selected_service_order_id)
        )
        if self.selected_service_order_id:
            self._set_service_order_flow_buttons_enabled(not is_loading)
        self.service_order_save_button.setText("Salvando..." if is_loading else "Salvar OS")

    def set_service_order_action_loading(self, is_loading: bool) -> None:
        self.service_order_save_button.setEnabled(not is_loading)
        self.service_order_new_button.setEnabled(not is_loading)
        self.service_order_delete_button.setEnabled(
            not is_loading and bool(self.selected_service_order_id)
        )
        self._set_service_order_flow_buttons_enabled(
            not is_loading and bool(self.selected_service_order_id)
        )

    def _set_service_order_flow_buttons_enabled(self, enabled: bool) -> None:
        self.service_order_diagnosis_button.setEnabled(enabled)
        self.service_order_add_budget_button.setEnabled(enabled)
        self.service_order_submit_quote_button.setEnabled(enabled)
        self.service_order_approve_button.setEnabled(enabled)
        self.service_order_reject_button.setEnabled(enabled)
        self.service_order_start_button.setEnabled(enabled)
        self.service_order_complete_button.setEnabled(enabled)
        self.service_order_select_document_button.setEnabled(enabled)
        self.service_order_upload_document_button.setEnabled(enabled)

    def set_user_sectors(self, sectors: list[dict[str, Any]]) -> None:
        current_sector_id = self.user_sector_combo.currentData()
        self.user_sectors = sectors
        self.user_sector_combo.clear()
        self.user_sector_combo.addItem("Sem setor", "")

        for sector in sectors:
            self.user_sector_combo.addItem(
                str(sector.get("name") or "Setor sem nome"),
                str(sector["id"]),
            )

        if current_sector_id:
            self._select_combo_value(self.user_sector_combo, str(current_sector_id))
        elif len(sectors) == 1:
            self.user_sector_combo.setCurrentIndex(1)
        self._refresh_session_footer()

    def clear_sector_form(self) -> None:
        self.selected_sector_id = None
        self.sector_name_input.clear()
        self.sector_description_input.clear()
        self.sector_full_summary.setPlainText("Novo registro de setor.")
        self.sector_form_status.setText("Novo setor.")
        is_admin = self.current_user_role == "admin"
        self.sector_new_button.setEnabled(is_admin)
        self.sector_delete_button.setEnabled(False)
        self.sector_save_button.setEnabled(is_admin)
        self.sector_name_input.setEnabled(is_admin)
        self.sector_description_input.setEnabled(is_admin)
        if not is_admin:
            self.sector_form_status.setText("Setor disponivel apenas para consulta.")
        self.table.clearSelection()

    def set_sector_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.sector_form_status, message, is_error)

    def set_sector_form_loading(self, is_loading: bool) -> None:
        is_admin = self.current_user_role == "admin"
        self.sector_save_button.setEnabled(is_admin and not is_loading)
        self.sector_new_button.setEnabled(is_admin and not is_loading)
        self.sector_delete_button.setEnabled(
            is_admin and not is_loading and bool(self.selected_sector_id)
        )
        self.sector_save_button.setText("Salvando..." if is_loading else "Salvar setor")

    def clear_user_form(self) -> None:
        self.selected_user_id = None
        self.user_full_name_input.clear()
        self.user_email_input.clear()
        if self.user_role_combo.count() > 0:
            self.user_role_combo.setCurrentIndex(2)
        if self.user_sector_combo.count() > 1:
            self.user_sector_combo.setCurrentIndex(1)
        elif self.user_sector_combo.count() > 0:
            self.user_sector_combo.setCurrentIndex(0)
        self.user_initial_password_input.clear()
        self.user_initial_password_input.setEnabled(True)
        self.user_active_checkbox.setChecked(True)
        self.user_reset_password_input.clear()
        self.user_reset_password_input.setEnabled(False)
        self.user_reset_password_button.setEnabled(False)
        self.user_delete_button.setEnabled(False)
        self.user_full_summary.setPlainText("Novo registro de usuario.")
        self.user_form_status.setText("Novo usuario.")
        self.table.clearSelection()

    def set_user_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.user_form_status, message, is_error)

    def set_user_form_loading(self, is_loading: bool) -> None:
        self.user_save_button.setEnabled(not is_loading)
        self.user_new_button.setEnabled(not is_loading)
        self.user_reset_password_button.setEnabled(not is_loading and bool(self.selected_user_id))
        self.user_delete_button.setEnabled(not is_loading and bool(self.selected_user_id))
        self.user_save_button.setText("Salvando..." if is_loading else "Salvar usuario")

    def set_user_password_reset_loading(self, is_loading: bool) -> None:
        self.user_reset_password_button.setEnabled(not is_loading and bool(self.selected_user_id))
        self.user_save_button.setEnabled(not is_loading)
        self.user_new_button.setEnabled(not is_loading)
        self.user_delete_button.setEnabled(not is_loading and bool(self.selected_user_id))
        self.user_reset_password_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )

    def clear_password_reset_form(self) -> None:
        self.selected_password_reset_request_id = None
        self.password_reset_requester_label.setText("Selecione uma solicitacao.")
        self.password_reset_new_password_input.clear()
        self.password_reset_resolve_button.setEnabled(False)
        self.password_reset_full_summary.setPlainText("Nenhuma solicitacao selecionada.")
        self.password_reset_form_status.setText("")
        self.table.clearSelection()

    def set_password_reset_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.password_reset_form_status, message, is_error)

    def set_password_reset_form_loading(self, is_loading: bool) -> None:
        self.password_reset_resolve_button.setEnabled(
            not is_loading and bool(self.selected_password_reset_request_id)
        )
        self.password_reset_resolve_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )

    def clear_settings_form(self) -> None:
        self.current_settings = {}
        self.settings_company_name_input.clear()
        self.settings_trade_name_input.clear()
        self.settings_document_input.clear()
        self.settings_email_input.clear()
        self.settings_phone_input.clear()
        self.settings_brand_name_input.clear()
        self.settings_brand_subtitle_input.clear()
        self._select_combo_value(self.settings_color_palette_combo, DEFAULT_COLOR_PALETTE)
        if self.settings_theme_combo.count() > 0:
            self.settings_theme_combo.setCurrentIndex(0)
        self.settings_backup_enabled_checkbox.setChecked(True)
        self.settings_backup_interval_input.setText("24")
        self.settings_backup_path_input.setText("backups")
        self.settings_backup_last_run_label.setText("Ultimo backup: nunca")
        self.settings_full_summary.setPlainText("Configuracoes ainda nao carregadas.")
        self.settings_form_status.setText("")

    def set_settings_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.settings_form_status, message, is_error)

    def set_settings_form_loading(self, is_loading: bool) -> None:
        self.settings_save_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setEnabled(not is_loading)
        self.settings_save_button.setText("Salvando..." if is_loading else "Salvar configuracoes")

    def set_backup_run_loading(self, is_loading: bool) -> None:
        self.settings_save_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setText(
            "Executando..." if is_loading else "Executar backup agora"
        )

    def clear_audit_form(self) -> None:
        self.audit_full_summary.setPlainText("Selecione um log para ver os detalhes.")
        self.audit_form_status.setText("")
        self.audit_delete_button.setEnabled(False)

    def set_audit_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.audit_form_status, message, is_error)

    def set_audit_form_loading(self, is_loading: bool) -> None:
        has_record = bool(self.current_selected_record)
        self.audit_delete_button.setEnabled(not is_loading and has_record)
        self.audit_delete_button.setText("Excluindo..." if is_loading else "Excluir log")
