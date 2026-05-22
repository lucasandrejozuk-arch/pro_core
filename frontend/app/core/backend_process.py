from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


class ManagedBackendError(RuntimeError):
    """Base error for local backend process management."""


class ManagedBackendUnavailable(ManagedBackendError):
    """Raised when the current backend process is not owned by this app."""


class ProcessLike(Protocol):
    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...

    def kill(self) -> None: ...

    def wait(self, timeout: float | None = None) -> int: ...


ProcessFactory = Callable[..., ProcessLike]
CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass
class ManagedBackendProcess:
    project_root: Path
    python_executable: str = sys.executable
    host: str = "127.0.0.1"
    port: int = 8000
    terminate_timeout_seconds: float = 8.0
    migration_timeout_seconds: float = 60.0
    process_factory: ProcessFactory = subprocess.Popen
    command_runner: CommandRunner = subprocess.run
    _process: ProcessLike | None = field(default=None, init=False, repr=False)
    _started_by_app: bool = field(default=False, init=False, repr=False)

    @property
    def command(self) -> list[str]:
        return [
            self.python_executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            self.host,
            "--port",
            str(self.port),
        ]

    @property
    def is_managed(self) -> bool:
        return self._started_by_app and self._process is not None

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> None:
        if self.is_running:
            return

        kwargs: dict[str, object] = {
            "cwd": str(self.project_root),
            "env": os.environ.copy(),
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            self._process = self.process_factory(self.command, **kwargs)
        except OSError as exc:
            self._process = None
            self._started_by_app = False
            raise ManagedBackendError(f"Falha ao iniciar backend local: {exc}") from exc

        self._started_by_app = True

    def stop(self) -> None:
        if not self.is_managed:
            return
        process = self._process
        if process is None or process.poll() is not None:
            return

        process.terminate()
        try:
            process.wait(timeout=self.terminate_timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=self.terminate_timeout_seconds)

    @property
    def migration_command(self) -> list[str]:
        return [self.python_executable, "-m", "alembic", "upgrade", "head"]

    def restart(self, *, apply_migrations: bool = False) -> None:
        if not self.is_managed:
            raise ManagedBackendUnavailable(
                "Reinicio seguro indisponivel: backend atual nao foi iniciado pelo app."
            )

        self.stop()
        if apply_migrations:
            try:
                self._run_migrations()
            except ManagedBackendError:
                self.start()
                raise
        self.start()

    def _run_migrations(self) -> None:
        try:
            result = self.command_runner(
                self.migration_command,
                cwd=str(self.project_root),
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                timeout=self.migration_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ManagedBackendError(
                "Tempo limite ao aplicar migrations antes de reiniciar o backend."
            ) from exc
        except OSError as exc:
            raise ManagedBackendError(f"Falha ao executar migrations: {exc}") from exc

        if result.returncode != 0:
            detail = _command_output_summary(result)
            message = "Falha ao aplicar migrations antes de reiniciar o backend."
            if detail:
                message = f"{message} {detail}"
            raise ManagedBackendError(message)


def _command_output_summary(result: subprocess.CompletedProcess[str]) -> str:
    output = "\n".join(
        part.strip()
        for part in (result.stderr or "", result.stdout or "")
        if part and part.strip()
    ).strip()
    if not output:
        return ""
    return output.replace("\r", " ").replace("\n", " ")[-500:]
