from __future__ import annotations

from pathlib import Path

from frontend.app import main


def test_build_restart_command_normalizes_python_entrypoint(monkeypatch) -> None:
    monkeypatch.setattr(main.sys, "executable", "C:/venv/Scripts/python.exe")

    command = main._build_restart_command(["frontend/app/main.py", "--debug"])

    assert command[0] == "C:/venv/Scripts/python.exe"
    assert Path(command[1]).name == "main.py"
    assert command[2:] == ["--debug"]


def test_restart_frontend_process_spawns_new_process(monkeypatch) -> None:
    spawned: dict[str, object] = {}

    def fake_popen(command, **kwargs):
        spawned["command"] = command
        spawned["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(main.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(main.sys, "executable", "C:/venv/Scripts/python.exe")

    main._restart_frontend_process(["frontend/app/main.py", "--lang", "en-US"])

    assert spawned["command"][0] == "C:/venv/Scripts/python.exe"
    assert Path(spawned["command"][1]).name == "main.py"
    assert spawned["command"][2:] == ["--lang", "en-US"]
    assert spawned["kwargs"]["cwd"] == str(main.PROJECT_ROOT)


def test_run_stops_backend_process_on_frontend_shutdown() -> None:
    class _Probe:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    class _ApiClient:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    class _BackendProcess:
        def __init__(self) -> None:
            self.stopped = False

        def stop(self) -> None:
            self.stopped = True

    class _Timer:
        def __init__(self) -> None:
            self.stopped = False

        def stop(self) -> None:
            self.stopped = True

    class _Splash:
        def __init__(self) -> None:
            self.started = False

        def start(self) -> None:
            self.started = True

    class _App:
        def exec(self) -> int:
            return 0

    application = main.ProCoreApplication.__new__(main.ProCoreApplication)
    application.splash = _Splash()
    application.qt_app = _App()
    application.backend_health_timer = _Timer()
    application.backend_health_probe = _Probe()
    application.api_client = _ApiClient()
    application.backend_process = _BackendProcess()

    result = application.run()

    assert result == 0
    assert application.splash.started is True
    assert application.backend_health_timer.stopped is True
    assert application.backend_health_probe.closed is True
    assert application.api_client.closed is True
    assert application.backend_process.stopped is True
