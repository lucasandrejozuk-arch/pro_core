from __future__ import annotations

from typing import Any

from frontend.app.themes.styles import DEFAULT_COLOR_PALETTE


class DashboardFormStateAdminSettingsAuditMixin:
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
            self._select_combo_value(self.settings_language_combo, "en-US")
        self.settings_backup_enabled_checkbox.setChecked(True)
        self.settings_backup_interval_input.setText("24")
        self.settings_backup_path_input.setText("backups")
        self.settings_backup_last_run_label.setText("Ultimo backup: nunca")
        self.settings_form_status.setText("")
        if hasattr(self, "_capture_settings_form_snapshot"):
            self.settings_form_snapshot = self._capture_settings_form_snapshot()
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

    def _refresh_settings_operational_status(self, settings: dict[str, Any] | None = None) -> None:
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
