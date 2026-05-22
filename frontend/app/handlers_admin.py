from __future__ import annotations

import math
from time import monotonic

from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox

from frontend.app.core.api_client import ApiError
from frontend.app.core.backend_process import ManagedBackendError, ManagedBackendUnavailable
from frontend.app.core.display import build_display_profile
from frontend.app.core.i18n import normalize_language, translate_ui_text


class AdminHandlersMixin:
    def _remaining_backend_restart_cooldown_seconds(self) -> int:
        cooldown_until = float(getattr(self, "backend_restart_cooldown_until", 0.0) or 0.0)
        remaining = cooldown_until - monotonic()
        if remaining <= 0:
            return 0
        return int(math.ceil(remaining))

    def _start_backend_restart_cooldown(self) -> None:
        self.backend_restart_cooldown_until = monotonic() + 3.0

    def _recover_login_backend_connection(self) -> bool:
        self.login_window.set_info(
            "Backend indisponivel. Tentando iniciar/reiniciar servidor interno."
        )
        QApplication.processEvents()
        try:
            self.backend_process.restart(apply_migrations=True)
        except ManagedBackendUnavailable:
            try:
                self.backend_process.start()
            except ManagedBackendError as exc:
                self.refresh_backend_health_status()
                self._sync_backend_restart_status()
                self.login_window.set_error(str(exc))
                return False
        except ManagedBackendError as exc:
            self.refresh_backend_health_status()
            self._sync_backend_restart_status()
            self.login_window.set_error(str(exc))
            return False

        self.refresh_backend_health_status()
        self._sync_backend_restart_status()
        if self.backend_health_connected:
            self.login_window.set_info("Backend conectado. Validando autorizacao de reinicio.")
            return True

        self.login_window.set_error(
            "Nao foi possivel reconectar ao backend apos tentativa de inicializacao."
        )
        return False

    def _request_backend_restart_authorization(
        self,
        operator_email: str,
        *,
        parent,
        show_status,
    ) -> dict | None:
        remaining = self._remaining_backend_restart_cooldown_seconds()
        if remaining > 0:
            show_status(f"Aguarde {remaining}s para nova tentativa de reinicio.")
            return None

        default_operator_email = str(operator_email or "").strip().lower()
        if not default_operator_email:
            show_status("Informe o email da conta operadora para iniciar o reinicio.")
            return None

        admin_email, accepted = QInputDialog.getText(
            parent,
            "Confirmar reinicio",
            "Email do administrador autorizador:",
            QLineEdit.EchoMode.Normal,
            default_operator_email,
        )
        if not accepted:
            return None
        admin_email = admin_email.strip().lower()
        if not admin_email:
            show_status("O email do administrador e obrigatorio para autorizar o reinicio.")
            return None

        admin_password, accepted = QInputDialog.getText(
            parent,
            "Confirmar senha admin",
            "Senha do administrador:",
            QLineEdit.EchoMode.Password,
            "",
        )
        if not accepted:
            return None
        if not admin_password:
            show_status("A senha do administrador e obrigatoria para autorizar o reinicio.")
            return None

        reason_options = [
            "Manutencao programada",
            "Backend travado",
            "Outro motivo",
        ]
        selected_reason, accepted = QInputDialog.getItem(
            parent,
            "Motivo do reinicio",
            "Selecione o motivo:",
            reason_options,
            0,
            False,
        )
        if not accepted:
            return None

        reason_map = {
            "Manutencao programada": "maintenance",
            "Backend travado": "hang",
            "Outro motivo": "other",
        }
        reason_type = reason_map.get(selected_reason, "maintenance")
        custom_reason = None
        if reason_type == "other":
            custom_reason, accepted = QInputDialog.getText(
                parent,
                "Motivo personalizado",
                "Descreva o motivo do reinicio:",
            )
            if not accepted:
                return None
            custom_reason = custom_reason.strip()
            if len(custom_reason) < 4:
                show_status("Informe um motivo personalizado com pelo menos 4 caracteres.")
                return None

        try:
            response = self.api_client.authorize_backend_restart(
                operator_email=default_operator_email,
                admin_email=admin_email,
                admin_password=admin_password,
                reason_type=reason_type,
                custom_reason=custom_reason,
            )
        except ApiError as exc:
            show_status(exc.display_message)
            return None

        self._start_backend_restart_cooldown()
        return response

    def handle_login_backend_reconnect(self) -> None:
        operator_email = self.login_window.email_input.text().strip().lower()
        self.login_window.set_backend_reconnect_loading(True)
        was_connected = bool(self.backend_health_connected)
        try:
            if not was_connected and not self._recover_login_backend_connection():
                return

            authorization = self._request_backend_restart_authorization(
                operator_email,
                parent=self.login_window,
                show_status=self.login_window.set_error,
            )
            if authorization is None:
                return

            reason = str(authorization.get("reason") or "Reinicio solicitado")
            if not was_connected:
                self.login_window.set_info(
                    f"Backend conectado e aviso global registrado. Motivo: {reason}."
                )
                return

            self.login_window.set_info(f"Tentando conectar/reiniciar backend. Motivo: {reason}.")
            QApplication.processEvents()
            try:
                self.backend_process.restart(apply_migrations=True)
            except ManagedBackendUnavailable as exc:
                self.refresh_backend_health_status()
                self._sync_backend_restart_status()
                if self.backend_health_connected:
                    self.login_window.set_info("Backend conectado.")
                else:
                    self.login_window.set_error(str(exc))
                return
            except ManagedBackendError as exc:
                self.refresh_backend_health_status()
                self._sync_backend_restart_status()
                self.login_window.set_error(str(exc))
                return

            self.refresh_backend_health_status()
            self._sync_backend_restart_status()
            if self.backend_health_connected:
                self.login_window.set_info("Backend conectado e reiniciado com sucesso.")
            else:
                self.login_window.set_error(
                    "Reinicio concluido, mas o backend ainda nao respondeu. Tente novamente em instantes."
                )
        finally:
            self.login_window.set_backend_reconnect_loading(False)

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
            "Idioma alterado. Para garantir 100% de cobertura da traducao em toda a interface, reinicie o frontend agora.",
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
        # Keep localized feedback in footer for both decisions.
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

    def handle_backend_restart(self) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        operator_email = str(self.session.user.get("email") or "").strip().lower()
        authorization = self._request_backend_restart_authorization(
            operator_email,
            parent=self.dashboard_window,
            show_status=lambda message: self.dashboard_window._set_footer_message(message, "error"),
        )
        if authorization is None:
            return

        self.dashboard_window.set_backend_restart_loading(True)
        self.dashboard_window.set_backend_connection_status(
            False,
            "Backend: atualizando",
            level="warning",
        )
        self.dashboard_window.set_internal_server_status("warning", "Servidor interno: atualizando")
        reason = str(authorization.get("reason") or "Reinicio solicitado")
        self.dashboard_window._set_footer_message(
            f"Aplicando migrations e reiniciando backend. Motivo: {reason}.",
            "warning",
        )
        QApplication.processEvents()
        try:
            self.backend_process.restart(apply_migrations=True)
        except ManagedBackendUnavailable as exc:
            self.dashboard_window.set_backend_restart_loading(False)
            self.dashboard_window.set_internal_server_status("warning", "Servidor interno: externo")
            self.dashboard_window.set_backend_restart_available(False, str(exc))
            self.dashboard_window._set_footer_message(str(exc), "warning")
            return
        except ManagedBackendError as exc:
            self.dashboard_window.set_backend_restart_loading(False)
            self.refresh_backend_health_status()
            self._sync_backend_restart_status()
            self.dashboard_window._set_footer_message(str(exc), "error")
            return

        self.dashboard_window.set_backend_restart_loading(False)
        self.refresh_backend_health_status()
        self._sync_backend_restart_status()
        self.dashboard_window._set_footer_message(
            "Backend atualizado, migrations aplicadas e servico reconectado.",
            "success",
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
