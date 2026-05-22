from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from frontend.app.core.api_client import ApiError
from frontend.app.core.display import build_display_profile
from frontend.app.core.i18n import normalize_language, translate_ui_text


class AdminOperationsHandlersMixin:
    def handle_user_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_form_loading(True)
        try:
            self.api_client.create_user(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_user_form_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_form_loading(False)
        self.dashboard_window.set_user_form_status("Usuario criado.")
        self.load_module("users")

    def handle_user_update(self, user_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_form_loading(True)
        try:
            self.api_client.update_user(self.session.access_token, user_id, payload)
        except ApiError as exc:
            self.dashboard_window.set_user_form_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_form_loading(False)
        self.dashboard_window.set_user_form_status("Usuario atualizado.")
        self.load_module("users")

    def handle_user_password_reset(self, user_id: str, new_password: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_password_reset_loading(True)
        try:
            self.api_client.reset_user_password(
                self.session.access_token,
                user_id,
                new_password,
            )
        except ApiError as exc:
            self.dashboard_window.set_user_password_reset_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_password_reset_loading(False)
        self.dashboard_window.set_user_form_status("Senha redefinida.")
        self.load_module("users")

    def handle_user_resource_access_update(
        self,
        user_id: str,
        allowed_resources: list[str],
        allowed_tool_specialties: list[str],
    ) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_resource_access_form_loading(True)
        try:
            self.api_client.update_user_resource_access(
                self.session.access_token,
                user_id,
                allowed_resources,
                allowed_tool_specialties,
            )
        except ApiError as exc:
            self.dashboard_window.set_resource_access_form_loading(False)
            self.dashboard_window.set_resource_access_form_status(
                exc.display_message, is_error=True
            )
            return

        self.dashboard_window.set_resource_access_form_loading(False)
        self.dashboard_window.set_resource_access_form_status("Acessos atualizados.")
        self.load_module("resource_access")

    def handle_user_delete(self, user_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_form_loading(True)
        try:
            self.api_client.delete_user(self.session.access_token, user_id)
        except ApiError as exc:
            self.dashboard_window.set_user_form_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_form_loading(False)
        self.dashboard_window.set_user_form_status("Usuario excluido.")
        self.load_module("users")

    def handle_password_reset_request(self, email: str) -> None:
        self.login_window.set_password_reset_loading(True)
        try:
            response = self.api_client.request_password_reset(email)
        except ApiError as exc:
            self.login_window.set_password_reset_loading(False)
            self.login_window.set_error(exc.display_message)
            return

        self.login_window.set_password_reset_loading(False)
        self.login_window.set_info(str(response.get("message") or "Solicitacao enviada."))

    def handle_password_reset_resolve(self, request_id: str, new_password: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_password_reset_form_loading(True)
        try:
            self.api_client.resolve_password_reset_request(
                self.session.access_token,
                request_id,
                new_password,
            )
        except ApiError as exc:
            self.dashboard_window.set_password_reset_form_loading(False)
            self.dashboard_window.set_password_reset_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_password_reset_form_loading(False)
        self.dashboard_window.set_password_reset_form_status("Senha redefinida.")
        self.load_module("password_resets")

    def handle_password_reset_cancel(self, request_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_password_reset_form_loading(True)
        try:
            self.api_client.cancel_password_reset_request(
                self.session.access_token,
                request_id,
            )
        except ApiError as exc:
            self.dashboard_window.set_password_reset_form_loading(False)
            self.dashboard_window.set_password_reset_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_password_reset_form_loading(False)
        self.dashboard_window.set_password_reset_form_status("Solicitacao ignorada.")
        self.load_module("password_resets")

    def handle_settings_update(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        previous_language = normalize_language(
            str(self.local_settings.value("appearance/language", "pt-BR") or "pt-BR")
        )
        self.dashboard_window.set_settings_form_loading(True)
        try:
            settings = self.api_client.update_settings(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_settings_form_loading(False)
            self.dashboard_window.set_settings_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_settings_form_loading(False)
        self._remember_appearance(settings)
        self._apply_local_theme()
        self.dashboard_window.render_settings(settings)
        self.dashboard_window.set_settings_form_status("Configuracoes salvas.")
        self._apply_runtime_language(settings.get("language"))

        selected_language = normalize_language(str(settings.get("language") or previous_language))
        if selected_language == previous_language:
            return

        if self._confirm_frontend_restart_for_language(selected_language):
            self.request_frontend_restart()

    def _confirm_frontend_restart_for_language(self, language: str) -> bool:
        title = translate_ui_text("Reinicio do sistema", language)
        message = translate_ui_text(
            "Idioma alterado. Para garantir 100% de cobertura da traducao em toda "
            "a interface, reinicie o frontend agora.",
            language,
        )
        yes_label = translate_ui_text("Reiniciar agora", language)
        no_label = translate_ui_text("Reiniciar depois", language)
        answer = QMessageBox.question(
            self.dashboard_window,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.dashboard_window._set_footer_message(yes_label, "warning")
            return True
        self.dashboard_window._set_footer_message(no_label, "info")
        return False

    def handle_ui_scale_changed(self, scale: float) -> None:
        self.local_settings.setValue("appearance/ui_scale", str(scale))
        self._apply_local_theme()
        profile = build_display_profile(
            self.dashboard_window.width(),
            max(self.dashboard_window.height(), 640),
            scale,
        )
        self.dashboard_window.apply_display_profile(profile)

    def handle_backup_run(self) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_backup_run_loading(True)
        try:
            backup = self.api_client.run_backup(self.session.access_token)
            settings = self.api_client.get_settings(self.session.access_token)
        except ApiError as exc:
            self.dashboard_window.set_backup_run_loading(False)
            self.dashboard_window.set_settings_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_backup_run_loading(False)
        self.dashboard_window.render_settings(settings)
        self.dashboard_window.set_settings_form_status(
            f"Backup validado: {backup.get('file_name')}"
        )

    def handle_audit_log_delete(self, log_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_audit_form_loading(True)
        try:
            self.api_client.delete_audit_log(self.session.access_token, log_id)
        except ApiError as exc:
            self.dashboard_window.set_audit_form_loading(False)
            self.dashboard_window.set_audit_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_audit_form_loading(False)
        self.dashboard_window.set_audit_form_status("Log excluido.")
        self.load_module("audit_logs")
