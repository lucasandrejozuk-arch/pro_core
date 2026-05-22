from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from frontend.app.core.backend_process import (
    ManagedBackendError,
    ManagedBackendProcess,
    ManagedBackendUnavailable,
)
from frontend.app.handlers_admin import AdminHandlersMixin
from frontend.app.screens.dashboard import DashboardWindow


class FakeProcess:
    def __init__(self, *, running: bool = True, timeout_on_wait: bool = False) -> None:
        self.running = running
        self.timeout_on_wait = timeout_on_wait
        self.terminated = False
        self.killed = False
        self.wait_timeouts: list[float | None] = []

    def poll(self) -> int | None:
        return None if self.running else 0

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True
        self.running = False

    def wait(self, timeout: float | None = None) -> int:
        self.wait_timeouts.append(timeout)
        if self.timeout_on_wait and not self.killed:
            raise subprocess.TimeoutExpired("uvicorn", timeout)
        self.running = False
        return 0


class RecordingProcessFactory:
    def __init__(self, *processes: FakeProcess) -> None:
        self.processes = list(processes)
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, command: list[str], **kwargs: object) -> FakeProcess:
        self.calls.append((command, kwargs))
        return self.processes.pop(0)


class RecordingCommandRunner:
    def __init__(self, returncode: int = 0, stderr: str = "") -> None:
        self.returncode = returncode
        self.stderr = stderr
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, self.returncode, "", self.stderr)


def test_managed_backend_restart_refuses_unowned_process(tmp_path: Path) -> None:
    factory = RecordingProcessFactory(FakeProcess())
    controller = ManagedBackendProcess(tmp_path, process_factory=factory)

    with pytest.raises(ManagedBackendUnavailable) as exc_info:
        controller.restart()

    assert "nao foi iniciado pelo app" in str(exc_info.value)
    assert factory.calls == []


def test_managed_backend_restart_terminates_only_owned_process(tmp_path: Path) -> None:
    owned_process = FakeProcess()
    replacement_process = FakeProcess()
    factory = RecordingProcessFactory(owned_process, replacement_process)
    controller = ManagedBackendProcess(
        tmp_path,
        python_executable="python-test",
        port=8123,
        terminate_timeout_seconds=3,
        process_factory=factory,
    )

    controller.start()
    controller.restart()

    assert owned_process.terminated is True
    assert owned_process.killed is False
    assert owned_process.wait_timeouts == [3]
    assert controller.is_running is True
    assert len(factory.calls) == 2
    restart_command, restart_kwargs = factory.calls[1]
    assert restart_command == [
        "python-test",
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8123",
    ]
    assert restart_kwargs["cwd"] == str(tmp_path)


def test_managed_backend_restart_kills_only_owned_process_after_timeout(tmp_path: Path) -> None:
    stuck_process = FakeProcess(timeout_on_wait=True)
    replacement_process = FakeProcess()
    factory = RecordingProcessFactory(stuck_process, replacement_process)
    controller = ManagedBackendProcess(
        tmp_path,
        terminate_timeout_seconds=1,
        process_factory=factory,
    )

    controller.start()
    controller.restart()

    assert stuck_process.terminated is True
    assert stuck_process.killed is True
    assert stuck_process.wait_timeouts == [1, 1]
    assert len(factory.calls) == 2


def test_managed_backend_restart_applies_migrations_before_start(tmp_path: Path) -> None:
    owned_process = FakeProcess()
    replacement_process = FakeProcess()
    factory = RecordingProcessFactory(owned_process, replacement_process)
    runner = RecordingCommandRunner()
    controller = ManagedBackendProcess(
        tmp_path,
        python_executable="python-test",
        process_factory=factory,
        command_runner=runner,
    )

    controller.start()
    controller.restart(apply_migrations=True)

    assert owned_process.terminated is True
    assert len(runner.calls) == 1
    migration_command, migration_kwargs = runner.calls[0]
    assert migration_command == ["python-test", "-m", "alembic", "upgrade", "head"]
    assert migration_kwargs["cwd"] == str(tmp_path)
    assert factory.calls[1][0][2] == "uvicorn"
    assert controller.is_running is True


def test_managed_backend_restart_attempts_to_restore_backend_when_migration_fails(
    tmp_path: Path,
) -> None:
    owned_process = FakeProcess()
    restored_process = FakeProcess()
    factory = RecordingProcessFactory(owned_process, restored_process)
    runner = RecordingCommandRunner(returncode=1, stderr="migration failed")
    controller = ManagedBackendProcess(
        tmp_path,
        process_factory=factory,
        command_runner=runner,
    )

    controller.start()

    with pytest.raises(ManagedBackendError) as exc_info:
        controller.restart(apply_migrations=True)

    assert "Falha ao aplicar migrations" in str(exc_info.value)
    assert "migration failed" in str(exc_info.value)
    assert owned_process.terminated is True
    assert len(runner.calls) == 1
    assert len(factory.calls) == 2
    assert controller.is_running is True


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
        self.info_messages: list[str] = []
        self.error_messages: list[str] = []
        self.email_input = SimpleNamespace(text=lambda: "tech@example.com")

    def set_backend_reconnect_loading(self, is_loading: bool) -> None:
        self.loading.append(is_loading)

    def set_info(self, message: str) -> None:
        self.info_messages.append(message)

    def set_error(self, message: str) -> None:
        self.error_messages.append(message)


class FakeRestartController:
    def __init__(self, exc: ManagedBackendError | None = None) -> None:
        self.exc = exc
        self.restart_calls = 0
        self.apply_migrations_values: list[bool] = []

    def restart(self, *, apply_migrations: bool = False) -> None:
        self.restart_calls += 1
        self.apply_migrations_values.append(apply_migrations)
        if self.exc is not None:
            raise self.exc


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


def test_login_backend_reconnect_handler_success_sets_info(monkeypatch) -> None:
    monkeypatch.setattr(
        "frontend.app.handlers_admin.QApplication.processEvents",
        lambda *args, **kwargs: None,
    )
    controller = FakeRestartController()
    app = FakeApp(role="manager", backend_process=controller, token=None)
    app._request_backend_restart_authorization = lambda *args, **kwargs: {
        "reason": "Manutencao programada"
    }
    app.backend_health_connected = True

    app.handle_login_backend_reconnect()

    assert controller.restart_calls == 1
    assert controller.apply_migrations_values == [True]
    assert app.login_window.loading == [True, False]
    assert app.login_window.info_messages == [
        "Tentando conectar/reiniciar backend. Motivo: Manutencao programada.",
        "Backend conectado e reiniciado com sucesso.",
    ]
    assert app.login_window.error_messages == []
    assert app.refreshed_backend_health is True
    assert app.synced_backend_status is True


def test_login_backend_reconnect_handler_unavailable_sets_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "frontend.app.handlers_admin.QApplication.processEvents",
        lambda *args, **kwargs: None,
    )
    controller = FakeRestartController(
        ManagedBackendUnavailable("Reinicio seguro indisponivel: backend externo.")
    )
    app = FakeApp(role="manager", backend_process=controller, token=None)
    app._request_backend_restart_authorization = lambda *args, **kwargs: {
        "reason": "Backend travado"
    }
    app.backend_health_connected = False

    app.handle_login_backend_reconnect()

    assert controller.restart_calls == 1
    assert controller.apply_migrations_values == [True]
    assert app.login_window.loading == [True, False]
    assert app.login_window.info_messages == [
        "Tentando conectar/reiniciar backend. Motivo: Backend travado."
    ]
    assert app.login_window.error_messages == ["Reinicio seguro indisponivel: backend externo."]
    assert app.refreshed_backend_health is True
    assert app.synced_backend_status is True
