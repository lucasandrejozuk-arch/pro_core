from __future__ import annotations

from typing import Any


class DashboardFormStateCustomerInventoryMixin:
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
        self._set_customer_operational_status(
            "Novo cliente: preencha nome, email e telefone para liberar o cadastro.",
            "warning",
        )
        self._set_customer_document_status(
            "Anexos: salve ou selecione um cliente antes de enviar evidencias.",
            "warning",
        )
        self.customer_delete_button.setEnabled(False)
        self.customer_upload_document_button.setEnabled(False)
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
    def _set_customer_operational_status(self, message: str, level: str) -> None:
        self.customer_operational_status.setText(message)
        self.customer_operational_status.setProperty("level", level)
        self.customer_operational_status.style().unpolish(self.customer_operational_status)
        self.customer_operational_status.style().polish(self.customer_operational_status)
    def _set_customer_document_status(self, message: str, level: str) -> None:
        self.customer_document_status.setText(message)
        self.customer_document_status.setProperty("level", level)
        self.customer_document_status.style().unpolish(self.customer_document_status)
        self.customer_document_status.style().polish(self.customer_document_status)
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
            self.equipment_context_label.setText("Nenhum equipamento selecionado")
            self.board_context_label.setText("Nenhum objeto vinculado selecionado")
            self._set_equipment_list_count(self.equipment_table, 0)
            self._set_equipment_list_count(self.equipment_boards_table, 0)
            self._set_equipment_list_count(self.equipment_components_table, 0)
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
        self.selected_inventory_document_path = None
        self._select_inventory_stock_group("components")
        self.inventory_active_stock_group = self._current_inventory_stock_group()
        self._sync_inventory_categories()
        self._generate_inventory_sku()
        self.inventory_name_input.clear()
        if self.inventory_category_input.count() > 0:
            self.inventory_category_input.setCurrentIndex(0)
        self.inventory_quantity_input.setText("0")
        self.inventory_minimum_quantity_input.setText("0")
        self.inventory_location_input.clear()
        self.inventory_unit_cost_input.setText("0")
        self.inventory_notes_input.clear()
        self.inventory_document_path_input.clear()
        self.inventory_documents_summary.setPlainText("Nenhum anexo vinculado ao item.")
        self._render_inventory_document_buttons([])
        self._populate_inventory_dynamic_data(None)
        self.inventory_full_summary.setPlainText("Novo registro de estoque.")
        self._set_inventory_stock_status("Status: novo item.", "info")
        self._set_inventory_reorder_status(
            "Reposicao: informe quantidade, minimo e custo para calcular necessidade.",
            "warning",
        )
        self._set_inventory_wizard_step(0)
        self.inventory_form_status.setText("Novo item de estoque.")
        self.inventory_delete_button.setEnabled(False)
        self.table.clearSelection()
    def set_inventory_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.inventory_form_status, message, is_error)
    def set_inventory_form_loading(self, is_loading: bool) -> None:
        has_selection = bool(self.selected_inventory_item_id)
        self.inventory_save_button.setEnabled(not is_loading)
        self.inventory_new_button.setEnabled(not is_loading)
        self.inventory_back_button.setEnabled(not is_loading and self.inventory_wizard_step > 0)
        self.inventory_next_button.setEnabled(not is_loading and self.inventory_wizard_step < 2)
        self.inventory_delete_button.setEnabled(not is_loading and has_selection)
        self.inventory_attach_document_button.setEnabled(not is_loading)
        self.inventory_remove_document_button.setEnabled(not is_loading)
        self.inventory_save_button.setText("Salvando..." if is_loading else "Salvar")
    def _set_inventory_stock_status(self, message: str, level: str) -> None:
        self.inventory_stock_status.setText(message)
        self.inventory_stock_status.setProperty("level", level)
        self.inventory_stock_status.style().unpolish(self.inventory_stock_status)
        self.inventory_stock_status.style().polish(self.inventory_stock_status)
    def _set_inventory_reorder_status(self, message: str, level: str) -> None:
        self.inventory_reorder_status.setText(message)
        self.inventory_reorder_status.setProperty("level", level)
        self.inventory_reorder_status.style().unpolish(self.inventory_reorder_status)
        self.inventory_reorder_status.style().polish(self.inventory_reorder_status)
    def set_service_order_dependencies(
        self,
        customers: list[dict[str, Any]],
        equipment: list[dict[str, Any]],
        technicians: list[dict[str, Any]],
    ) -> None:
        current_customer_id = self.service_order_customer_combo.currentData()
        current_equipment_type = self.service_order_equipment_type_combo.currentData()
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
        self.service_order_equipment_type_combo.blockSignals(True)
        self.service_order_equipment_type_combo.clear()
        self.service_order_equipment_type_combo.addItem("Todos os tipos", "")
        equipment_types = sorted(
            {
                str(item.get("category") or "").strip()
                for item in equipment
                if str(item.get("category") or "").strip()
            }
        )
        for equipment_type in equipment_types:
            self.service_order_equipment_type_combo.addItem(equipment_type, equipment_type)
        self.service_order_equipment_type_combo.blockSignals(False)
        self.service_order_technician_combo.clear()
        self.service_order_technician_combo.addItem("Sem tecnico", "")
        for technician in technicians:
            self.service_order_technician_combo.addItem(
                str(technician.get("full_name") or technician.get("email") or "Tecnico"),
                str(technician["id"]),
            )
        if current_customer_id:
            self._select_combo_value(self.service_order_customer_combo, str(current_customer_id))
        if current_equipment_type:
            self._select_combo_value(
                self.service_order_equipment_type_combo,
                str(current_equipment_type),
            )
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
        self.service_order_custom_id_input.clear()
        if self.service_order_customer_combo.count() > 0:
            self.service_order_customer_combo.setCurrentIndex(0)
        if self.service_order_equipment_type_combo.count() > 0:
            self.service_order_equipment_type_combo.setCurrentIndex(0)
        if self.service_order_technician_combo.count() > 0:
            self.service_order_technician_combo.setCurrentIndex(0)
        if self.service_order_service_type_combo.count() > 0:
            self.service_order_service_type_combo.setCurrentIndex(0)
        if self.service_order_status_combo.count() > 0:
            self.service_order_status_combo.setCurrentIndex(0)
        if self.service_order_customer_approval_combo.count() > 0:
            self.service_order_customer_approval_combo.setCurrentIndex(0)
        self._refresh_service_order_equipment_combo()
        self._select_combo_value(self.service_order_priority_combo, "normal")
        self.service_order_entry_date_input.clear()
        self.service_order_budget_sent_at_input.clear()
        self.service_order_special_number_input.clear()
        self.service_order_serial_number_input.clear()
        self.service_order_sla_input.clear()
        self.service_order_problem_input.clear()
        self.service_order_diagnosis_input.clear()
        self.service_order_inspection_visual_input.clear()
        self.service_order_proposed_solution_input.clear()
        self.service_order_proposed_actions_input.clear()
        self.service_order_intake_checklist_input.clear()
        self.service_order_linked_objects_input.clear()
        self.service_order_parts_used_input.clear()
        self.service_order_workflow_history_input.clear()
        self.service_order_notes_input.clear()
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
        self.service_order_budget_summary.setText("Orçamento: nenhum item.")
        self.service_order_documents_summary.setText("Anexos: nenhum arquivo.")
        self.service_order_full_summary.setPlainText("Novo registro de ordem de serviço.")
        self._update_service_order_workflow(None)
        self._set_service_order_flow_buttons_enabled(False)
        self.service_order_form_status.setText("Nova ordem de serviço.")
        self.service_order_delete_button.setEnabled(False)
        self.table.clearSelection()
    def set_service_order_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.service_order_form_status, message, is_error)
    def set_service_order_form_loading(self, is_loading: bool) -> None:
        self.service_order_save_button.setEnabled(not is_loading)
        self.service_order_new_button.setEnabled(not is_loading)
        self.service_order_delete_button.setEnabled(
            not is_loading and self._can_delete_service_order()
        )
        if self.selected_service_order_id:
            self._set_service_order_flow_buttons_enabled(not is_loading)
        self.service_order_save_button.setText("Salvando..." if is_loading else "Salvar OS")
    def set_service_order_action_loading(self, is_loading: bool) -> None:
        self.service_order_save_button.setEnabled(not is_loading)
        self.service_order_new_button.setEnabled(not is_loading)
        self.service_order_delete_button.setEnabled(
            not is_loading and self._can_delete_service_order()
        )
        self._set_service_order_flow_buttons_enabled(
            not is_loading and bool(self.selected_service_order_id)
        )
    def _can_delete_service_order(self) -> bool:
        return bool(self.selected_service_order_id) and self.current_user_role in {
            "admin",
            "manager",
        }
    def _set_service_order_flow_buttons_enabled(
        self,
        enabled: bool,
        status: str | None = None,
    ) -> None:
        status_key = status
        if status_key is None and hasattr(self, "service_order_status_combo"):
            status_key = str(self.service_order_status_combo.currentData() or "")
        status_key = status_key or ""
        diagnosis_statuses = {"open", "assigned", "pending_tech", "diagnosis", "pending_quote"}
        budget_statuses = {
            "open",
            "assigned",
            "pending_tech",
            "diagnosis",
            "pending_quote",
            "quote_sent",
            "pending_approval",
        }
        approval_statuses = {"quote_sent", "pending_approval"}
        start_statuses = {"approved"}
        complete_statuses = {"in_progress", "ready_dispatch"}
        self.service_order_diagnosis_button.setEnabled(enabled and status_key in diagnosis_statuses)
        self.service_order_add_budget_button.setEnabled(enabled and status_key in budget_statuses)
        self.service_order_submit_quote_button.setEnabled(enabled and status_key in budget_statuses)
        self.service_order_approve_button.setEnabled(enabled and status_key in approval_statuses)
        self.service_order_reject_button.setEnabled(enabled and status_key in approval_statuses)
        self.service_order_start_button.setEnabled(enabled and status_key in start_statuses)
        self.service_order_complete_button.setEnabled(enabled and status_key in complete_statuses)
        self.service_order_select_document_button.setEnabled(enabled)
        self.service_order_upload_document_button.setEnabled(enabled)
