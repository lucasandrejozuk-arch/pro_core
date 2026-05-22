from __future__ import annotations

from typing import Any

from frontend.app.screens.dashboard_mixins_4_state_admin_settings_audit import (
    DashboardFormStateAdminSettingsAuditMixin,
)


class DashboardFormStateAdminMixin(DashboardFormStateAdminSettingsAuditMixin):
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

    def clear_resource_access_form(self) -> None:
        self.selected_user_id = None
        self.resource_access_target_label.setText("Selecione uma conta para revisar os acessos.")
        for checkbox in self.resource_access_checkboxes.values():
            checkbox.setChecked(False)
            checkbox.setEnabled(False)
        for checkbox in self.resource_access_tool_specialty_checkboxes.values():
            checkbox.setChecked(False)
            checkbox.setEnabled(False)
        self.resource_access_full_summary.setPlainText("Nenhuma conta selecionada.")
        self.resource_access_form_status.setText("")
        self.resource_access_save_button.setEnabled(False)
        self._refresh_resource_access_operational_status()
        self.table.clearSelection()

    def set_resource_access_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.resource_access_form_status, message, is_error)

    def set_resource_access_form_loading(self, is_loading: bool) -> None:
        has_selection = bool(self.selected_user_id)
        self.resource_access_new_button.setEnabled(not is_loading)
        self.resource_access_save_button.setEnabled(not is_loading and has_selection)
        for checkbox in self.resource_access_checkboxes.values():
            checkbox.setEnabled(not is_loading and has_selection)
        tool_module_enabled = bool(
            self.resource_access_checkboxes.get("tools")
            and self.resource_access_checkboxes["tools"].isEnabled()
            and self.resource_access_checkboxes["tools"].isChecked()
        )
        for checkbox in self.resource_access_tool_specialty_checkboxes.values():
            checkbox.setEnabled(not is_loading and has_selection and tool_module_enabled)
        self.resource_access_save_button.setText("Salvando..." if is_loading else "Salvar acessos")

    def _set_resource_access_operational_status(self, message: str, level: str) -> None:
        self.resource_access_operational_status.setText(message)
        self.resource_access_operational_status.setProperty("level", level)
        self.resource_access_operational_status.style().unpolish(
            self.resource_access_operational_status
        )
        self.resource_access_operational_status.style().polish(
            self.resource_access_operational_status
        )

    def _refresh_resource_access_operational_status(
        self, record: dict[str, Any] | None = None
    ) -> None:
        if record is not None:
            name = str(record.get("full_name") or "Conta")
            role = self._user_role_label(record.get("role"))
            self._set_resource_access_operational_status(
                f"Conta selecionada: {name} | Perfil: {role}. Ajuste os recursos liberados.",
                "info",
            )
            return
        count = len(self.all_rows) if self.active_module_key == "resource_access" else 0
        if count:
            self._set_resource_access_operational_status(
                f"{count} conta(s) carregada(s); selecione uma para editar acessos.",
                "info",
            )
        else:
            self._set_resource_access_operational_status(
                "Nenhum registro de acesso carregado para o seu escopo.",
                "warning",
            )

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
