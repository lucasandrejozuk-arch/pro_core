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


class DashboardMixin6:
    def _populate_inventory_form(self, item: dict[str, Any]) -> None:
        self.selected_inventory_item_id = str(item["id"])
        self.inventory_sku_input.setText(str(item.get("sku") or ""))
        self.inventory_name_input.setText(str(item.get("name") or ""))
        self.inventory_category_input.setText(str(item.get("category") or ""))
        self.inventory_quantity_input.setText(str(item.get("quantity") or "0"))
        self.inventory_minimum_quantity_input.setText(str(item.get("minimum_quantity") or "0"))
        self.inventory_unit_cost_input.setText(str(item.get("unit_cost") or "0"))
        self.inventory_full_summary.setPlainText(self._format_inventory_full_summary(item))
        if self._inventory_is_low(item):
            self._set_inventory_stock_status(
                "Estoque critico: quantidade no minimo ou abaixo.", "error"
            )
        else:
            self._set_inventory_stock_status("Estoque em nivel operacional.", "info")
        self.inventory_delete_button.setEnabled(True)
        self.set_inventory_form_status("Editando item selecionado.")

    def _request_inventory_save(self) -> None:
        name = self.inventory_name_input.text().strip()
        if not name:
            self.set_inventory_form_status("Informe o nome do item.", is_error=True)
            return

        quantity = self._decimal_text(self.inventory_quantity_input, "Quantidade")
        minimum_quantity = self._decimal_text(
            self.inventory_minimum_quantity_input,
            "Quantidade minima",
        )
        unit_cost = self._decimal_text(self.inventory_unit_cost_input, "Custo unitario")
        if quantity is None or minimum_quantity is None or unit_cost is None:
            return

        payload = {
            "sku": self._optional_text(self.inventory_sku_input),
            "name": name,
            "category": self._optional_text(self.inventory_category_input),
            "quantity": quantity,
            "minimum_quantity": minimum_quantity,
            "unit_cost": unit_cost,
        }

        self.set_inventory_form_status("")
        if self.selected_inventory_item_id:
            self.inventory_update_requested.emit(self.selected_inventory_item_id, payload)
            return

        self.inventory_create_requested.emit(payload)

    def _request_inventory_delete(self) -> None:
        if not self.selected_inventory_item_id:
            self.set_inventory_form_status("Selecione um item.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir item",
            "Excluir o item de estoque selecionado?",
        ):
            return
        self.inventory_delete_requested.emit(self.selected_inventory_item_id)

    def _populate_service_order_form(self, service_order: dict[str, Any]) -> None:
        self.selected_service_order_id = str(service_order["id"])
        self._select_combo_value(
            self.service_order_customer_combo,
            str(service_order.get("customer_id") or ""),
        )
        self._refresh_service_order_equipment_combo()
        self._select_combo_value(
            self.service_order_equipment_combo,
            str(service_order.get("equipment_id") or ""),
        )
        self._select_combo_value(
            self.service_order_technician_combo,
            str(service_order.get("assigned_technician_id") or ""),
        )
        self._select_combo_value(
            self.service_order_priority_combo,
            str(service_order.get("priority") or "normal"),
        )
        self.service_order_sla_input.setText(str(service_order.get("sla_due_at") or ""))
        self.service_order_problem_input.setText(
            str(service_order.get("problem_description") or "")
        )
        self.service_order_diagnosis_input.setText(
            str(service_order.get("technical_diagnosis") or "")
        )
        self.service_order_rejection_input.setText(str(service_order.get("rejection_reason") or ""))
        self.service_order_budget_description_input.clear()
        self.service_order_budget_quantity_input.setText("1")
        self.service_order_budget_unit_price_input.setText("0")
        self.selected_service_order_document_path = None
        self.service_order_document_path_input.clear()
        self.service_order_current_status.setText(
            f"Status: {self._format_value(service_order.get('status'))}"
        )
        self._update_service_order_workflow(str(service_order.get("status") or ""))
        self.service_order_full_summary.setPlainText(
            self._format_service_order_full_summary(service_order)
        )
        self.service_order_budget_summary.setText(self._format_service_order_budget(service_order))
        self.service_order_documents_summary.setText(
            self._format_service_order_documents(service_order)
        )
        self._set_service_order_flow_buttons_enabled(True)
        self.service_order_delete_button.setEnabled(True)
        self.set_service_order_form_status("Editando ordem de servico selecionada.")

    def _request_service_order_save(self) -> None:
        customer_id = self.service_order_customer_combo.currentData()
        equipment_id = self.service_order_equipment_combo.currentData()
        technician_id = self.service_order_technician_combo.currentData()
        problem_description = self.service_order_problem_input.text().strip()

        if not customer_id:
            self.set_service_order_form_status("Selecione um cliente.", is_error=True)
            return

        if not equipment_id:
            self.set_service_order_form_status("Selecione um equipamento.", is_error=True)
            return

        if not problem_description:
            self.set_service_order_form_status("Informe o problema da OS.", is_error=True)
            return

        if self.selected_service_order_id:
            payload = {
                "assigned_technician_id": str(technician_id) if technician_id else None,
                "priority": str(self.service_order_priority_combo.currentData() or "normal"),
                "sla_due_at": self._optional_text(self.service_order_sla_input),
                "problem_description": problem_description,
                "technical_diagnosis": self._optional_text(self.service_order_diagnosis_input),
                "rejection_reason": self._optional_text(self.service_order_rejection_input),
            }
            self.service_order_update_requested.emit(self.selected_service_order_id, payload)
            return

        payload = {
            "customer_id": str(customer_id),
            "equipment_id": str(equipment_id),
            "assigned_technician_id": str(technician_id) if technician_id else None,
            "priority": str(self.service_order_priority_combo.currentData() or "normal"),
            "sla_due_at": self._optional_text(self.service_order_sla_input),
            "problem_description": problem_description,
        }
        self.service_order_create_requested.emit(payload)

    def _request_service_order_delete(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir OS",
            "Excluir a ordem de servico selecionada?",
        ):
            return
        self.service_order_delete_requested.emit(self.selected_service_order_id)

    def _request_service_order_diagnosis(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return

        diagnosis = self.service_order_diagnosis_input.text().strip()
        if not diagnosis:
            self.set_service_order_form_status("Informe o diagnostico tecnico.", is_error=True)
            return

        self.set_service_order_form_status("")
        self.service_order_diagnosis_requested.emit(self.selected_service_order_id, diagnosis)

    def _request_service_order_budget_item(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return

        description = self.service_order_budget_description_input.text().strip()
        if not description:
            self.set_service_order_form_status("Informe a descricao do item.", is_error=True)
            return

        quantity = self._decimal_text_for_service_order(
            self.service_order_budget_quantity_input,
            "Quantidade",
            allow_zero=False,
        )
        unit_price = self._decimal_text_for_service_order(
            self.service_order_budget_unit_price_input,
            "Valor unitario",
            allow_zero=True,
        )
        if quantity is None or unit_price is None:
            return

        payload = {
            "inventory_item_id": None,
            "item_type": str(self.service_order_budget_type_combo.currentData() or "service"),
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
        }
        self.set_service_order_form_status("")
        self.service_order_budget_item_requested.emit(self.selected_service_order_id, payload)

    def _request_service_order_submit_quote(self) -> None:
        if self._require_selected_service_order():
            self.service_order_submit_quote_requested.emit(self.selected_service_order_id)

    def _request_service_order_approve(self) -> None:
        if self._require_selected_service_order():
            self.service_order_approve_requested.emit(self.selected_service_order_id)

    def _request_service_order_reject(self) -> None:
        if not self._require_selected_service_order():
            return

        rejection_reason = self.service_order_rejection_input.text().strip()
        if not rejection_reason:
            self.set_service_order_form_status("Informe o motivo da reprovacao.", is_error=True)
            return

        self.service_order_reject_requested.emit(self.selected_service_order_id, rejection_reason)

    def _request_service_order_start(self) -> None:
        if self._require_selected_service_order():
            self.service_order_start_requested.emit(self.selected_service_order_id)

    def _request_service_order_complete(self) -> None:
        if self._require_selected_service_order():
            self.service_order_complete_requested.emit(self.selected_service_order_id)

    def _select_service_order_document(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Selecionar anexo",
            "",
            "Arquivos (*.*)",
        )
        if not file_path:
            return

        self.selected_service_order_document_path = file_path
        self.service_order_document_path_input.setText(file_path)

    def _request_service_order_document_upload(self) -> None:
        if not self._require_selected_service_order():
            return

        file_path = self.selected_service_order_document_path
        if not file_path:
            self.set_service_order_form_status("Selecione um arquivo.", is_error=True)
            return

        if not Path(file_path).exists():
            self.set_service_order_form_status("Arquivo selecionado nao existe.", is_error=True)
            return

        document_type = str(self.service_order_document_type_combo.currentData() or "other")
        self.set_service_order_form_status("")
        self.service_order_document_upload_requested.emit(
            self.selected_service_order_id,
            document_type,
            file_path,
        )

    def _require_selected_service_order(self) -> bool:
        if self.selected_service_order_id:
            self.set_service_order_form_status("")
            return True

        self.set_service_order_form_status("Selecione uma OS.", is_error=True)
        return False

    def _update_service_order_workflow(self, status: str | None) -> None:
        stage_by_status = {
            "open": 0,
            "assigned": 0,
            "pending_quote": 1,
            "quote_sent": 2,
            "pending_approval": 3,
            "approved": 3,
            "in_progress": 4,
            "completed": 5,
            "rejected": 5,
            "closed": 5,
        }
        current_stage = stage_by_status.get(status or "", 0)
        for index, label in enumerate(self.service_order_workflow_steps):
            if index < current_stage:
                stage = "done"
            elif index == current_stage:
                stage = "active"
            else:
                stage = "future"
            label.setProperty("stage", stage)
            label.style().unpolish(label)
            label.style().polish(label)

    def _populate_sector_form(self, sector: dict[str, Any]) -> None:
        self.selected_sector_id = str(sector["id"])
        self.sector_name_input.setText(str(sector.get("name") or ""))
        self.sector_description_input.setText(str(sector.get("description") or ""))
        is_admin = self.current_user_role == "admin"
        self.sector_new_button.setEnabled(is_admin)
        self.sector_save_button.setEnabled(is_admin)
        self.sector_name_input.setEnabled(is_admin)
        self.sector_description_input.setEnabled(is_admin)
        status_message = (
            "Editando setor selecionado." if is_admin else "Setor disponivel apenas para consulta."
        )
        self.sector_full_summary.setPlainText(self._format_sector_summary(sector))
        self.set_sector_form_status(status_message)

    def _request_sector_save(self) -> None:
        name = self.sector_name_input.text().strip()
        if not name:
            self.set_sector_form_status("Informe o nome do setor.", is_error=True)
            return

        payload = {
            "name": name,
            "description": self._optional_text(self.sector_description_input),
        }

        self.set_sector_form_status("")
        if self.selected_sector_id:
            self.sector_update_requested.emit(self.selected_sector_id, payload)
            return

        self.sector_create_requested.emit(payload)

    def _populate_user_form(self, user: dict[str, Any]) -> None:
        self.selected_user_id = str(user["id"])
        self.user_full_name_input.setText(str(user.get("full_name") or ""))
        self.user_email_input.setText(str(user.get("email") or ""))
        self._select_combo_value(self.user_role_combo, str(user.get("role") or "technician"))
        self._select_combo_value(self.user_sector_combo, str(user.get("sector_id") or ""))
        self.user_initial_password_input.clear()
        self.user_initial_password_input.setEnabled(False)
        self.user_active_checkbox.setChecked(bool(user.get("is_active", True)))
        self.user_reset_password_input.clear()
        self.user_reset_password_input.setEnabled(True)
        self.user_reset_password_button.setEnabled(True)
        self.user_full_summary.setPlainText(self._format_user_summary(user))
        self.set_user_form_status("Editando usuario selecionado.")

    def _request_user_save(self) -> None:
        full_name = self.user_full_name_input.text().strip()
        email = self.user_email_input.text().strip().lower()
        role = self.user_role_combo.currentData()
        sector_id = self.user_sector_combo.currentData()

        if not full_name:
            self.set_user_form_status("Informe o nome do usuario.", is_error=True)
            return

        if not email:
            self.set_user_form_status("Informe o email do usuario.", is_error=True)
            return

        if not role:
            self.set_user_form_status("Selecione o perfil do usuario.", is_error=True)
            return

        payload = {
            "full_name": full_name,
            "email": email,
            "role": str(role),
            "sector_id": str(sector_id) if sector_id else None,
            "is_active": self.user_active_checkbox.isChecked(),
        }

        self.set_user_form_status("")
        if self.selected_user_id:
            self.user_update_requested.emit(self.selected_user_id, payload)
            return

        password = self.user_initial_password_input.text()
        if not password:
            self.set_user_form_status("Informe a senha inicial.", is_error=True)
            return

        create_payload = payload.copy()
        create_payload.pop("is_active")
        create_payload["password"] = password
        self.user_create_requested.emit(create_payload)

    def _request_user_password_reset(self) -> None:
        if not self.selected_user_id:
            self.set_user_form_status("Selecione um usuario para redefinir a senha.", is_error=True)
            return

        new_password = self.user_reset_password_input.text()
        if not new_password:
            self.set_user_form_status("Informe a nova senha.", is_error=True)
            return

        self.set_user_form_status("")
        self.user_password_reset_requested.emit(self.selected_user_id, new_password)

    def _populate_password_reset_form(self, request: dict[str, Any]) -> None:
        self.selected_password_reset_request_id = str(request["id"])
        full_name = self._format_value(request.get("requester_full_name"))
        email = self._format_value(request.get("requester_email"))
        role = self._format_value(request.get("requester_role"))
        created_at = self._format_value(request.get("created_at"))
        self.password_reset_requester_label.setText(
            f"Solicitante: {full_name} | {email} | Perfil: {role} | Criada em: {created_at}"
        )
        self.password_reset_new_password_input.clear()
        self.password_reset_resolve_button.setEnabled(True)
        self.password_reset_full_summary.setPlainText(self._format_password_reset_summary(request))
        self.set_password_reset_form_status("Informe uma nova senha temporaria.")

    def _request_password_reset_resolve(self) -> None:
        if not self.selected_password_reset_request_id:
            self.set_password_reset_form_status(
                "Selecione uma solicitacao.",
                is_error=True,
            )
            return

        new_password = self.password_reset_new_password_input.text()
        if not new_password:
            self.set_password_reset_form_status("Informe a nova senha.", is_error=True)
            return

        self.set_password_reset_form_status("")
        self.password_reset_resolve_requested.emit(
            self.selected_password_reset_request_id,
            new_password,
        )

    def _populate_financial_form(self, record: dict[str, Any]) -> None:
        self.selected_financial_record_id = str(record["id"])
        self._select_combo_value(
            self.financial_type_combo,
            str(record.get("record_type") or "receivable"),
        )
        self.financial_description_input.setText(str(record.get("description") or ""))
        self.financial_amount_input.setText(str(record.get("amount") or ""))
        self.financial_due_date_input.setText(str(record.get("due_date") or ""))
        self.financial_notes_input.setText(str(record.get("notes") or ""))
        self.financial_full_summary.setPlainText(self._format_financial_summary(record))
        self.financial_paid_button.setEnabled(str(record.get("status") or "") == "open")
        self.financial_cancel_button.setEnabled(str(record.get("status") or "") == "open")
        self.financial_delete_button.setEnabled(True)
        self.set_financial_form_status("Editando lancamento selecionado.")

    def _request_financial_save(self) -> None:
        description = self.financial_description_input.text().strip()
        if not description:
            self.set_financial_form_status("Informe a descricao.", is_error=True)
            return

        amount = self.financial_amount_input.text().strip().replace(",", ".")
        try:
            if float(amount) <= 0:
                raise ValueError
        except ValueError:
            self.set_financial_form_status("Valor deve ser maior que zero.", is_error=True)
            return

        payload = {
            "record_type": str(self.financial_type_combo.currentData() or "receivable"),
            "description": description,
            "amount": amount,
            "due_date": self._optional_text(self.financial_due_date_input),
            "notes": self._optional_text(self.financial_notes_input),
        }
        self.set_financial_form_status("")
        self.financial_create_requested.emit(payload)

    def _request_financial_mark_paid(self) -> None:
        if not self.selected_financial_record_id:
            self.set_financial_form_status("Selecione um lancamento.", is_error=True)
            return
        self.financial_mark_paid_requested.emit(self.selected_financial_record_id)

    def _request_financial_cancel(self) -> None:
        if not self.selected_financial_record_id:
            self.set_financial_form_status("Selecione um lancamento.", is_error=True)
            return
        self.financial_cancel_requested.emit(self.selected_financial_record_id)

    def _request_financial_delete(self) -> None:
        if not self.selected_financial_record_id:
            self.set_financial_form_status("Selecione um lancamento.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir lancamento",
            "Excluir o lancamento financeiro selecionado?",
        ):
            return
        self.financial_delete_requested.emit(self.selected_financial_record_id)

    def _populate_settings_form(self, settings: dict[str, Any]) -> None:
        self.current_settings = dict(settings)
        self.settings_company_name_input.setText(str(settings.get("company_name") or ""))
        self.settings_trade_name_input.setText(str(settings.get("trade_name") or ""))
        self.settings_document_input.setText(str(settings.get("document_number") or ""))
        self.settings_email_input.setText(str(settings.get("email") or ""))
        self.settings_phone_input.setText(str(settings.get("phone") or ""))
        self.settings_brand_name_input.setText(str(settings.get("brand_name") or ""))
        self.settings_brand_subtitle_input.setText(str(settings.get("brand_subtitle") or ""))
        self._select_combo_value(
            self.settings_color_palette_combo,
            str(settings.get("color_palette") or DEFAULT_COLOR_PALETTE),
        )
        self._select_combo_value(self.settings_theme_combo, str(settings.get("theme") or "light"))
        self.settings_backup_enabled_checkbox.setChecked(bool(settings.get("backup_enabled", True)))
        self.settings_backup_interval_input.setText(
            str(settings.get("backup_interval_hours") or "24")
        )
        self.settings_backup_path_input.setText(
            str(settings.get("backup_storage_path") or "backups")
        )
        last_run = settings.get("backup_last_run_at")
        self.settings_backup_last_run_label.setText(
            f"Ultimo backup: {last_run}" if last_run else "Ultimo backup: nunca"
        )
        self.settings_full_summary.setPlainText(self._format_settings_summary(settings))
        self.apply_branding(settings)
        self.set_settings_form_status("Configuracoes carregadas.")

    def configure_ui_scale(self, minimum: float, maximum: float, current: float) -> None:
        self.ui_scale_min = minimum
        self.ui_scale_max = maximum
        self.ui_scale_value = current
        self.settings_ui_scale_slider.blockSignals(True)
        self.settings_ui_scale_slider.setMinimum(round(minimum * 100))
        self.settings_ui_scale_slider.setMaximum(round(maximum * 100))
        self.settings_ui_scale_slider.setValue(round(current * 100))
        self.settings_ui_scale_slider.blockSignals(False)
        self.settings_ui_scale_label.setText(f"{round(current * 100)}%")

    def _handle_ui_scale_slider_changed(self, value: int) -> None:
        self.ui_scale_value = value / 100
        self.settings_ui_scale_label.setText(f"{value}%")
        self.ui_scale_changed.emit(self.ui_scale_value)

    def _request_settings_save(self) -> None:
        company_name = self.settings_company_name_input.text().strip()
        if not company_name:
            self.set_settings_form_status("Informe o nome da empresa.", is_error=True)
            return

        interval_text = self.settings_backup_interval_input.text().strip()
        try:
            backup_interval_hours = int(interval_text)
        except ValueError:
            self.set_settings_form_status("Intervalo de backup deve ser inteiro.", is_error=True)
            return

        if backup_interval_hours < 1 or backup_interval_hours > 720:
            self.set_settings_form_status(
                "Intervalo de backup deve ficar entre 1 e 720 horas.",
                is_error=True,
            )
            return

        backup_storage_path = self.settings_backup_path_input.text().strip()
        if not backup_storage_path:
            self.set_settings_form_status("Informe a pasta de backup.", is_error=True)
            return

        payload = {
            "company_name": company_name,
            "trade_name": self._optional_text(self.settings_trade_name_input),
            "document_number": self._optional_text(self.settings_document_input),
            "email": self._optional_text(self.settings_email_input),
            "phone": self._optional_text(self.settings_phone_input),
            "brand_name": self._optional_text(self.settings_brand_name_input),
            "brand_subtitle": self._optional_text(self.settings_brand_subtitle_input),
            "color_palette": str(
                self.settings_color_palette_combo.currentData() or DEFAULT_COLOR_PALETTE
            ),
            "theme": str(self.settings_theme_combo.currentData() or "light"),
            "backup_enabled": self.settings_backup_enabled_checkbox.isChecked(),
            "backup_interval_hours": backup_interval_hours,
            "backup_storage_path": backup_storage_path,
        }
        self.set_settings_form_status("")
        self.settings_update_requested.emit(payload)

    def _request_report_view(self) -> None:
        module_key = str(self.report_module_combo.currentData() or "service_orders")
        self.current_report_module_key = module_key
        self.set_report_status("")
        self.report_view_requested.emit(module_key)

    def _request_report_export(self, report_format: str) -> None:
        module_key = str(self.report_module_combo.currentData() or self.current_report_module_key)
        extension = report_format.lower()
        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio",
            f"{module_key}.{extension}",
            f"{extension.upper()} (*.{extension})",
        )
        if not file_path:
            return

        if not file_path.lower().endswith(f".{extension}"):
            file_path = f"{file_path}.{extension}"

        self.current_report_module_key = module_key
        self.set_report_status("")
        self.report_export_requested.emit(module_key, report_format, file_path)

    def _refresh_service_order_equipment_combo(self) -> None:
        if not hasattr(self, "service_order_equipment_combo"):
            return

        current_equipment_id = self.service_order_equipment_combo.currentData()
        self.service_order_equipment_combo.clear()

        for equipment in self.service_order_equipment:
            label = " - ".join(
                part
                for part in [
                    str(equipment.get("category") or ""),
                    str(equipment.get("brand") or ""),
                    str(equipment.get("model") or ""),
                    str(equipment.get("special_number") or ""),
                    str(equipment.get("serial_number") or ""),
                ]
                if part
            )
            self.service_order_equipment_combo.addItem(
                label or "Equipamento sem descricao", str(equipment["id"])
            )

        if current_equipment_id:
            self._select_combo_value(self.service_order_equipment_combo, str(current_equipment_id))

    @staticmethod
    def _format_value(value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, bool):
            return "Sim" if value else "Nao"

        labels = {
            "open": "Aberta",
            "assigned": "Atribuida",
            "pending_quote": "Pendente de orcamento",
            "quote_sent": "Orcamento enviado",
            "pending_approval": "Pendente de aprovacao",
            "approved": "Aprovada",
            "in_progress": "Em execucao",
            "completed": "Concluida",
            "rejected": "Reprovada",
            "closed": "Encerrada",
            "admin": "Administrador",
            "manager": "Gestor/Lider",
            "technician": "Tecnico",
            "customer": "Cliente",
            "pending": "Pendente",
            "resolved": "Resolvida",
            "service": "Servico",
            "part": "Peca",
            "other": "Outro",
            "light": "Claro",
            "dark": "Escuro",
            "low": "Baixa",
            "normal": "Normal",
            "high": "Alta",
            "urgent": "Urgente",
            "receivable": "A receber",
            "payable": "A pagar",
            "paid": "Pago",
            "canceled": "Cancelado",
            "overdue": "Vencido",
            "email": "Email",
            "whatsapp": "WhatsApp",
            "system": "Sistema",
            "sent": "Enviada",
            "failed": "Falhou",
            "service_orders": "Ordens de Servico",
            "customers": "Clientes",
            "equipment": "Equipamentos",
            "inventory": "Estoque",
            "users": "Usuarios",
            "financial": "Financeiro",
            "audit_logs": "Logs/Auditoria",
        }
        if isinstance(value, str) and value in labels:
            return labels[value]

        return str(value)

    def _format_service_order_budget(self, service_order: dict[str, Any]) -> str:
        items = service_order.get("budget_items") or []
        total = self._format_value(service_order.get("quoted_total"))
        if not items:
            return f"Orcamento: nenhum item. Total: {total or '0'}"

        descriptions = []
        for item in items[:4]:
            item_type = self._format_value(item.get("item_type"))
            quantity = self._format_value(item.get("quantity"))
            unit_price = self._format_value(item.get("unit_price"))
            description = self._format_value(item.get("description"))
            descriptions.append(f"{item_type}: {description} ({quantity} x {unit_price})")

        remaining = len(items) - len(descriptions)
        suffix = f" + {remaining} item(ns)" if remaining > 0 else ""
        return f"Orcamento: {'; '.join(descriptions)}{suffix}. Total: {total}"

    def _format_service_order_documents(self, service_order: dict[str, Any]) -> str:
        documents = service_order.get("documents") or []
        if not documents:
            return "Anexos: nenhum arquivo."

        descriptions = []
        for document in documents[:4]:
            document_type = self._format_value(document.get("document_type"))
            file_name = self._format_value(document.get("file_name"))
            descriptions.append(f"{document_type}: {file_name}")

        remaining = len(documents) - len(descriptions)
        suffix = f" + {remaining} arquivo(s)" if remaining > 0 else ""
        return f"Anexos: {'; '.join(descriptions)}{suffix}."

    def _format_selected_record_summary(self, record: dict[str, Any]) -> str:
        formatters = {
            "customers": self._format_customer_full_summary,
            "equipment": self._format_equipment_full_summary,
            "inventory": self._format_inventory_full_summary,
            "service_orders": self._format_service_order_full_summary,
            "sectors": self._format_sector_summary,
            "users": self._format_user_summary,
            "password_resets": self._format_password_reset_summary,
            "financial": self._format_financial_summary,
            "audit_logs": self._format_audit_summary,
            "notifications": self._format_notification_summary,
        }
        formatter = formatters.get(self.active_module_key)
        if formatter is not None:
            return formatter(record)
        lines = []
        for key, value in record.items():
            lines.append(f"{key}: {self._format_value(value) or '-'}")
        return "\n".join(lines) or "Nenhum item selecionado."

    def _format_service_order_full_summary(self, service_order: dict[str, Any]) -> str:
        customer_name = self._lookup_label(
            self.service_order_customers,
            service_order.get("customer_id"),
            "name",
            "Cliente nao identificado",
        )
        technician_name = self._lookup_label(
            self.service_order_technicians,
            service_order.get("assigned_technician_id"),
            "full_name",
            "Sem tecnico",
        )
        equipment_label = self._lookup_equipment_label(service_order.get("equipment_id"))
        lines = [
            f"Codigo: {self._format_value(service_order.get('code')) or '-'}",
            f"Status: {self._format_value(service_order.get('status'))}",
            f"Prioridade: {self._format_value(service_order.get('priority')) or 'Normal'}",
            f"Prazo SLA: {self._format_value(service_order.get('sla_due_at')) or '-'}",
            f"Cliente: {customer_name}",
            f"Equipamento: {equipment_label}",
            f"Tecnico: {technician_name}",
            f"Problema informado: {self._format_value(service_order.get('problem_description'))}",
            f"Diagnostico: {self._format_value(service_order.get('technical_diagnosis')) or '-'}",
            f"Total orcado: {self._format_value(service_order.get('quoted_total')) or '0'}",
            f"Criada em: {self._format_value(service_order.get('created_at'))}",
        ]
        return "\n".join(lines)

    def _format_customer_full_summary(self, customer: dict[str, Any]) -> str:
        active = "Sim" if customer.get("is_active", True) else "Nao"
        lines = [
            f"Nome: {self._format_value(customer.get('name')) or '-'}",
            f"Email: {self._format_value(customer.get('email')) or '-'}",
            f"Telefone: {self._format_value(customer.get('phone')) or '-'}",
            f"Endereco: {self._format_value(customer.get('address')) or '-'}",
            f"Ativo: {active}",
            f"Observacoes: {self._format_value(customer.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_full_summary(self, equipment: dict[str, Any]) -> str:
        boards = equipment.get("boards") or []
        components_count = sum(len(board.get("components") or []) for board in boards)
        lines = [
            f"ID: {self._format_value(equipment.get('id')) or '-'}",
            f"Tipo: {self._format_value(equipment.get('category')) or '-'}",
            f"Marca: {self._format_value(equipment.get('brand')) or '-'}",
            f"Modelo: {self._format_value(equipment.get('model')) or '-'}",
            f"N especial: {self._format_value(equipment.get('special_number')) or '-'}",
            f"Serie: {self._format_value(equipment.get('serial_number')) or '-'}",
            f"Valor unitario: R$ {self._format_value(equipment.get('unit_price')) or '0'}",
            f"Placas vinculadas: {len(boards)}",
            f"Componentes cadastrados: {components_count}",
            f"Notas: {self._format_value(equipment.get('description')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_board_summary(self, board: dict[str, Any]) -> str:
        components = board.get("components") or []
        lines = [
            f"ID: {self._format_value(board.get('id')) or '-'}",
            f"Nome: {self._format_value(board.get('name')) or '-'}",
            f"N especial: {self._format_value(board.get('special_number')) or '-'}",
            f"Serie: {self._format_value(board.get('serial_number')) or '-'}",
            f"Modelo / Tipo: {self._format_value(board.get('model')) or '-'}",
            f"Revisao: {self._format_value(board.get('revision')) or '-'}",
            f"Valor unitario: R$ {self._format_value(board.get('unit_price')) or '0'}",
            f"Componentes vinculados: {len(components)}",
            f"Notas: {self._format_value(board.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_component_summary(self, component: dict[str, Any]) -> str:
        lines = [
            f"ID: {self._format_value(component.get('id')) or '-'}",
            f"Dados: {self._format_value(component.get('name')) or '-'}",
            f"Categoria: {self._format_value(component.get('category')) or '-'}",
            f"Modelo / Part Number: {self._format_value(component.get('part_number')) or '-'}",
            f"Localizacao: {self._format_value(component.get('location')) or '-'}",
            f"Quantidade: {self._format_value(component.get('quantity')) or '-'}",
            f"Valor unitario: R$ {self._format_value(component.get('unit_price')) or '0'}",
            f"Observacoes: {self._format_value(component.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

