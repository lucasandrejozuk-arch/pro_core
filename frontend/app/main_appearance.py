from __future__ import annotations

from frontend.app.core.api_client import ApiError
from frontend.app.themes.styles import DEFAULT_COLOR_PALETTE, apply_theme, build_theme_palette


class ProCoreAppearanceMixin:
    def _apply_saved_theme(self) -> None:
        if not self.session.access_token:
            return

        try:
            settings = self.api_client.get_appearance_settings(self.session.access_token)
        except ApiError:
            return

        self._remember_appearance(settings)
        self._apply_local_theme()
        self.dashboard_window.apply_branding(settings)

    def _apply_local_theme(self) -> None:
        theme = str(self.local_settings.value("appearance/theme", "light") or "light")
        color_palette = str(self.local_settings.value("appearance/color_palette", "") or "")
        if not color_palette:
            color_palette = str(self.local_settings.value("appearance/primary_color", "") or "")
        ui_scale = self._local_ui_scale()
        apply_theme(
            self.qt_app,
            theme,
            color_palette,
            ui_scale,
        )
        if hasattr(self, "dashboard_window"):
            palette = build_theme_palette(theme, color_palette)
            sidebar_icon_color = palette["text"] if theme == "light" else palette["button_text"]
            self.dashboard_window.apply_sidebar_icon_color(sidebar_icon_color)
            self.dashboard_window.apply_record_editor_icon_colors(
                palette["primary"],
                palette["button_text"],
            )

    def _remember_appearance(self, settings: dict) -> None:
        self.local_settings.setValue("appearance/theme", str(settings.get("theme") or "light"))
        self.local_settings.setValue(
            "appearance/color_palette",
            str(settings.get("color_palette") or DEFAULT_COLOR_PALETTE),
        )
        self.local_settings.remove("appearance/primary_color")
        self.local_settings.setValue("appearance/brand_name", str(settings.get("brand_name") or ""))
        self.local_settings.setValue(
            "appearance/brand_subtitle",
            str(settings.get("brand_subtitle") or ""),
        )
        self.local_settings.setValue(
            "appearance/language",
            str(settings.get("language") or "pt-BR"),
        )
        self.login_window.apply_branding(settings)

    def _apply_cached_login_branding(self) -> None:
        self.login_window.apply_branding(
            {
                "brand_name": self.local_settings.value("appearance/brand_name", ""),
                "brand_subtitle": self.local_settings.value("appearance/brand_subtitle", ""),
            }
        )

    def _refresh_login_branding(self) -> None:
        try:
            settings = self.api_client.get_login_appearance_settings()
        except ApiError:
            self.login_window.set_backend_connection_status(False)
            self._apply_cached_login_branding()
            return

        self.login_window.set_backend_connection_status(True)
        self._remember_appearance(settings)

    def _local_ui_scale(self) -> float:
        try:
            raw_value = self.local_settings.value("appearance/ui_scale", 1.0)
            return float(str(raw_value or 1.0))
        except (TypeError, ValueError):
            return 1.0
