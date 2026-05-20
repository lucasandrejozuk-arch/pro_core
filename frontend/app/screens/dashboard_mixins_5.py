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


class DashboardMixin5:
    def _set_active_module(self, module_key: str) -> None:
        previous_module_key = self.active_module_key
        self.active_module_key = module_key
        self.current_rows = []
        self.title_label.setText(self.module_labels.get(module_key, "Dashboard"))
        if hasattr(self, "data_description"):
            self.data_description.setText(self.module_descriptions.get(module_key, ""))
        if hasattr(self, "module_search_input"):
            self.module_search_input.setPlaceholderText(self._module_search_placeholder(module_key))
            if previous_module_key != module_key:
                self.module_search_input.blockSignals(True)
                self.module_search_input.clear()
                self.module_search_input.blockSignals(False)
        if hasattr(self, "session_module_label"):
            self.session_module_label.setText(
                self.module_labels.get(module_key, "Painel Principal")
            )
        self.setWindowTitle(
            f"{self.sidebar_title.text() or 'PRO CORE'} - {self.title_label.text()}"
        )
        self._mark_active_nav(module_key)
        self.dashboard_section_title.setVisible(module_key == "dashboard")
        self.dashboard_greeting_label.setVisible(module_key == "dashboard")
        self.dashboard_last_refresh_label.setVisible(module_key == "dashboard")
        self.dashboard_grid_widget.setVisible(module_key == "dashboard")
        self.dashboard_alerts_frame.setVisible(module_key == "dashboard")
        self.generic_record_container.setVisible(module_key in self.record_module_keys)
        self.data_title.setVisible(
            module_key not in {"dashboard", "equipment", "tools", "admin_area"}
        )
        self.data_description.setVisible(
            module_key not in {"dashboard", "equipment", "tools", "admin_area"}
        )
        self.module_search_input.setVisible(module_key in self.searchable_module_keys)
        self.table.setVisible(module_key in self.searchable_module_keys)
        self.customer_form_panel.setVisible(module_key == "customers")
        self.equipment_form_panel.setVisible(module_key == "equipment")
        self.tools_form_panel.setVisible(module_key == "tools")
        self.inventory_form_panel.setVisible(module_key == "inventory")
        self.service_order_form_panel.setVisible(module_key == "service_orders")
        self.sector_form_panel.setVisible(module_key == "sectors")
        self.user_form_panel.setVisible(module_key == "users")
        self.password_reset_form_panel.setVisible(module_key == "password_resets")
        self.settings_form_panel.setVisible(module_key == "settings")
        self.admin_area_panel.setVisible(module_key == "admin_area")
        self.audit_form_panel.setVisible(module_key == "audit_logs")
        self._sync_active_module_space(module_key)
        if module_key in self.record_module_keys:
            self._set_record_editor_open(False)
        else:
            self.generic_form_column.hide()
        if module_key == "customers":
            self.clear_customer_form()
        elif module_key == "equipment":
            self.clear_equipment_form()
        elif module_key == "inventory":
            self.clear_inventory_form()
        elif module_key == "service_orders":
            self.clear_service_order_form()
        elif module_key == "sectors":
            self.clear_sector_form()
        elif module_key == "users":
            self.clear_user_form()
        elif module_key == "password_resets":
            self.clear_password_reset_form()
        elif module_key == "settings":
            self.clear_settings_form()
        elif module_key == "admin_area":
            self._clear_current_selection()
        elif module_key == "audit_logs":
            self.clear_audit_form()
        self._position_record_editor()

    def _handle_table_selection(self) -> None:
        if self.active_module_key not in {
            "customers",
            "equipment",
            "inventory",
            "service_orders",
            "sectors",
            "users",
            "password_resets",
            "audit_logs",
        }:
            return

        selected_items = self.table.selectedItems()
        if not selected_items:
            self.current_selected_record = None
            self.current_selected_summary = "Nenhum item selecionado."
            return

        row_index = selected_items[0].row()
        if row_index >= len(self.current_rows):
            return
        selected_row = self.current_rows[row_index]
        self.current_selected_record = dict(selected_row)
        self.current_selected_summary = self._format_selected_record_summary(selected_row)

        if self.active_module_key == "customers":
            self._populate_customer_form(selected_row)
            return

        if self.active_module_key == "equipment":
            self._populate_equipment_form(selected_row)
            return

        if self.active_module_key == "inventory":
            self._populate_inventory_form(selected_row)
            return

        if self.active_module_key == "service_orders":
            self._populate_service_order_form(selected_row)
            return

        if self.active_module_key == "sectors":
            self._populate_sector_form(selected_row)
            return

        if self.active_module_key == "password_resets":
            self._populate_password_reset_form(selected_row)
            return

        if self.active_module_key == "audit_logs":
            self.audit_full_summary.setPlainText(self._format_audit_summary(selected_row))
            self.audit_delete_button.setEnabled(True)
            return

        self._populate_user_form(selected_row)

    def _populate_customer_form(self, customer: dict[str, Any]) -> None:
        self.selected_customer_id = str(customer["id"])
        self.selected_customer_document_path = None
        self.customer_name_input.setText(str(customer.get("name") or ""))
        self.customer_email_input.setText(str(customer.get("email") or ""))
        self.customer_phone_input.setText(str(customer.get("phone") or ""))
        self.customer_address_input.setText(str(customer.get("address") or ""))
        self.customer_notes_input.setText(str(customer.get("notes") or ""))
        self.customer_document_path_input.clear()
        self.customer_active_checkbox.setChecked(bool(customer.get("is_active", True)))
        self.customer_full_summary.setPlainText(self._format_customer_full_summary(customer))
        self.customer_delete_button.setEnabled(True)
        self.set_customer_form_status("Editando cliente selecionado.")

    def _request_customer_save(self) -> None:
        name = self.customer_name_input.text().strip()
        email = self.customer_email_input.text().strip().lower()
        phone = self.customer_phone_input.text().strip()
        if not name:
            self.set_customer_form_status("Informe o nome do cliente.", is_error=True)
            return

        if not email:
            self.set_customer_form_status("Informe o email do cliente.", is_error=True)
            return

        if not self._is_complete_phone(phone):
            self.set_customer_form_status(
                "Informe o telefone no formato (DD) 99999-9999.",
                is_error=True,
            )
            return

        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": self._optional_text(self.customer_address_input),
            "notes": self._optional_text(self.customer_notes_input),
            "is_active": self.customer_active_checkbox.isChecked(),
        }

        self.set_customer_form_status("")
        if self.selected_customer_id:
            self.customer_update_requested.emit(self.selected_customer_id, payload)
            return

        self.customer_create_requested.emit(payload)

    def _request_customer_delete(self) -> None:
        if not self.selected_customer_id:
            self.set_customer_form_status("Selecione um cliente.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir cliente",
            "Excluir o cliente selecionado?",
        ):
            return
        self.customer_delete_requested.emit(self.selected_customer_id)

    def _select_customer_document(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Selecionar anexo",
            "",
            "Arquivos (*.*)",
        )
        if not file_path:
            return

        self.selected_customer_document_path = file_path
        self.customer_document_path_input.setText(file_path)

    def _request_customer_document_upload(self) -> None:
        if not self.selected_customer_id:
            self.set_customer_form_status(
                "Salve ou selecione um cliente antes do anexo.", is_error=True
            )
            return

        file_path = self.selected_customer_document_path
        if not file_path:
            self.set_customer_form_status("Selecione um anexo.", is_error=True)
            return

        if not Path(file_path).exists():
            self.set_customer_form_status("Arquivo selecionado nao existe.", is_error=True)
            return

        self.customer_document_upload_requested.emit(self.selected_customer_id, "other", file_path)

    def _render_equipment_rows(self, title: str, rows: list[dict[str, Any]]) -> None:
        self._set_active_module("equipment")
        self.current_rows = rows
        self.data_title.setText(title)
        self.empty_label.hide()
        self.table.hide()
        self._refresh_equipment_table()
        if not rows:
            self.set_equipment_form_status("Nenhum equipamento cadastrado.")
        else:
            self.set_equipment_form_status("Equipamentos carregados.")

    def _populate_equipment_form(self, equipment: dict[str, Any]) -> None:
        self._select_equipment_by_id(str(equipment["id"]))

    def _refresh_equipment_table(self) -> None:
        term = self.equipment_search_input.text().strip().lower()
        self.equipment_visible_rows = [
            row
            for row in self.current_rows
            if self._row_matches(
                row,
                ("id", "category", "brand", "model", "special_number"),
                term,
            )
        ]
        self._fill_equipment_table(
            self.equipment_table,
            self.equipment_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("category")),
                lambda row: self._format_value(row.get("brand")),
                lambda row: self._format_value(row.get("model")),
                lambda row: self._format_value(row.get("special_number")),
            ],
        )
        if not self.equipment_visible_rows:
            self.selected_equipment_id = None
            self.equipment_full_summary.setPlainText(
                "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
            )
            self._refresh_equipment_boards_table()
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_table,
            self.equipment_visible_rows,
            self.selected_equipment_id,
        ):
            self.equipment_table.selectRow(0)

    def _refresh_equipment_boards_table(self) -> None:
        equipment = self._selected_equipment()
        boards = equipment.get("boards") if equipment else []
        term = self.board_search_input.text().strip().lower()
        self.equipment_board_visible_rows = [
            board
            for board in (boards or [])
            if self._row_matches(board, ("id", "name", "special_number", "model", "revision"), term)
        ]
        self._fill_equipment_table(
            self.equipment_boards_table,
            self.equipment_board_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("name")),
                lambda row: self._format_value(row.get("special_number")),
                lambda row: self._format_value(row.get("model")),
                lambda row: self._format_value(row.get("revision")),
            ],
        )
        if not self.equipment_board_visible_rows:
            self.selected_equipment_board_id = None
            self.selected_equipment_component_id = None
            self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
            self._refresh_equipment_components_table()
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_boards_table,
            self.equipment_board_visible_rows,
            self.selected_equipment_board_id,
        ):
            self.equipment_boards_table.selectRow(0)

    def _refresh_equipment_components_table(self) -> None:
        board = self._selected_equipment_board()
        components = board.get("components") if board else []
        term = self.component_search_input.text().strip().lower()
        self.equipment_component_visible_rows = [
            component
            for component in (components or [])
            if self._row_matches(
                component,
                ("id", "category", "name", "part_number", "location", "notes"),
                term,
            )
        ]
        self._fill_equipment_table(
            self.equipment_components_table,
            self.equipment_component_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("category")),
                lambda row: self._format_value(row.get("name")),
                lambda row: self._format_value(row.get("part_number")),
                lambda row: self._format_value(row.get("location")),
                lambda row: self._format_value(row.get("notes")),
            ],
        )
        if not self.equipment_component_visible_rows:
            self.selected_equipment_component_id = None
            self.component_full_summary.setPlainText(
                "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
            )
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_components_table,
            self.equipment_component_visible_rows,
            self.selected_equipment_component_id,
        ):
            self.equipment_components_table.selectRow(0)

    def _handle_equipment_table_selection(self) -> None:
        selected_items = self.equipment_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_visible_rows):
            return
        equipment = self.equipment_visible_rows[row_index]
        self.current_selected_record = dict(equipment)
        self.current_selected_summary = self._format_equipment_full_summary(equipment)
        self.selected_equipment_id = str(equipment["id"])
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.equipment_full_summary.setPlainText(self._format_equipment_full_summary(equipment))
        self.equipment_context_label.setText(
            f"_EQUIPAMENTO: {self._equipment_label(equipment).upper()}_"
        )
        self._refresh_equipment_boards_table()
        self._update_equipment_action_state()

    def _handle_equipment_board_table_selection(self) -> None:
        selected_items = self.equipment_boards_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_board_visible_rows):
            return
        board = self.equipment_board_visible_rows[row_index]
        self.current_selected_record = dict(board)
        self.current_selected_summary = self._format_equipment_board_summary(board)
        self.selected_equipment_board_id = str(board["id"])
        self.selected_equipment_component_id = None
        self.board_full_summary.setPlainText(self._format_equipment_board_summary(board))
        self.board_context_label.setText(f"_OBJETO: {self._board_label(board).upper()}_")
        self._refresh_equipment_components_table()
        self._update_equipment_action_state()

    def _handle_equipment_component_table_selection(self) -> None:
        selected_items = self.equipment_components_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_component_visible_rows):
            return
        component = self.equipment_component_visible_rows[row_index]
        self.current_selected_record = dict(component)
        self.current_selected_summary = self._format_equipment_component_summary(component)
        self.selected_equipment_component_id = str(component["id"])
        self.component_full_summary.setPlainText(
            self._format_equipment_component_summary(component)
        )
        self._update_equipment_action_state()

    def _open_equipment_create_dialog(self) -> None:
        dialog = EquipmentAssetDialog(
            "NOVO EQUIPAMENTO",
            self._equipment_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_create_requested.emit(dialog.payload())

    def _open_equipment_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR EQUIPAMENTO",
            self._equipment_dialog_fields(),
            equipment,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_update_requested.emit(str(equipment["id"]), dialog.payload())

    def _request_equipment_delete(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Remover equipamento",
            "Remover o equipamento selecionado?",
        ):
            return
        self.equipment_delete_requested.emit(str(equipment["id"]))

    def _request_equipment_import(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Importar Equipamentos - CSV",
            "",
            "CSV (*.csv)",
        )
        if not file_path:
            return
        answer = QMessageBox.question(
            self,
            "Importar Equipamentos",
            "Deseja substituir os equipamentos atuais? Escolha Nao para apenas adicionar.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return
        replace = answer == QMessageBox.StandardButton.Yes
        self.equipment_import_requested.emit(file_path, replace)

    def _request_equipment_export(self, export_format: str) -> None:
        extension = export_format.lower()
        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar Equipamentos",
            f"equipamentos.{extension}",
            f"{extension.upper()} (*.{extension})",
        )
        if not file_path:
            return
        if not file_path.lower().endswith(f".{extension}"):
            file_path = f"{file_path}.{extension}"
        self.equipment_export_requested.emit(export_format, file_path)

    def _request_equipment_defect_cases_open(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        self.equipment_defect_cases_requested.emit(str(equipment["id"]))

    def open_equipment_defect_cases_dialog(
        self,
        equipment_id: str,
        list_cases: Callable[[str], list[dict[str, Any]]],
        create_case: Callable[[dict[str, Any]], dict[str, Any]],
        update_case: Callable[[str, dict[str, Any]], dict[str, Any]],
        delete_case: Callable[[str], None],
    ) -> None:
        equipment = self._find_by_id(self.current_rows, equipment_id)
        if not equipment:
            self.set_equipment_form_status("Equipamento nao encontrado.", is_error=True)
            return
        dialog = EquipmentDefectCasesDialog(
            equipment,
            list_cases=list_cases,
            create_case=create_case,
            update_case=update_case,
            delete_case=delete_case,
            parent=self,
        )
        dialog.exec()
        self.equipment_form_status.setText("Casos de defeito atualizados.")

    def _request_equipment_board_create(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "NOVO OBJETO VINCULADO",
            self._board_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_board_create_requested.emit(str(equipment["id"]), dialog.payload())

    def _open_equipment_board_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment or not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR OBJETO VINCULADO",
            self._board_dialog_fields(),
            board,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_board_update_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            dialog.payload(),
        )

    def _request_equipment_board_delete(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment or not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Remover objeto",
            "Remover o objeto vinculado selecionado?",
        ):
            return
        self.equipment_board_delete_requested.emit(str(equipment["id"]), str(board["id"]))

    def _request_equipment_component_create(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        if not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "NOVO COMPONENTE",
            self._component_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_component_create_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            dialog.payload(),
        )

    def _open_equipment_component_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        if not equipment or not board or not component:
            self.set_equipment_form_status("Selecione um componente.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR COMPONENTE",
            self._component_dialog_fields(),
            component,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_component_update_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            str(component["id"]),
            dialog.payload(),
        )

    def _request_equipment_component_delete(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        if not equipment or not board or not component:
            self.set_equipment_form_status("Selecione um componente.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Remover componente",
            "Remover o componente selecionado?",
        ):
            return
        self.equipment_component_delete_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            str(component["id"]),
        )

    def _update_equipment_action_state(self) -> None:
        has_equipment = bool(self.selected_equipment_id)
        has_board = bool(self.selected_equipment_board_id)
        has_component = bool(self.selected_equipment_component_id)
        self.equipment_edit_button.setEnabled(has_equipment)
        self.equipment_remove_button.setEnabled(has_equipment)
        self.equipment_defect_cases_button.setEnabled(has_equipment)
        self.board_add_button.setEnabled(has_equipment)
        self.board_edit_button.setEnabled(has_board)
        self.board_remove_button.setEnabled(has_board)
        self.component_add_button.setEnabled(has_board)
        self.component_edit_button.setEnabled(has_component)
        self.component_remove_button.setEnabled(has_component)

    def _selected_equipment(self) -> dict[str, Any] | None:
        return self._find_by_id(self.current_rows, self.selected_equipment_id)

    def _selected_equipment_board(self) -> dict[str, Any] | None:
        equipment = self._selected_equipment()
        if not equipment:
            return None
        return self._find_by_id(equipment.get("boards") or [], self.selected_equipment_board_id)

    def _selected_equipment_component(self) -> dict[str, Any] | None:
        board = self._selected_equipment_board()
        if not board:
            return None
        return self._find_by_id(
            board.get("components") or [],
            self.selected_equipment_component_id,
        )

    def _select_equipment_by_id(self, equipment_id: str) -> None:
        self.selected_equipment_id = equipment_id
        self._select_visible_table_row(
            self.equipment_table,
            self.equipment_visible_rows,
            equipment_id,
        )

    def _fill_equipment_table(
        self,
        table: QTableWidget,
        rows: list[dict[str, Any]],
        getters: list,
    ) -> None:
        table.blockSignals(True)
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, getter in enumerate(getters):
                item = QTableWidgetItem(str(getter(row) or ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setData(Qt.ItemDataRole.UserRole, str(row.get("id") or ""))
                table.setItem(row_index, column_index, item)
        table.blockSignals(False)

    def _select_visible_table_row(
        self,
        table: QTableWidget,
        rows: list[dict[str, Any]],
        selected_id: str | None,
    ) -> bool:
        if not selected_id:
            return False
        for row_index, row in enumerate(rows):
            if str(row.get("id")) == selected_id:
                table.selectRow(row_index)
                return True
        return False

    @staticmethod
    def _find_by_id(rows: list[dict[str, Any]], row_id: str | None) -> dict[str, Any] | None:
        if not row_id:
            return None
        for row in rows:
            if str(row.get("id")) == row_id:
                return row
        return None

    @staticmethod
    def _row_matches(row: dict[str, Any], keys: tuple[str, ...], term: str) -> bool:
        if not term:
            return True
        return any(term in str(row.get(key) or "").lower() for key in keys)

    @staticmethod
    def _short_id(value: Any) -> str:
        text = str(value or "")
        return text[:8] if len(text) > 8 else text

    @staticmethod
    def _equipment_label(equipment: dict[str, Any]) -> str:
        return (
            " - ".join(
                part
                for part in [
                    str(equipment.get("category") or ""),
                    str(equipment.get("brand") or ""),
                    str(equipment.get("model") or ""),
                    str(equipment.get("special_number") or ""),
                ]
                if part
            )
            or "Equipamento sem descricao"
        )

    @staticmethod
    def _board_label(board: dict[str, Any]) -> str:
        return str(board.get("name") or board.get("model") or "Objeto vinculado")

    @staticmethod
    def _equipment_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "category",
                "label": "Tipo:",
                "placeholder": "Tipo do equipamento",
                "required": True,
            },
            {"key": "brand", "label": "Marca:", "placeholder": "Marca do equipamento"},
            {"key": "model", "label": "Modelo:", "placeholder": "Modelo do equipamento"},
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, S120-CU320",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 1499,90",
                "money": True,
            },
            {
                "key": "description",
                "label": "Notas:",
                "placeholder": "Observacoes gerais (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _board_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Nome:",
                "placeholder": "Nome do objeto vinculado",
                "required": True,
            },
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, numero de inventario",
            },
            {"key": "model", "label": "Modelo / Tipo:", "placeholder": "Modelo / tipo da placa"},
            {"key": "revision", "label": "Revisao:", "placeholder": "Ex.: A01, B02, Rev.C"},
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 980,00",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Notas:",
                "placeholder": "Observacoes (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _component_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Dados:",
                "placeholder": "Dados do componente",
                "required": True,
            },
            {"key": "category", "label": "Categoria:", "placeholder": "Categoria do componente"},
            {
                "key": "part_number",
                "label": "Modelo / Part Number:",
                "placeholder": "Ex.: BC547B, IRFZ44N",
            },
            {
                "key": "location",
                "label": "Localizacao:",
                "placeholder": "Ex.: Gaveta A3, Bandeja 2",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 12,50",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Observacoes:",
                "placeholder": "Observacoes",
                "multiline": True,
            },
        ]
