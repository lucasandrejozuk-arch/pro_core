from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from frontend.app.core.backend_process import (
    ManagedBackendError,
    ManagedBackendProcess,
    ManagedBackendUnavailable,
)


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
