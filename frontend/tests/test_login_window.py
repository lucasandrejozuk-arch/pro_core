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


def test_login_window_applies_backend_cover_only_when_connected(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)
    image_data_url = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhg"
        "GAWjR9awAAAABJRU5ErkJggg=="
    )

    window.apply_branding(
        {
            "login_cover_preset": "custom",
            "login_cover_image_data_url": image_data_url,
        }
    )

    assert window.brand_panel._cover_preset == "custom"
    assert window.brand_panel._cover_pixmap is not None

    window.apply_branding(
        {
            "login_cover_preset": "custom",
            "login_cover_image_data_url": image_data_url,
        },
        backend_connected=False,
    )

    assert window.brand_panel._cover_preset == "original"
    assert window.brand_panel._cover_pixmap is None


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


def test_login_window_uses_dedicated_forgot_password_style(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    assert window.forgot_password_button.objectName() == "forgotPasswordButton"


def test_login_window_updates_backend_connection_status(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    window.set_backend_connection_status(True)

    assert window.backend_status_label.text() == "Backend conectado."
    assert window.backend_status_label.property("level") == ""
    assert window.backend_connect_button.isHidden() is False

    window.set_backend_connection_status(False)

    assert window.backend_status_label.text() == "Backend indisponivel."
    assert window.backend_status_label.property("level") == "error"
    assert window.backend_connect_button.isHidden() is False


def test_login_window_guides_next_step_from_form_state(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    assert "email" in window.helper_label.text().lower()

    window.email_input.setText("operador@empresa.com")

    assert "senha" in window.helper_label.text().lower()

    window.password_input.setText("segredo123")

    assert "tudo pronto" in window.helper_label.text().lower()


def test_login_window_guidance_prioritizes_backend_recovery(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    window.set_backend_connection_status(False)

    assert "inicializar/reinicializar backend" in window.helper_label.text().lower()
    assert "backend" in window.helper_label.text().lower()


def test_login_window_backend_connect_button_emits_signal(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)
    emitted: list[bool] = []
    window.backend_connect_requested.connect(lambda: emitted.append(True))
    window.set_backend_connection_status(False)

    window.backend_connect_button.click()

    assert emitted == [True]


def test_login_window_backend_connect_loading_state(qtbot) -> None:
    window = LoginWindow()
    qtbot.addWidget(window)

    window.set_backend_connect_loading(True)

    assert window.backend_connect_button.isEnabled() is False
    assert window.backend_connect_button.text() == "Inicializando/Reiniciando..."

    window.set_backend_connect_loading(False)

    assert window.backend_connect_button.isEnabled() is True
    assert window.backend_connect_button.text() == "Inicializar/Reinicializar Backend"
