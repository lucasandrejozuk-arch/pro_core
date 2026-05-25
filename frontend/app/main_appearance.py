from __future__ import annotations

from frontend.app.core.api_client import ApiError
from frontend.app.core.i18n import apply_language_to_widgets, normalize_language
from frontend.app.themes.styles import DEFAULT_COLOR_PALETTE, apply_theme, build_theme_palette


class ProCoreAppearanceMixin:
    def _cached_login_branding_settings(self) -> dict[str, str]:
        return {
            "brand_name": str(self.local_settings.value("appearance/brand_name", "") or ""),
            "brand_subtitle": str(self.local_settings.value("appearance/brand_subtitle", "") or ""),
            "login_cover_preset": str(
                self.local_settings.value("appearance/login_cover_preset", "original") or "original"
            ),
            "login_cover_image_data_url": str(
                self.local_settings.value("appearance/login_cover_image_data_url", "") or ""
            ),
        }

    def _has_cached_login_branding(self) -> bool:
        cached = self._cached_login_branding_settings()
        return bool(
            cached["brand_name"].strip()
            or cached["brand_subtitle"].strip()
            or cached["login_cover_image_data_url"].strip()
            or cached["login_cover_preset"] != "original"
        )

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
        self._apply_runtime_language(settings.get("language"))

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
            self.dashboard_window.apply_sidebar_icon_color(palette["sidebar_icon"])
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
        self.local_settings.setValue(
            "appearance/login_cover_preset",
            str(settings.get("login_cover_preset") or "original"),
        )
        login_cover_image_data_url = str(settings.get("login_cover_image_data_url") or "")
        if login_cover_image_data_url:
            self.local_settings.setValue(
                "appearance/login_cover_image_data_url",
                login_cover_image_data_url,
            )
        else:
            self.local_settings.remove("appearance/login_cover_image_data_url")
        self.login_window.apply_branding(settings, backend_connected=True)
        self._apply_runtime_language(settings.get("language"))

    def _apply_cached_login_branding(self) -> None:
        self.login_window.apply_branding(
            self._cached_login_branding_settings(),
            backend_connected=bool(getattr(self, "backend_health_connected", False)),
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

    def _apply_runtime_language(self, language: str | None = None) -> None:
        active_language = normalize_language(
            str(language or self.local_settings.value("appearance/language", "pt-BR") or "pt-BR")
        )
        apply_language_to_widgets(
            active_language,
            getattr(self, "splash", None),
            getattr(self, "login_window", None),
            getattr(self, "password_window", None),
            getattr(self, "dashboard_window", None),
        )

    def _local_ui_scale(self) -> float:
        try:
            raw_value = self.local_settings.value("appearance/ui_scale", 1.0)
            return float(str(raw_value or 1.0))
        except (TypeError, ValueError):
            return 1.0
