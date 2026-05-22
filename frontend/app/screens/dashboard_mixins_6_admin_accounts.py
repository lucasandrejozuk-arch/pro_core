from __future__ import annotations

from typing import Any


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardAdminAccountActionsMixin:
    def _populate_sector_form(self, sector: dict[str, Any]) -> None:
        self.selected_sector_id = str(sector["id"])
        self.sector_name_input.setText(str(sector.get("name") or ""))
        self.sector_description_input.setText(str(sector.get("description") or ""))
        is_admin = self.current_user_role == "admin"
        self.sector_new_button.setEnabled(is_admin)
        self.sector_delete_button.setEnabled(is_admin)
        self.sector_save_button.setEnabled(is_admin)
        self.sector_name_input.setEnabled(is_admin)
        self.sector_description_input.setEnabled(is_admin)
        status_message = (
            "Editando setor selecionado." if is_admin else "Setor disponivel apenas para consulta."
        )
        self.sector_full_summary.setPlainText(self._format_sector_summary(sector))
        self._refresh_sector_operational_status(sector)
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

    def _request_sector_delete(self) -> None:
        if not self.selected_sector_id:
            self.set_sector_form_status("Selecione um setor.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir setor",
            "Excluir o setor selecionado?",
        ):
            return
        self.sector_delete_requested.emit(self.selected_sector_id)

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
        self.user_delete_button.setEnabled(True)
        self.user_full_summary.setPlainText(self._format_user_summary(user))
        self._refresh_user_operational_status(user)
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

        if not self._is_valid_email(email):
            self.set_user_form_status("Informe um email valido.", is_error=True)
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
        if not self._is_valid_password(password):
            self.set_user_form_status("Senha deve ter pelo menos 8 caracteres.", is_error=True)
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
        if not self._is_valid_password(new_password):
            self.set_user_form_status("Senha deve ter pelo menos 8 caracteres.", is_error=True)
            return

        self.set_user_form_status("")
        self.user_password_reset_requested.emit(self.selected_user_id, new_password)

    def _request_user_delete(self) -> None:
        if not self.selected_user_id:
            self.set_user_form_status("Selecione um usuario.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir usuario",
            "Excluir o usuario selecionado?",
        ):
            return
        self.user_delete_requested.emit(self.selected_user_id)

    def _populate_resource_access_form(self, record: dict[str, Any]) -> None:
        self.selected_user_id = str(record.get("user_id") or "")
        target = str(record.get("full_name") or "Conta")
        email = str(record.get("email") or "")
        role = self._user_role_label(record.get("role"))
        self.resource_access_target_label.setText(f"Conta: {target} | {email} | Perfil: {role}")
        default_resources = {
            str(item) for item in (record.get("default_resources") or []) if str(item)
        }
        allowed_resources = {
            str(item) for item in (record.get("allowed_resources") or []) if str(item)
        }
        allowed_tool_specialties = {
            str(item).strip().lower()
            for item in (record.get("allowed_tool_specialties") or [])
            if str(item).strip()
        }
        default_tool_specialties = {
            str(item).strip().lower()
            for item in (record.get("default_tool_specialties") or [])
            if str(item).strip()
        }
        for key, checkbox in self.resource_access_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(key in allowed_resources)
            checkbox.setEnabled(key in default_resources)
            checkbox.blockSignals(False)
        tool_module_enabled = bool(
            self.resource_access_checkboxes.get("tools")
            and self.resource_access_checkboxes["tools"].isEnabled()
            and self.resource_access_checkboxes["tools"].isChecked()
        )
        for key, checkbox in self.resource_access_tool_specialty_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(key in allowed_tool_specialties)
            checkbox.setEnabled(tool_module_enabled and key in default_tool_specialties)
            checkbox.blockSignals(False)
        self.resource_access_save_button.setEnabled(bool(self.selected_user_id))
        self.resource_access_full_summary.setPlainText(self._format_resource_access_summary(record))
        self._refresh_resource_access_operational_status(record)
        self.set_resource_access_form_status("Revise os recursos e salve para aplicar.")

    def _request_resource_access_save(self) -> None:
        if not self.selected_user_id:
            self.set_resource_access_form_status(
                "Selecione uma conta para salvar os acessos.", is_error=True
            )
            return
        allowed_resources = [
            key
            for key, checkbox in self.resource_access_checkboxes.items()
            if checkbox.isEnabled() and checkbox.isChecked()
        ]
        allowed_tool_specialties = [
            key
            for key, checkbox in self.resource_access_tool_specialty_checkboxes.items()
            if checkbox.isEnabled() and checkbox.isChecked()
        ]
        self.set_resource_access_form_status("")
        self.user_resource_access_update_requested.emit(
            self.selected_user_id,
            allowed_resources,
            allowed_tool_specialties,
        )
