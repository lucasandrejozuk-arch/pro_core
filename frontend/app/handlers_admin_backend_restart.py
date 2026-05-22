from __future__ import annotations

import math
from time import monotonic

from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit

from frontend.app.core.api_client import ApiError
from frontend.app.core.backend_process import ManagedBackendError, ManagedBackendUnavailable


class AdminBackendRestartHandlersMixin:
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
                    "Reinicio concluido, mas o backend ainda nao respondeu. "
                    "Tente novamente em instantes."
                )
        finally:
            self.login_window.set_backend_reconnect_loading(False)

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
