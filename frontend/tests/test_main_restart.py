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
