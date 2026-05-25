from __future__ import annotations

import webbrowser
from urllib.parse import urlsplit, urlunsplit

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from frontend.app.core.api_client import ApiError
from frontend.app.core.backend_process import ManagedBackendError


class ProCoreMainRuntimeMixin:
    def handle_login_backend_connect(self) -> None:
        self.login_window.set_backend_connect_loading(True)
        self.login_window.set_info("Tentando inicializar/reinicializar backend...")
        self.backend_process_start_error = ""

        try:
            if self.backend_process.is_running and self.backend_process.is_managed:
                self.backend_process.restart(apply_migrations=False)
            else:
                self.backend_process.start()
        except ManagedBackendError as exc:
            self.backend_process_start_error = str(exc)
            self.refresh_backend_health_status()
            self.login_window.set_backend_connect_loading(False)
            self.login_window.set_error(str(exc))
            return

        self.refresh_backend_health_status()
        if self.backend_health_connected:
            self.login_window.set_backend_connect_loading(False)
            self.login_window.set_info("Backend conectado.")
            return

        QTimer.singleShot(1200, self._complete_login_backend_connect)

    def _complete_login_backend_connect(self) -> None:
        self.refresh_backend_health_status()
        self.login_window.set_backend_connect_loading(False)

        if self.backend_health_connected:
            self.login_window.set_info("Backend conectado.")
            return

        if self.backend_process_start_error:
            self.login_window.set_error(self.backend_process_start_error)
            return

        if self.backend_process.is_running:
            self.login_window.set_info(
                "Backend iniciado/reiniciado. Aguarde alguns instantes para concluir a conexao."
            )
            return

        self.login_window.set_error(
            "Nao foi possivel conectar ao backend. Tente novamente em instantes."
        )

    def handle_open_customer_portal(self) -> None:
        if str(self.session.user.get("role") or "") != "admin":
            self.dashboard_window._set_footer_message(
                "Acesso ao portal do cliente disponivel apenas para administradores.",
                "error",
            )
            return

        parsed = urlsplit(str(self.api_client._client.base_url))
        if not parsed.scheme or not parsed.netloc:
            self.dashboard_window._set_footer_message(
                "URL base do backend invalida para abrir o portal do cliente.",
                "error",
            )
            return
        path = parsed.path.rstrip("/")
        for suffix in ("/api/v1", "/api"):
            if path.endswith(suffix):
                path = path[: -len(suffix)]
                break
        portal_url = urlunsplit((parsed.scheme, parsed.netloc, f"{path}/customer-portal", "", ""))
        try:
            opened = webbrowser.open(portal_url)
        except Exception as exc:
            self.dashboard_window._set_footer_message(
                f"Falha ao acionar navegador para o portal do cliente: {exc}",
                "error",
            )
            return
        if opened:
            self.dashboard_window._set_footer_message(
                f"Portal do cliente aberto no navegador: {portal_url}",
                "success",
            )
            return
        self.dashboard_window._set_footer_message(
            "Nao foi possivel abrir o navegador para o portal do cliente.",
            "error",
        )

    def _sync_backend_restart_status(self) -> None:
        if self.backend_process.is_managed:
            if self.backend_process.is_running:
                if self.backend_health_connected:
                    self.dashboard_window.set_internal_server_status(
                        "success",
                        "Servidor interno: gerenciado",
                    )
                else:
                    self.dashboard_window.set_internal_server_status(
                        "error",
                        "Servidor interno: sem resposta",
                    )
                self.dashboard_window.set_backend_restart_available(
                    True,
                    "Reinicio seguro disponivel: backend gerenciado pelo app.",
                )
                return
            self.dashboard_window.set_internal_server_status("warning", "Servidor interno: parado")
            self.dashboard_window.set_backend_restart_available(
                True,
                "Backend gerenciado pelo app esta parado; reinicio iniciara novo processo.",
            )
            return

        if self.backend_process_start_error:
            self.dashboard_window.set_internal_server_status("error", "Servidor interno: falhou")
            self.dashboard_window.set_backend_restart_available(
                False,
                self.backend_process_start_error,
            )
            return

        self.dashboard_window.set_internal_server_status("warning", "Servidor interno: externo")
        self.dashboard_window.set_backend_restart_available(
            False,
            "Reinicio seguro indisponivel: backend atual nao foi iniciado pelo app.",
        )

    def refresh_backend_health_status(self) -> None:
        status = self.backend_health_probe.check()
        was_connected = self.backend_health_connected
        self.backend_health_connected = status.is_connected
        self.login_window.set_backend_connection_status(
            status.is_connected,
            status.message.replace("Backend: ", "Backend "),
        )
        if status.is_connected and not was_connected and self.login_window.isVisible():
            self._refresh_login_branding()
        self.dashboard_window.set_backend_connection_status(status.is_connected, status.message)
        self._sync_backend_restart_status()
        self._poll_backend_restart_notice()

    def _poll_backend_restart_notice(self) -> None:
        if not self.session.access_token:
            return
        try:
            response = self.api_client.poll_backend_restart_notice(
                self.session.access_token,
                last_notice_id=self._last_backend_restart_notice_id or None,
            )
        except ApiError:
            return

        if not bool(response.get("has_notice")):
            return
        notice = response.get("notice") or {}
        notice_id = str(notice.get("id") or "").strip()
        reason = str(notice.get("reason") or "").strip() or "Reinicio solicitado"
        if not notice_id:
            return
        self._last_backend_restart_notice_id = notice_id

        message = (
            "O sistema esta sendo reiniciado. "
            f"Motivo informado: {reason}. "
            "Salve seu trabalho e aguarde a reconexao."
        )
        parent = self.dashboard_window if self.dashboard_window.isVisible() else self.login_window
        QMessageBox.warning(parent, "Reinicio do sistema", message)

    def _prime_backend_restart_notice_cursor(self) -> None:
        if not self.session.access_token:
            self._last_backend_restart_notice_id = ""
            return
        try:
            response = self.api_client.poll_backend_restart_notice(
                self.session.access_token,
                last_notice_id=None,
            )
        except ApiError:
            return
        if not bool(response.get("has_notice")):
            return
        notice = response.get("notice") or {}
        notice_id = str(notice.get("id") or "").strip()
        if notice_id:
            self._last_backend_restart_notice_id = notice_id

    def load_module(self, module_key: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        if not self._module_allowed(module_key):
            self.dashboard_window.render_error(
                "Acesso negado",
                "Seu perfil nao possui acesso a este modulo.",
                self.active_module or "dashboard",
            )
            return

        self.active_module = module_key
        title, columns = self._module_columns(module_key)
        self.dashboard_window.render_loading(title, module_key)

        try:
            if module_key == "admin_area":
                self.dashboard_window.render_admin_area()
                self._apply_runtime_language()
                return
            if module_key == "dashboard":
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_dashboard(
                    self._build_dashboard_summary(self.session.access_token)
                )
                self._apply_runtime_language()
                return
            if module_key == "settings":
                settings = self.api_client.get_settings(self.session.access_token)
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_settings(settings)
                self._apply_runtime_language(settings.get("language"))
                return
            if module_key == "tools":
                tools = self.api_client.list_tools(self.session.access_token)
                allowed_specialties = [
                    str(item).strip().lower()
                    for item in (self.session.user.get("tools_specialties") or [])
                    if str(item).strip()
                ]
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_tools(tools, allowed_specialties=allowed_specialties)
                self._apply_runtime_language()
                return
            if module_key == "audit_logs":
                rows = self._load_module_rows(module_key, self.session.access_token)
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_rows(title, rows, columns, module_key)
                self._apply_runtime_language()
                return

            user_sectors = (
                self.api_client.list_sectors(self.session.access_token)
                if module_key == "users"
                else None
            )
            rows = self._load_module_rows(module_key, self.session.access_token)
            service_order_dependencies = None
            if module_key == "service_orders":
                if str(self.session.user.get("role") or "") in {"admin", "manager"}:
                    service_order_dependencies = (
                        self.api_client.list_customers(self.session.access_token),
                        self.api_client.list_equipment(self.session.access_token),
                        self.api_client.list_technicians(self.session.access_token),
                    )
                else:
                    service_order_dependencies = self._dependencies_from_service_orders(rows)
        except ApiError as exc:
            self.dashboard_window.set_backend_connection_status(exc.status_code is not None)
            self.dashboard_window.render_error(title, exc.display_message, module_key)
            return

        self.dashboard_window.set_backend_connection_status(True)
        if user_sectors is not None:
            sector_names = {
                str(sector["id"]): str(sector.get("name") or "") for sector in user_sectors
            }
            for row in rows:
                row["sector_name"] = sector_names.get(str(row.get("sector_id")), "")
            self.dashboard_window.set_user_sectors(user_sectors)
        if service_order_dependencies is not None:
            self.dashboard_window.set_service_order_dependencies(*service_order_dependencies)

        self.dashboard_window.render_rows(title, rows, columns, module_key)
        self._apply_runtime_language()
