from __future__ import annotations

from types import SimpleNamespace

from frontend.app.core.backend_process import (
    ManagedBackendError,
    ManagedBackendUnavailable,
)
from frontend.app.handlers_admin import AdminHandlersMixin
from frontend.app.main_runtime import ProCoreMainRuntimeMixin
from frontend.app.screens.dashboard import DashboardWindow


class FakeDashboard:
    def __init__(self) -> None:
        self.loading: list[bool] = []
        self.backend_status: list[tuple[bool, str | None, str | None]] = []
        self.internal_status: list[tuple[str, str]] = []
        self.restart_available: list[tuple[bool, str]] = []
        self.footer_messages: list[tuple[str, str]] = []

    def set_backend_restart_loading(self, is_loading: bool) -> None:
        self.loading.append(is_loading)

    def set_backend_connection_status(
        self,
        is_connected: bool,
        message: str | None = None,
        level: str | None = None,
    ) -> None:
        self.backend_status.append((is_connected, message, level))

    def set_internal_server_status(self, level: str, message: str) -> None:
        self.internal_status.append((level, message))

    def set_backend_restart_available(self, is_available: bool, message: str = "") -> None:
        self.restart_available.append((is_available, message))

    def _set_footer_message(self, message: str, level: str = "info") -> None:
        self.footer_messages.append((message, level))


class FakeLoginWindow:
    def __init__(self) -> None:
        self.loading: list[bool] = []
        self.connect_loading: list[bool] = []
        self.info_messages: list[str] = []
        self.error_messages: list[str] = []
        self.email_input = SimpleNamespace(text=lambda: "tech@example.com")
        self.visible = False

    def set_backend_reconnect_loading(self, is_loading: bool) -> None:
        self.loading.append(is_loading)

    def set_info(self, message: str) -> None:
        self.info_messages.append(message)

    def set_error(self, message: str) -> None:
        self.error_messages.append(message)

    def set_backend_connect_loading(self, is_loading: bool) -> None:
        self.connect_loading.append(is_loading)

    def isVisible(self) -> bool:
        return self.visible


class FakeRestartController:
    def __init__(
        self,
        exc: ManagedBackendError | None = None,
        *,
        start_exc: ManagedBackendError | None = None,
    ) -> None:
        self.exc = exc
        self.start_exc = start_exc
        self.restart_calls = 0
        self.start_calls = 0
        self.apply_migrations_values: list[bool] = []

    def restart(self, *, apply_migrations: bool = False) -> None:
        self.restart_calls += 1
        self.apply_migrations_values.append(apply_migrations)
        if self.exc is not None:
            raise self.exc

    def start(self) -> None:
        self.start_calls += 1
        if self.start_exc is not None:
            raise self.start_exc


class FakeApp(AdminHandlersMixin):
    def __init__(
        self,
        *,
        role: str,
        backend_process: FakeRestartController,
        token: str | None = "token",
    ) -> None:
        self.session = SimpleNamespace(access_token=token, user={"role": role})
        self.session.user["email"] = "user@example.com"
        self.dashboard_window = FakeDashboard()
        self.login_window = FakeLoginWindow()
        self.backend_process = backend_process
        self.login_shown = False
        self.synced_backend_status = False
        self.refreshed_backend_health = False
        self.backend_health_connected = False
        self.backend_restart_cooldown_until = 0.0

    def show_login(self) -> None:
        self.login_shown = True

    def _sync_backend_restart_status(self) -> None:
        self.synced_backend_status = True

    def refresh_backend_health_status(self) -> None:
        self.refreshed_backend_health = True


class FakeRuntimeApp(ProCoreMainRuntimeMixin):
    def __init__(self, *, token: str | None = "token", response: dict | None = None) -> None:
        self.session = SimpleNamespace(access_token=token)
        self.api_client = SimpleNamespace(
            poll_backend_restart_notice=lambda access_token, last_notice_id=None: response or {}
        )
        self._last_backend_restart_notice_id = ""
        self.dashboard_window = SimpleNamespace(isVisible=lambda: False)
        self.login_window = SimpleNamespace()


class FakeLoginConnectController:
    def __init__(self, *, start_exc: ManagedBackendError | None = None) -> None:
        self.start_exc = start_exc
        self.start_calls = 0
        self.restart_calls = 0
        self.is_running = False
        self.is_managed = True

    def start(self) -> None:
        self.start_calls += 1
        if self.start_exc is not None:
            raise self.start_exc
        self.is_running = True

    def restart(self, *, apply_migrations: bool = False) -> None:
        self.restart_calls += 1
        if self.start_exc is not None:
            raise self.start_exc
        self.is_running = True


class FakeLoginConnectApp(ProCoreMainRuntimeMixin):
    def __init__(
        self, *, statuses: list[bool], start_exc: ManagedBackendError | None = None
    ) -> None:
        self.backend_process = FakeLoginConnectController(start_exc=start_exc)
        self.backend_process_start_error = ""
        self.backend_health_connected = False
        self.login_window = FakeLoginWindow()
        self.dashboard_window = SimpleNamespace(
            set_backend_connection_status=lambda *args, **kwargs: None,
            set_internal_server_status=lambda *args, **kwargs: None,
            set_backend_restart_available=lambda *args, **kwargs: None,
            isVisible=lambda: False,
        )
        self.session = SimpleNamespace(access_token=None)
        self._status_sequence = iter(statuses)

    def refresh_backend_health_status(self) -> None:
        self.backend_health_connected = next(self._status_sequence, self.backend_health_connected)


def test_backend_restart_handler_blocks_non_admin_profiles() -> None:
    controller = FakeRestartController()
    app = FakeApp(role="manager", backend_process=controller)
    app._request_backend_restart_authorization = lambda *args, **kwargs: None

    app.handle_backend_restart()

    assert controller.restart_calls == 0
    assert app.dashboard_window.footer_messages == []


def test_backend_restart_handler_reports_unowned_backend_without_restart_side_effects() -> None:
    controller = FakeRestartController(
        ManagedBackendUnavailable("Reinicio seguro indisponivel: backend externo.")
    )
    app = FakeApp(role="admin", backend_process=controller)
    app._request_backend_restart_authorization = lambda *args, **kwargs: {
        "reason": "Manutencao programada"
    }

    app.handle_backend_restart()

    assert controller.restart_calls == 1
    assert controller.apply_migrations_values == [True]
    assert app.dashboard_window.loading == [True, False]
    assert app.dashboard_window.backend_status == [(False, "Backend: atualizando", "warning")]
    assert app.dashboard_window.internal_status == [
        ("warning", "Servidor interno: atualizando"),
        ("warning", "Servidor interno: externo"),
    ]
    assert app.dashboard_window.restart_available == [
        (False, "Reinicio seguro indisponivel: backend externo.")
    ]
    assert app.dashboard_window.footer_messages == [
        ("Aplicando migrations e reiniciando backend. Motivo: Manutencao programada.", "warning"),
        ("Reinicio seguro indisponivel: backend externo.", "warning"),
    ]
    assert app.synced_backend_status is False
    assert app.refreshed_backend_health is False


def test_backend_restart_handler_syncs_status_after_success() -> None:
    controller = FakeRestartController()
    app = FakeApp(role="admin", backend_process=controller)
    app._request_backend_restart_authorization = lambda *args, **kwargs: {
        "reason": "Backend travado"
    }

    app.handle_backend_restart()

    assert controller.restart_calls == 1
    assert controller.apply_migrations_values == [True]
    assert app.dashboard_window.loading == [True, False]
    assert app.dashboard_window.backend_status == [(False, "Backend: atualizando", "warning")]
    assert app.dashboard_window.internal_status == [("warning", "Servidor interno: atualizando")]
    assert app.refreshed_backend_health is True
    assert app.synced_backend_status is True
    assert app.dashboard_window.footer_messages == [
        ("Aplicando migrations e reiniciando backend. Motivo: Backend travado.", "warning"),
        ("Backend atualizado, migrations aplicadas e servico reconectado.", "success"),
    ]


def test_admin_backend_restart_control_is_role_aware_and_emits(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[bool] = []
    window.backend_restart_requested.connect(lambda: emitted.append(True))

    window.set_backend_restart_available(True, "Reinicio seguro disponivel.")
    window.set_user({"full_name": "Gestor", "email": "gestor@example.com", "role": "manager"})
    window.render_admin_area()
    window.backend_restart_button.click()

    assert window.backend_restart_button.isEnabled() is False
    assert "restrito a administradores" in window.backend_restart_status_label.text()
    assert emitted == []

    window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})
    window.render_admin_area()
    window.backend_restart_button.click()

    assert window.backend_restart_button.isEnabled() is True
    assert window.backend_restart_status_label.text() == "Reinicio seguro disponivel."
    assert emitted == [True]

    window.set_backend_restart_loading(True)

    assert window.backend_restart_button.isEnabled() is False
    assert window.backend_restart_button.text() == "Reiniciando..."


def test_prime_backend_restart_notice_cursor_skips_historical_notice() -> None:
    app = FakeRuntimeApp(
        response={
            "has_notice": True,
            "notice": {"id": "notice-42", "reason": "Manutencao programada"},
        }
    )

    app._prime_backend_restart_notice_cursor()

    assert app._last_backend_restart_notice_id == "notice-42"


def test_login_backend_connect_starts_local_backend_and_confirms_when_health_recovers(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "frontend.app.main_runtime.QTimer.singleShot",
        lambda _delay, callback: callback(),
    )
    app = FakeLoginConnectApp(statuses=[False, True])

    app.handle_login_backend_connect()

    assert app.backend_process.start_calls == 1
    assert app.backend_process.restart_calls == 0
    assert app.login_window.connect_loading == [True, False]
    assert app.login_window.info_messages == [
        "Tentando inicializar/reinicializar backend...",
        "Backend conectado.",
    ]
    assert app.login_window.error_messages == []


def test_login_backend_connect_surfaces_start_failure() -> None:
    app = FakeLoginConnectApp(
        statuses=[False],
        start_exc=ManagedBackendError("Falha ao iniciar backend local."),
    )

    app.handle_login_backend_connect()

    assert app.backend_process.start_calls == 1
    assert app.backend_process.restart_calls == 0
    assert app.login_window.connect_loading == [True, False]
    assert app.login_window.info_messages == ["Tentando inicializar/reinicializar backend..."]
    assert app.login_window.error_messages == ["Falha ao iniciar backend local."]


def test_login_backend_connect_restarts_managed_running_backend(monkeypatch) -> None:
    monkeypatch.setattr(
        "frontend.app.main_runtime.QTimer.singleShot",
        lambda _delay, callback: callback(),
    )
    app = FakeLoginConnectApp(statuses=[True])
    app.backend_process.is_running = True
    app.backend_process.is_managed = True

    app.handle_login_backend_connect()

    assert app.backend_process.start_calls == 0
    assert app.backend_process.restart_calls == 1
    assert app.login_window.connect_loading == [True, False]
    assert app.login_window.info_messages == [
        "Tentando inicializar/reinicializar backend...",
        "Backend conectado.",
    ]
    assert app.login_window.error_messages == []
