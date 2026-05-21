from __future__ import annotations

from typing import Any

from frontend.app.themes.styles import DEFAULT_COLOR_PALETTE


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardAdminActionsMixin:
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
        if not self._is_valid_password(new_password):
            self.set_password_reset_form_status(
                "Senha deve ter pelo menos 8 caracteres.",
                is_error=True,
            )
            return

        self.set_password_reset_form_status("")
        self.password_reset_resolve_requested.emit(
            self.selected_password_reset_request_id,
            new_password,
        )

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
        self._select_combo_value(
            self.settings_language_combo,
            str(settings.get("language") or "pt-BR"),
        )
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

        email = self._optional_text(self.settings_email_input)
        if email and not self._is_valid_email(email):
            self.set_settings_form_status("Informe um email valido.", is_error=True)
            return

        payload = {
            "company_name": company_name,
            "trade_name": self._optional_text(self.settings_trade_name_input),
            "document_number": self._optional_text(self.settings_document_input),
            "email": email,
            "phone": self._optional_text(self.settings_phone_input),
            "brand_name": self._optional_text(self.settings_brand_name_input),
            "brand_subtitle": self._optional_text(self.settings_brand_subtitle_input),
            "color_palette": str(
                self.settings_color_palette_combo.currentData() or DEFAULT_COLOR_PALETTE
            ),
            "theme": str(self.settings_theme_combo.currentData() or "light"),
            "language": str(self.settings_language_combo.currentData() or "pt-BR"),
            "backup_enabled": self.settings_backup_enabled_checkbox.isChecked(),
            "backup_interval_hours": backup_interval_hours,
            "backup_storage_path": backup_storage_path,
        }
        self.set_settings_form_status("")
        self.settings_update_requested.emit(payload)

    def _request_audit_delete(self) -> None:
        if not self.current_selected_record:
            self.set_audit_form_status("Selecione um log.", is_error=True)
            return
        log_id = str(self.current_selected_record.get("id") or "")
        if not log_id:
            self.set_audit_form_status("Selecione um log valido.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir log",
            "Excluir o log de auditoria selecionado?",
        ):
            return
        self.audit_delete_requested.emit(log_id)

    def _refresh_service_order_equipment_combo(self) -> None:
        if not hasattr(self, "service_order_equipment_combo"):
            return

        current_equipment_id = self.service_order_equipment_combo.currentData()
        selected_customer_id = (
            str(self.service_order_customer_combo.currentData() or "")
            if hasattr(self, "service_order_customer_combo")
            else ""
        )
        selected_type = (
            str(self.service_order_equipment_type_combo.currentData() or "")
            if hasattr(self, "service_order_equipment_type_combo")
            else ""
        )
        self.service_order_equipment_combo.clear()

        for equipment in self.service_order_equipment:
            equipment_customer_id = str(equipment.get("customer_id") or "")
            equipment_type = str(equipment.get("category") or "").strip()
            if (
                selected_customer_id
                and equipment_customer_id
                and equipment_customer_id != selected_customer_id
            ):
                continue
            if selected_type and equipment_type != selected_type:
                continue
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
