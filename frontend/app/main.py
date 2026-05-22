# ruff: noqa: E402
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtWidgets import QApplication

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
from frontend.app.main_runtime import ProCoreMainRuntimeMixin
from frontend.app.main_signals import ProCoreMainSignalsMixin
from frontend.app.screens.dashboard import DashboardWindow
from frontend.app.screens.login import LoginWindow
from frontend.app.screens.password_change import PasswordChangeWindow
from frontend.app.screens.splash import SplashScreen


class ProCoreApplication(
    ProCoreMainSignalsMixin,
    ProCoreMainRuntimeMixin,
    ProCoreHandlersMixin,
    ProCoreAppearanceMixin,
    ProCoreDataMixin,
):
    def __init__(self) -> None:
        self._restart_requested = False
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

        self._connect_application_signals()
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

    def request_frontend_restart(self) -> None:
        self._restart_requested = True
        self.qt_app.quit()

    def show_login(self) -> None:
        self.splash.close()
        self.password_window.hide()
        self.dashboard_window.hide()
        self._refresh_login_branding()
        self._apply_runtime_language()
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
        self._prime_backend_restart_notice_cursor()
        self.login_window.persist_remembered_user(email.strip().lower())
        self.login_window.hide()
        self.login_window.set_loading(False)

        if auth_response.get("must_change_password"):
            self.show_password_change()
            return

        self.show_dashboard()

    def show_password_change(self) -> None:
        self.password_window.clear_form()
        self._apply_runtime_language()
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
        self._apply_runtime_language()
        self._show_dashboard_maximized()
        self.load_module(self.active_module)

    def _show_dashboard_maximized(self) -> None:
        self.dashboard_window.showMaximized()
        self.dashboard_window.raise_()
        self.dashboard_window.activateWindow()
        QTimer.singleShot(0, self._enforce_dashboard_maximized_geometry)
        QTimer.singleShot(250, self._enforce_dashboard_maximized_geometry)

    def _enforce_dashboard_maximized_geometry(self) -> None:
        screen = self.dashboard_window.screen() or QApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            profile = build_display_profile(
                geometry.width(),
                geometry.height(),
                self._local_ui_scale(),
            )
            self.dashboard_window.apply_display_profile(profile)
        self.dashboard_window.setWindowState(
            self.dashboard_window.windowState() | Qt.WindowState.WindowMaximized
        )
        self.dashboard_window.showMaximized()

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
        self._last_backend_restart_notice_id = ""
        self.session.clear()
        self.show_login()

    def refresh_active_module(self) -> None:
        self.load_module(self.active_module)


def _build_restart_command(argv: list[str] | None = None) -> list[str]:
    active_argv = list(argv or sys.argv)
    entrypoint = (
        active_argv[0] if active_argv else str(PROJECT_ROOT / "frontend" / "app" / "main.py")
    )
    if entrypoint.endswith((".py", ".pyw")):
        entrypoint = str(Path(entrypoint).resolve())
    return [sys.executable, entrypoint, *active_argv[1:]]


def _restart_frontend_process(argv: list[str] | None = None) -> None:
    command = _build_restart_command(argv)
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(
            subprocess,
            "DETACHED_PROCESS",
            0,
        )
        if creationflags:
            subprocess.Popen(
                command,
                cwd=str(PROJECT_ROOT),
                creationflags=creationflags,
            )
            return
    subprocess.Popen(command, cwd=str(PROJECT_ROOT))


def main() -> int:
    app = ProCoreApplication()
    exit_code = app.run()
    if app._restart_requested:
        _restart_frontend_process()
        return 0
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
