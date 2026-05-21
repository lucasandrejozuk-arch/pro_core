from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QFileDialog,
)


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
        if hasattr(self, "command_context_label"):
            self.command_context_label.setText(
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
        self.record_summary_panel.setVisible(module_key in self.searchable_module_keys)
        if hasattr(self, "command_editor_button"):
            self.command_editor_button.setEnabled(module_key in self.record_module_keys)
        if hasattr(self, "command_clear_selection_button"):
            self.command_clear_selection_button.setEnabled(module_key in self.record_module_keys)
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
            self._update_record_summary_panel()
            return

        row_index = selected_items[0].row()
        if row_index >= len(self.current_rows):
            return
        selected_row = self.current_rows[row_index]
        self.current_selected_record = dict(selected_row)
        self.current_selected_summary = self._format_selected_record_summary(selected_row)
        self._update_record_summary_panel()

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

    def _update_record_summary_panel(self) -> None:
        if hasattr(self, "record_summary_text"):
            self.record_summary_text.setPlainText(
                self.current_selected_summary or "Nenhum item selecionado."
            )

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
