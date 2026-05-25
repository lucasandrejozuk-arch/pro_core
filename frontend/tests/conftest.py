from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QSettings

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def _reset_frontend_language() -> None:
    settings = QSettings("PRO CORE", "PRO CORE")
    settings.setValue("appearance/language", "pt-BR")
    settings.sync()
    yield
