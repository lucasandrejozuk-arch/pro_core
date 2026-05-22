# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from frontend.app.core.api_client import ApiClient, ApiError
from frontend.app.core.backend_health import BackendHealthProbe
from frontend.app.core.backend_process import ManagedBackendError, ManagedBackendProcess
from frontend.app.core.display import build_display_profile, prepare_window_for_display
from frontend.app.core.icons import build_app_icon
from frontend.app.core.session import AppSession
from frontend.app.core.settings import get_frontend_settings
from frontend.app.main_appearance import ProCoreAppearanceMixin
from frontend.app.main_data import ProCoreDataMixin
from frontend.app.main_handlers import ProCoreHandlersMixin
from frontend.app.screens.dashboard import DashboardWindow
from frontend.app.screens.login import LoginWindow
from frontend.app.screens.password_change import PasswordChangeWindow
from frontend.app.screens.splash import SplashScreen


class ProCoreApplication(ProCoreHandlersMixin, ProCoreAppearanceMixin, ProCoreDataMixin):
    def __init__(self) -> None:
        self._set_windows_app_id()
        self.qt_app = QApplication(sys.argv)
        self.app_icon = build_app_icon()
        self.qt_app.setWindowIcon(self.app_icon)
        self.local_settings = QSettings("PRO CORE", "PRO CORE")
        self._apply_local_theme()

        settings = get_frontend_settings()
        self.api_client = ApiClient(settings.api_base_url)
        self.backend_health_probe = BackendHealthProbe(settings.api_base_url)
        self.backend_health_connected = False
        self.backend_restart_cooldown_until = 0.0
        self._last_backend_restart_notice_id = ""
        self.backend_process = ManagedBackendProcess(PROJECT_ROOT)
        self.backend_process_start_error = ""
        if settings.manage_backend_process:
            try:
                self.backend_process.start()
            except ManagedBackendError as exc:
                self.backend_process_start_error = str(exc)
        self.session = AppSession()

        self.splash = SplashScreen()
        self.login_window = LoginWindow()
        self.password_window = PasswordChangeWindow()
        self.dashboard_window = DashboardWindow()
        self._apply_cached_login_branding()
        for window in (
            self.splash,
            self.login_window,
            self.password_window,
            self.dashboard_window,
        ):
            window.setWindowIcon(self.app_icon)
        self._apply_local_theme()
        self.active_module = "dashboard"

        self.splash.finished.connect(self.show_login)
        self.login_window.login_requested.connect(self.handle_login)
        self.login_window.password_reset_requested.connect(self.handle_password_reset_request)
        self.login_window.backend_reconnect_requested.connect(self.handle_login_backend_reconnect)
        self.password_window.password_change_requested.connect(self.handle_password_change)
        self.dashboard_window.logout_requested.connect(self.handle_logout)
        self.dashboard_window.exit_requested.connect(self.qt_app.quit)
        self.dashboard_window.module_selected.connect(self.load_module)
        self.dashboard_window.refresh_requested.connect(self.refresh_active_module)
        self.dashboard_window.customer_create_requested.connect(self.handle_customer_create)
        self.dashboard_window.customer_update_requested.connect(self.handle_customer_update)
        self.dashboard_window.customer_delete_requested.connect(self.handle_customer_delete)
        self.dashboard_window.customer_document_upload_requested.connect(
            self.handle_customer_document_upload
        )
        self.dashboard_window.equipment_create_requested.connect(self.handle_equipment_create)
        self.dashboard_window.equipment_update_requested.connect(self.handle_equipment_update)
        self.dashboard_window.equipment_delete_requested.connect(self.handle_equipment_delete)
        self.dashboard_window.equipment_board_create_requested.connect(
            self.handle_equipment_board_create
        )
        self.dashboard_window.equipment_board_update_requested.connect(
            self.handle_equipment_board_update
        )
        self.dashboard_window.equipment_board_delete_requested.connect(
            self.handle_equipment_board_delete
        )
        self.dashboard_window.equipment_component_create_requested.connect(
            self.handle_equipment_component_create
        )
        self.dashboard_window.equipment_component_update_requested.connect(
            self.handle_equipment_component_update
        )
        self.dashboard_window.equipment_component_delete_requested.connect(
            self.handle_equipment_component_delete
        )
        self.dashboard_window.equipment_defect_cases_requested.connect(
            self.handle_equipment_defect_cases
        )
        self.dashboard_window.equipment_import_requested.connect(self.handle_equipment_import)
        self.dashboard_window.equipment_export_requested.connect(self.handle_equipment_export)
        self.dashboard_window.inventory_create_requested.connect(self.handle_inventory_create)
        self.dashboard_window.inventory_update_requested.connect(self.handle_inventory_update)
        self.dashboard_window.inventory_delete_requested.connect(self.handle_inventory_delete)
        self.dashboard_window.inventory_document_download_requested.connect(
            self.handle_inventory_document_download
        )
        self.dashboard_window.sector_create_requested.connect(self.handle_sector_create)
        self.dashboard_window.sector_update_requested.connect(self.handle_sector_update)
        self.dashboard_window.sector_delete_requested.connect(self.handle_sector_delete)
        self.dashboard_window.service_order_create_requested.connect(
            self.handle_service_order_create
        )
        self.dashboard_window.service_order_update_requested.connect(
            self.handle_service_order_update
        )
        self.dashboard_window.service_order_delete_requested.connect(
            self.handle_service_order_delete
        )
        self.dashboard_window.service_order_diagnosis_requested.connect(
            self.handle_service_order_diagnosis
        )
        self.dashboard_window.service_order_budget_item_requested.connect(
            self.handle_service_order_budget_item
        )
        self.dashboard_window.service_order_submit_quote_requested.connect(
            self.handle_service_order_submit_quote
        )
        self.dashboard_window.service_order_approve_requested.connect(
            self.handle_service_order_approve
        )
        self.dashboard_window.service_order_reject_requested.connect(
            self.handle_service_order_reject
        )
        self.dashboard_window.service_order_start_requested.connect(self.handle_service_order_start)
        self.dashboard_window.service_order_complete_requested.connect(
            self.handle_service_order_complete
        )
        self.dashboard_window.service_order_document_upload_requested.connect(
            self.handle_service_order_document_upload
        )
        self.dashboard_window.user_create_requested.connect(self.handle_user_create)
        self.dashboard_window.user_update_requested.connect(self.handle_user_update)
        self.dashboard_window.user_delete_requested.connect(self.handle_user_delete)
        self.dashboard_window.user_password_reset_requested.connect(self.handle_user_password_reset)
        self.dashboard_window.user_resource_access_update_requested.connect(
            self.handle_user_resource_access_update
        )
        self.dashboard_window.password_reset_resolve_requested.connect(
            self.handle_password_reset_resolve
        )
        self.dashboard_window.password_reset_cancel_requested.connect(
            self.handle_password_reset_cancel
        )
        self.dashboard_window.settings_update_requested.connect(self.handle_settings_update)
        self.dashboard_window.ui_scale_changed.connect(self.handle_ui_scale_changed)
        self.dashboard_window.backup_run_requested.connect(self.handle_backup_run)
        self.dashboard_window.backend_restart_requested.connect(self.handle_backend_restart)
        self.dashboard_window.audit_delete_requested.connect(self.handle_audit_log_delete)
        self._sync_backend_restart_status()
        self.backend_health_timer = QTimer()
        self.backend_health_timer.setInterval(3000)
        self.backend_health_timer.timeout.connect(self.refresh_backend_health_status)
        self.backend_health_timer.start()
        self.refresh_backend_health_status()

    def run(self) -> int:
        self.splash.start()
        try:
            return self.qt_app.exec()
        finally:
            self.backend_health_timer.stop()
            self.backend_health_probe.close()
            self.api_client.close()
            self.backend_process.stop()

    def show_login(self) -> None:
        self.splash.close()
        self.password_window.hide()
        self.dashboard_window.hide()
        self._refresh_login_branding()
        self.login_window.clear_form()
        profile = prepare_window_for_display(
            self.login_window,
            preferred_size=(1100, 680),
            minimum_size=(760, 520),
        )
        if profile.should_maximize:
            self.login_window.showMaximized()
            return
        self.login_window.show()

    def handle_login(self, email: str, password: str) -> None:
        self.login_window.set_loading(True)

        try:
            auth_response = self.api_client.login(email=email, password=password)
        except ApiError as exc:
            self.login_window.set_loading(False)
            self.login_window.set_backend_connection_status(
                exc.status_code is not None,
                "Backend conectado." if exc.status_code is not None else "Backend indisponivel.",
            )
            self.login_window.set_error(exc.display_message)
            return

        self.login_window.set_backend_connection_status(True)
        self.session.set_authentication(
            access_token=auth_response["access_token"],
            user=auth_response["user"],
        )
        self.login_window.persist_remembered_user(email.strip().lower())
        self.login_window.hide()
        self.login_window.set_loading(False)

        if auth_response.get("must_change_password"):
            self.show_password_change()
            return

        self.show_dashboard()

    def show_password_change(self) -> None:
        self.password_window.clear_form()
        prepare_window_for_display(
            self.password_window,
            preferred_size=(700, 520),
            minimum_size=(520, 420),
        )
        self.password_window.show()

    def handle_password_change(self, current_password: str, new_password: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.password_window.set_loading(True)

        try:
            user = self.api_client.change_password(
                access_token=self.session.access_token,
                current_password=current_password,
                new_password=new_password,
            )
        except ApiError as exc:
            self.password_window.set_loading(False)
            self.password_window.set_error(exc.display_message)
            return

        self.session.update_user(user)
        self.password_window.hide()
        self.password_window.set_loading(False)
        self.show_dashboard()

    def show_dashboard(self) -> None:
        self._apply_saved_theme()
        self.dashboard_window.set_user(self.session.user)
        self.dashboard_window.set_session_login_at(self.session.login_at)
        profile = prepare_window_for_display(
            self.dashboard_window,
            preferred_size=(1680, 960),
            minimum_size=(980, 640),
        )
        profile = build_display_profile(profile.width, profile.height, self._local_ui_scale())
        self.dashboard_window.apply_display_profile(profile)
        self.dashboard_window.showMaximized()
        self.load_module(self.active_module)

    @staticmethod
    def _set_windows_app_id() -> None:
        if sys.platform != "win32":
            return

        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PROCORE.Desktop")
        except Exception:
            return

    def handle_logout(self) -> None:
        self.session.clear()
        self.show_login()

    def refresh_active_module(self) -> None:
        self.load_module(self.active_module)

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
        self.backend_health_connected = status.is_connected
        self.login_window.set_backend_connection_status(
            status.is_connected,
            status.message.replace("Backend: ", "Backend "),
        )
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
                return
            if module_key == "dashboard":
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_dashboard(
                    self._build_dashboard_summary(self.session.access_token)
                )
                return
            if module_key == "settings":
                settings = self.api_client.get_settings(self.session.access_token)
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_settings(settings)
                return
            if module_key == "tools":
                tools = self.api_client.list_tools(self.session.access_token)
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_tools(tools)
                return
            if module_key == "audit_logs":
                rows = self._load_module_rows(module_key, self.session.access_token)
                self.dashboard_window.set_backend_connection_status(True)
                self.dashboard_window.render_rows(title, rows, columns, module_key)
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


def main() -> int:
    return ProCoreApplication().run()


if __name__ == "__main__":
    raise SystemExit(main())
