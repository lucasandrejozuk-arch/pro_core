from __future__ import annotations

from typing import Any

from frontend.app.themes.styles import DEFAULT_COLOR_PALETTE


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardFormStateMixin:
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
        self._set_inventory_reorder_status(
            "Reposicao: informe quantidade, minimo e custo para calcular necessidade.",
            "warning",
        )
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
        self._refresh_sector_operational_status()
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

    def _set_sector_operational_status(self, message: str, level: str) -> None:
        self.sector_operational_status.setText(message)
        self.sector_operational_status.setProperty("level", level)
        self.sector_operational_status.style().unpolish(self.sector_operational_status)
        self.sector_operational_status.style().polish(self.sector_operational_status)

    def _refresh_sector_operational_status(self, sector: dict[str, Any] | None = None) -> None:
        is_admin = self.current_user_role == "admin"
        action_scope = (
            "Admin: pode criar, editar e excluir setores."
            if is_admin
            else "Consulta: alteracoes de setor ficam restritas ao administrador."
        )
        self.sector_scope_status.setText(action_scope)

        if sector is not None:
            sector_name = str(sector.get("name") or "Setor sem nome")
            action = "edicao liberada" if is_admin else "consulta liberada"
            level = "info" if is_admin else "warning"
            self._set_sector_operational_status(
                f"Setor selecionado: {sector_name}. {action}.", level
            )
            return

        sector_count = len(self.all_rows) if self.active_module_key == "sectors" else 0
        if sector_count:
            action = "selecione um setor para editar" if is_admin else "selecione para consultar"
            level = "info" if is_admin else "warning"
            self._set_sector_operational_status(
                f"{sector_count} setor(es) cadastrado(s); {action}.", level
            )
            return

        message = (
            "Nenhum setor cadastrado. Crie a estrutura inicial para orientar usuarios e rotinas."
            if is_admin
            else "Nenhum setor disponivel para consulta no momento."
        )
        self._set_sector_operational_status(message, "warning")

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
        self._refresh_user_operational_status()
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

    def _set_user_operational_status(self, message: str, level: str) -> None:
        self.user_operational_status.setText(message)
        self.user_operational_status.setProperty("level", level)
        self.user_operational_status.style().unpolish(self.user_operational_status)
        self.user_operational_status.style().polish(self.user_operational_status)

    def _refresh_user_operational_status(self, user: dict[str, Any] | None = None) -> None:
        if user is not None:
            full_name = str(user.get("full_name") or "Usuario sem nome")
            role = self._user_role_label(user.get("role"))
            sector = self._lookup_label(
                self.user_sectors,
                user.get("sector_id"),
                "name",
                "Sem setor",
            )
            is_active = bool(user.get("is_active", True))
            level = "info" if is_active else "warning"
            status = "ativo" if is_active else "inativo"
            self._set_user_operational_status(
                f"Usuario selecionado: {full_name} | {role} | {sector} | {status}.",
                level,
            )
            security_message = (
                "Seguranca: senha inicial bloqueada; use redefinicao manual se necessario."
            )
            if user.get("must_change_password", False):
                security_message += " Troca de senha pendente no proximo acesso."
            self.user_security_status.setText(security_message)
            return

        user_count = len(self.all_rows) if self.active_module_key == "users" else 0
        if user_count:
            self._set_user_operational_status(
                f"{user_count} usuario(s) carregado(s); selecione uma conta para revisar acesso.",
                "info",
            )
        else:
            self._set_user_operational_status(
                "Nenhum usuario carregado. Cadastre uma conta com perfil, setor e senha inicial.",
                "warning",
            )
        self.user_security_status.setText(
            "Seguranca: senha inicial obrigatoria para novas contas; "
            "redefinicao exige usuario selecionado."
        )

    def _user_role_label(self, role: Any) -> str:
        role_key = str(role or "")
        for index in range(self.user_role_combo.count()):
            if self.user_role_combo.itemData(index) == role_key:
                return self.user_role_combo.itemText(index)
        return role_key or "Perfil nao informado"

    def clear_password_reset_form(self) -> None:
        self.selected_password_reset_request_id = None
        self.selected_password_reset_status = None
        self.password_reset_requester_label.setText("Selecione uma solicitacao.")
        self.password_reset_new_password_input.clear()
        self.password_reset_resolve_button.setEnabled(False)
        self.password_reset_full_summary.setPlainText("Nenhuma solicitacao selecionada.")
        self.password_reset_form_status.setText("")
        self._refresh_password_reset_operational_status()
        self.table.clearSelection()

    def set_password_reset_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.password_reset_form_status, message, is_error)

    def set_password_reset_form_loading(self, is_loading: bool) -> None:
        self.password_reset_resolve_button.setEnabled(
            not is_loading and self._password_reset_can_resolve()
        )
        self.password_reset_resolve_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )

    def _set_password_reset_operational_status(self, message: str, level: str) -> None:
        self.password_reset_operational_status.setText(message)
        self.password_reset_operational_status.setProperty("level", level)
        self.password_reset_operational_status.style().unpolish(
            self.password_reset_operational_status
        )
        self.password_reset_operational_status.style().polish(
            self.password_reset_operational_status
        )

    def _refresh_password_reset_operational_status(
        self, request: dict[str, Any] | None = None
    ) -> None:
        if request is not None:
            requester = str(
                request.get("requester_full_name")
                or request.get("requester_email")
                or "-"
            )
            status_key = self._password_reset_status_key(request.get("status"))
            status_label = self._password_reset_status_label(status_key)
            level = "warning" if status_key == "pending" else "info"
            self._set_password_reset_operational_status(
                f"Solicitacao selecionada: {requester} | Status: {status_label}.",
                level,
            )
            if status_key == "pending":
                self.password_reset_security_status.setText(
                    "Seguranca: informe uma senha temporaria com pelo menos 8 caracteres."
                )
            else:
                self.password_reset_security_status.setText(
                    "Seguranca: solicitacao ja resolvida; acao de redefinicao bloqueada."
                )
            return

        request_count = len(self.all_rows) if self.active_module_key == "password_resets" else 0
        pending_count = sum(
            1
            for row in self.all_rows
            if self._password_reset_status_key(row.get("status")) == "pending"
        )
        if request_count:
            self._set_password_reset_operational_status(
                f"{request_count} solicitacao(oes) carregada(s); {pending_count} pendente(s).",
                "warning" if pending_count else "info",
            )
        else:
            self._set_password_reset_operational_status(
                "Nenhuma solicitacao de senha carregada para atendimento.",
                "warning",
            )
        self.password_reset_security_status.setText(
            "Seguranca: selecione uma solicitacao pendente para definir senha temporaria."
        )

    def _password_reset_can_resolve(self) -> bool:
        return bool(self.selected_password_reset_request_id) and (
            self.selected_password_reset_status == "pending"
        )

    def _password_reset_status_key(self, status: Any) -> str:
        return str(status or "pending").strip().lower()

    def _password_reset_status_label(self, status: Any) -> str:
        status_key = self._password_reset_status_key(status)
        return {
            "pending": "Pendente",
            "resolved": "Resolvida",
            "completed": "Resolvida",
            "cancelled": "Cancelada",
        }.get(status_key, self._format_value(status_key) or "Pendente")

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
        if self.settings_language_combo.count() > 0:
            self._select_combo_value(self.settings_language_combo, "pt-BR")
        self.settings_backup_enabled_checkbox.setChecked(True)
        self.settings_backup_interval_input.setText("24")
        self.settings_backup_path_input.setText("backups")
        self.settings_backup_last_run_label.setText("Ultimo backup: nunca")
        self.settings_full_summary.setPlainText("Configuracoes ainda nao carregadas.")
        self.settings_form_status.setText("")
        self._refresh_settings_operational_status()

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

    def _set_settings_operational_status(self, message: str, level: str) -> None:
        self.settings_operational_status.setText(message)
        self.settings_operational_status.setProperty("level", level)
        self.settings_operational_status.style().unpolish(self.settings_operational_status)
        self.settings_operational_status.style().polish(self.settings_operational_status)

    def _refresh_settings_operational_status(
        self, settings: dict[str, Any] | None = None
    ) -> None:
        active_settings = settings if settings is not None else self.current_settings
        if not active_settings:
            self._set_settings_operational_status(
                "Configuracoes ainda nao carregadas. Revise empresa, aparencia e backup.",
                "warning",
            )
            self.settings_backup_status.setText(
                "Backup: informe intervalo e destino antes de salvar."
            )
            return

        company_name = self._format_value(active_settings.get("company_name")) or "-"
        brand_name = self._format_value(active_settings.get("brand_name")) or company_name
        theme = self._format_value(active_settings.get("theme")) or "light"
        scale = round(self.ui_scale_value * 100)
        self._set_settings_operational_status(
            f"Identidade: {brand_name} | Empresa: {company_name} | "
            f"Tema: {theme} | Escala: {scale}%.",
            "info",
        )

        backup_enabled = bool(active_settings.get("backup_enabled", True))
        interval = active_settings.get("backup_interval_hours") or 24
        destination = self._format_value(active_settings.get("backup_storage_path")) or "backups"
        last_run = self._format_value(active_settings.get("backup_last_run_at")) or "nunca"
        backup_state = "ativo" if backup_enabled else "inativo"
        self.settings_backup_status.setText(
            f"Backup: {backup_state} | intervalo {interval}h | "
            f"destino {destination} | ultimo {last_run}."
        )

    def clear_audit_form(self) -> None:
        self.audit_full_summary.setPlainText("Selecione um log para ver os detalhes.")
        self.audit_form_status.setText("")
        self.audit_delete_button.setEnabled(False)
        self._refresh_audit_operational_status()

    def set_audit_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.audit_form_status, message, is_error)

    def set_audit_form_loading(self, is_loading: bool) -> None:
        has_record = bool(self.current_selected_record)
        self.audit_delete_button.setEnabled(not is_loading and has_record)
        self.audit_delete_button.setText("Excluindo..." if is_loading else "Excluir log")

    def _set_audit_operational_status(self, message: str, level: str) -> None:
        self.audit_operational_status.setText(message)
        self.audit_operational_status.setProperty("level", level)
        self.audit_operational_status.style().unpolish(self.audit_operational_status)
        self.audit_operational_status.style().polish(self.audit_operational_status)

    def _refresh_audit_operational_status(self, record: dict[str, Any] | None = None) -> None:
        if record is not None:
            action = self._format_value(record.get("action")) or "-"
            entity = self._format_value(record.get("entity_type")) or "-"
            actor = (
                self._format_value(record.get("actor_user_id"))
                or self._format_value(record.get("actor_type"))
                or "-"
            )
            level = "warning" if self._audit_action_is_sensitive(action) else "info"
            self._set_audit_operational_status(
                f"Evento selecionado: {action} | {entity} | Ator: {actor}.",
                level,
            )
            self.audit_retention_status.setText(
                "Retencao: exclusao de log deve ser usada apenas para correcao administrativa."
            )
            return

        log_count = len(self.all_rows) if self.active_module_key == "audit_logs" else 0
        sensitive_count = sum(
            1
            for row in self.all_rows
            if self._audit_action_is_sensitive(str(row.get("action") or ""))
        )
        if log_count:
            self._set_audit_operational_status(
                f"{log_count} log(s) carregado(s); {sensitive_count} evento(s) sensivel(is).",
                "warning" if sensitive_count else "info",
            )
        else:
            self._set_audit_operational_status(
                "Nenhum log carregado para revisao de rastreabilidade.",
                "warning",
            )
        self.audit_retention_status.setText(
            "Retencao: selecione um evento antes de avaliar exclusao."
        )

    def _audit_action_is_sensitive(self, action: str) -> bool:
        action_key = action.lower()
        sensitive_terms = ("delete", "remove", "password", "reset", "settings", "audit")
        return any(term in action_key for term in sensitive_terms)
