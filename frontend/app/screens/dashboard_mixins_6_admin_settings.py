from __future__ import annotations

import secrets
import string
from typing import Any

from frontend.app.themes.styles import DEFAULT_COLOR_PALETTE


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardAdminSettingsActionsMixin:
    def _active_settings_tab_key(self) -> str:
        tab_keys = ("company", "appearance", "interface", "backup")
        index = self.settings_tabs.currentIndex() if hasattr(self, "settings_tabs") else 0
        if 0 <= index < len(tab_keys):
            return tab_keys[index]
        return "company"

    def _capture_settings_form_snapshot(self) -> dict[str, Any]:
        return {
            "company_name": self.settings_company_name_input.text().strip(),
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
            "language": str(self.settings_language_combo.currentData() or "en-US"),
            "login_cover_preset": str(
                self.settings_login_cover_preset_combo.currentData() or "original"
            ),
            "login_cover_image_data_url": str(
                getattr(self, "settings_login_cover_image_data_url", "") or ""
            ),
            "backup_enabled": self.settings_backup_enabled_checkbox.isChecked(),
            "backup_interval_hours": self.settings_backup_interval_input.text().strip(),
            "backup_storage_path": self.settings_backup_path_input.text().strip(),
        }

    def _populate_password_reset_form(self, request: dict[str, Any]) -> None:
        self.selected_password_reset_request_id = str(request["id"])
        self.selected_password_reset_status = self._password_reset_status_key(request.get("status"))
        full_name = self._format_value(request.get("requester_full_name"))
        email = self._format_value(request.get("requester_email"))
        role = self._format_value(request.get("requester_role"))
        created_at = self._format_value(request.get("created_at"))
        self.password_reset_requester_label.setText(
            f"Solicitante: {full_name} | {email} | Perfil: {role} | Criada em: {created_at}"
        )
        self.password_reset_new_password_input.clear()
        can_resolve = self._password_reset_can_resolve()
        self.password_reset_generate_button.setEnabled(can_resolve)
        self.password_reset_resolve_button.setEnabled(False)
        self.password_reset_cancel_button.setEnabled(can_resolve)
        self.password_reset_full_summary.setPlainText(self._format_password_reset_summary(request))
        self._refresh_password_reset_operational_status(request)
        self.set_password_reset_form_status(
            "Gere uma senha temporaria para redefinir o acesso."
            if can_resolve
            else "Solicitacao ja encerrada."
        )

    def _generate_password_reset_temporary_password(self) -> None:
        if not self._password_reset_can_resolve():
            self.set_password_reset_form_status(
                "Selecione uma solicitacao pendente.",
                is_error=True,
            )
            return

        alphabet = string.ascii_letters + string.digits
        required = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
        ]
        generated = required + [secrets.choice(alphabet) for _ in range(3)]
        secrets.SystemRandom().shuffle(generated)
        self.password_reset_new_password_input.setText("".join(generated))
        self.password_reset_resolve_button.setEnabled(True)
        self.set_password_reset_form_status("Senha temporaria gerada.")

    def _request_password_reset_resolve(self) -> None:
        if not self.selected_password_reset_request_id:
            self.set_password_reset_form_status(
                "Selecione uma solicitacao.",
                is_error=True,
            )
            return

        new_password = self.password_reset_new_password_input.text()
        if not new_password:
            self.set_password_reset_form_status("Gere a senha temporaria.", is_error=True)
            return
        if not self._is_valid_temporary_password(new_password):
            self.set_password_reset_form_status(
                "Senha temporaria deve ter 6 caracteres com letras maiusculas, "
                "minusculas e numeros.",
                is_error=True,
            )
            return

        self.set_password_reset_form_status("")
        self.password_reset_resolve_requested.emit(
            self.selected_password_reset_request_id,
            new_password,
        )

    def _request_password_reset_cancel(self) -> None:
        if not self.selected_password_reset_request_id:
            self.set_password_reset_form_status(
                "Selecione uma solicitacao.",
                is_error=True,
            )
            return
        if not self._password_reset_can_resolve():
            self.set_password_reset_form_status("Solicitacao ja encerrada.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Ignorar solicitacao",
            "Marcar a solicitacao de redefinicao de senha como ignorada?",
        ):
            return
        self.password_reset_cancel_requested.emit(self.selected_password_reset_request_id)

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
            str(settings.get("language") or "en-US"),
        )
        self.settings_login_cover_image_data_url = str(
            settings.get("login_cover_image_data_url") or ""
        )
        self._select_combo_value(
            self.settings_login_cover_preset_combo,
            str(settings.get("login_cover_preset") or "original"),
        )
        self._handle_login_cover_preset_changed()
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
        self.settings_form_snapshot = self._capture_settings_form_snapshot()
        self.apply_branding(settings)
        self._refresh_settings_operational_status(settings)
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
        if hasattr(self, "settings_operational_status"):
            self._refresh_settings_operational_status()

    def _handle_ui_scale_slider_changed(self, value: int) -> None:
        self.ui_scale_value = value / 100
        self.settings_ui_scale_label.setText(f"{value}%")
        self._refresh_settings_operational_status()
        self.ui_scale_changed.emit(self.ui_scale_value)

    def _request_settings_save(self) -> None:
        baseline_settings = dict(
            getattr(self, "settings_form_snapshot", {})
            or getattr(self, "current_settings", {})
            or {}
        )
        current_form = self._capture_settings_form_snapshot()
        payload: dict[str, Any] = {}
        active_tab = self._active_settings_tab_key()

        def _baseline_text(key: str) -> str:
            return str(baseline_settings.get(key) or "").strip()

        def _form_text(key: str) -> str:
            return str(current_form.get(key) or "").strip()

        def _changed(key: str) -> bool:
            return current_form.get(key) != baseline_settings.get(key)

        def _add_optional_text(key: str, value: str | None) -> None:
            if (value or "") != _baseline_text(key):
                payload[key] = value

        if active_tab == "company":
            company_keys = (
                "company_name",
                "trade_name",
                "document_number",
                "email",
                "phone",
            )
            company_changed = any(_changed(key) for key in company_keys)
            company_name = _form_text("company_name")
            if company_changed and company_name != _baseline_text("company_name"):
                if not company_name:
                    self.set_settings_form_status("Informe o nome da empresa.", is_error=True)
                    return
                payload["company_name"] = company_name

            email = current_form.get("email")
            email_changed = (email or "") != _baseline_text("email")
            if email_changed and email and not self._is_valid_email(email):
                self.set_settings_form_status("Informe um email valido.", is_error=True)
                return

            if company_changed:
                _add_optional_text("trade_name", current_form.get("trade_name"))
                _add_optional_text("document_number", current_form.get("document_number"))
                if email_changed:
                    payload["email"] = email
                _add_optional_text("phone", current_form.get("phone"))

        elif active_tab == "appearance":
            for key in ("brand_name", "brand_subtitle", "color_palette", "theme"):
                if _changed(key):
                    payload[key] = current_form.get(key)

            login_cover_preset = str(current_form.get("login_cover_preset") or "original")
            if _changed("login_cover_preset"):
                payload["login_cover_preset"] = login_cover_preset
            current_cover_data = str(baseline_settings.get("login_cover_image_data_url") or "")
            if login_cover_preset == "custom":
                cover_data = str(current_form.get("login_cover_image_data_url") or "")
                if not cover_data and not current_cover_data:
                    self.set_settings_form_status(
                        "Selecione uma imagem PNG/JPEG para a capa customizada.",
                        is_error=True,
                    )
                    return
                if cover_data != current_cover_data:
                    payload["login_cover_image_data_url"] = cover_data
            elif current_cover_data and (
                _changed("login_cover_preset") or _changed("login_cover_image_data_url")
            ):
                payload["login_cover_image_data_url"] = None

        elif active_tab == "interface":
            if _changed("language"):
                payload["language"] = current_form.get("language")

        elif active_tab == "backup":
            backup_enabled = bool(current_form.get("backup_enabled", True))
            interval_text = _form_text("backup_interval_hours")
            current_interval = _baseline_text("backup_interval_hours")
            backup_storage_path = _form_text("backup_storage_path")
            current_backup_path = _baseline_text("backup_storage_path")
            backup_changed = (
                _changed("backup_enabled")
                or _changed("backup_interval_hours")
                or _changed("backup_storage_path")
            )
            if backup_changed:
                if _changed("backup_enabled"):
                    payload["backup_enabled"] = backup_enabled
                if interval_text:
                    try:
                        backup_interval_hours = int(interval_text)
                    except ValueError:
                        self.set_settings_form_status(
                            "Intervalo de backup deve ser inteiro.", is_error=True
                        )
                        return
                    if backup_interval_hours < 1 or backup_interval_hours > 720:
                        self.set_settings_form_status(
                            "Intervalo de backup deve ficar entre 1 e 720 horas.",
                            is_error=True,
                        )
                        return
                    if interval_text != current_interval:
                        payload["backup_interval_hours"] = backup_interval_hours
                elif backup_enabled and current_interval:
                    self.set_settings_form_status("Informe o intervalo de backup.", is_error=True)
                    return

                if backup_storage_path:
                    if backup_storage_path != current_backup_path:
                        payload["backup_storage_path"] = backup_storage_path
                elif backup_enabled and current_backup_path:
                    self.set_settings_form_status("Informe a pasta de backup.", is_error=True)
                    return

        if not payload:
            self.set_settings_form_status("Nenhuma alteracao pendente.")
            return

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

    def _populate_audit_form(self, record: dict[str, Any]) -> None:
        self.audit_full_summary.setPlainText(self._format_audit_summary(record))
        self._refresh_audit_operational_status(record)
        self.audit_delete_button.setEnabled(True)
        self.set_audit_form_status("Log selecionado para revisao.")

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
