from __future__ import annotations

from PySide6.QtWidgets import QLineEdit

from frontend.app.core.grid import GRID_COLUMNS
from frontend.app.screens.login import LoginWindow


def test_login_window_applies_branding(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    window.apply_branding(
        {
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
        }
    )

    assert window.brand_label.text() == "Pro Assist"
    assert window.tagline_label.text() == "Laboratorio tecnico"
    assert window.windowTitle() == "Pro Assist"


def test_login_window_uses_12_column_grid(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    layout = window.layout()

    assert layout.columnCount() == GRID_COLUMNS
    assert layout.getItemPosition(0) == (0, 0, 1, 7)
    assert layout.getItemPosition(1) == (0, 7, 1, 5)


def test_login_window_toggles_password_visibility(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    assert window.password_input.echoMode() == QLineEdit.EchoMode.Password

    window.password_visibility_button.click()

    assert window.password_input.echoMode() == QLineEdit.EchoMode.Normal
    assert window.password_visibility_button.text() == "Ocultar senha"

    window.password_visibility_button.click()

    assert window.password_input.echoMode() == QLineEdit.EchoMode.Password
    assert window.password_visibility_button.text() == "Exibir senha"


def test_login_window_updates_backend_connection_status(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    window.set_backend_connection_status(True)

    assert window.backend_status_label.text() == "Backend conectado."
    assert window.backend_status_label.property("level") == ""

    window.set_backend_connection_status(False)

    assert window.backend_status_label.text() == "Backend indisponivel."
    assert window.backend_status_label.property("level") == "error"


def test_login_window_backend_reconnect_button_emits_signal(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)
    emitted: list[bool] = []
    window.backend_reconnect_requested.connect(lambda: emitted.append(True))

    window.backend_reconnect_button.click()

    assert emitted == [True]


def test_login_window_backend_reconnect_loading_state(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    window.set_backend_reconnect_loading(True)

    assert window.backend_reconnect_button.isEnabled() is False
    assert window.backend_reconnect_button.text() == "Conectando/Reiniciando..."

    window.set_backend_reconnect_loading(False)

    assert window.backend_reconnect_button.isEnabled() is True
    assert window.backend_reconnect_button.text() == "Conectar/Reiniciar backend"
