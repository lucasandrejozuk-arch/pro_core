from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtCore import QSettings

from frontend.app.main_appearance import ProCoreAppearanceMixin
from frontend.app.screens.login import LoginWindow


class FakeAppearanceApp(ProCoreAppearanceMixin):
    def __init__(self) -> None:
        self.local_settings = QSettings("PRO CORE", "PRO CORE")
        self.local_settings.clear()
        self.local_settings.sync()
        self.login_window = LoginWindow()
        self.dashboard_window = SimpleNamespace(
            apply_sidebar_icon_color=lambda *args, **kwargs: None,
            apply_record_editor_icon_colors=lambda *args, **kwargs: None,
            apply_branding=lambda *args, **kwargs: None,
        )
        self.backend_health_connected = True

    def _apply_runtime_language(self, language: str | None = None) -> None:
        self.applied_language = language


def test_cached_login_branding_restores_saved_cover_and_text(qtbot) -> None:
    app = FakeAppearanceApp()
    qtbot.addWidget(app.login_window)
    image_data_url = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhg"
        "GAWjR9awAAAABJRU5ErkJggg=="
    )

    app._remember_appearance(
        {
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "green",
            "theme": "dark",
            "language": "pt-BR",
            "login_cover_preset": "custom",
            "login_cover_image_data_url": image_data_url,
        }
    )
    app.login_window.apply_branding({}, backend_connected=False)

    app._apply_cached_login_branding()

    assert app.local_settings.value("appearance/login_cover_preset") == "custom"
    assert app.login_window.brand_label.text() == "Pro Assist"
    assert app.login_window.tagline_label.text() == "Laboratorio tecnico"
    assert app.login_window.brand_panel._cover_preset == "custom"
    assert app.login_window.brand_panel._cover_pixmap is not None


def test_cached_login_branding_falls_back_to_original_cover_when_backend_is_offline(qtbot) -> None:
    app = FakeAppearanceApp()
    qtbot.addWidget(app.login_window)
    image_data_url = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhg"
        "GAWjR9awAAAABJRU5ErkJggg=="
    )
    app.backend_health_connected = False

    app._remember_appearance(
        {
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "green",
            "theme": "dark",
            "language": "pt-BR",
            "login_cover_preset": "custom",
            "login_cover_image_data_url": image_data_url,
        }
    )

    app._apply_cached_login_branding()

    assert app.login_window.brand_panel._cover_preset == "original"
    assert app.login_window.brand_panel._cover_pixmap is None
