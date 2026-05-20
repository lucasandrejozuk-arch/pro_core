from __future__ import annotations

from frontend.app.core.display import build_display_profile
from frontend.app.core.icons import build_app_icon, build_icon
from frontend.app.themes.styles import build_theme_palette


def test_display_profile_detects_compact_monitor() -> None:
    profile = build_display_profile(1366, 768)

    assert profile.compact is True
    assert profile.should_maximize is True
    assert profile.dashboard_columns == 2
    assert 58 <= profile.sidebar_width <= 74
    assert 32 <= profile.collapsed_sidebar_width <= 38
    assert 14 <= profile.content_margin <= 28
    assert 10 <= profile.section_spacing <= 18
    assert profile.ui_scale_min <= profile.ui_scale <= profile.ui_scale_max


def test_display_profile_uses_wide_layout_for_large_monitor() -> None:
    profile = build_display_profile(1920, 1080)

    assert profile.compact is False
    assert profile.should_maximize is False
    assert profile.dashboard_columns == 4
    assert build_display_profile(1920, 1080, 1.21).ui_scale == 1.21


def test_theme_palette_derives_background_from_primary_color() -> None:
    palette = build_theme_palette("light", "#0f766e")

    assert palette["primary"] == "#0f766e"
    assert palette["app_bg"] != "#f6f8fa"
    assert palette["surface"] != "#ffffff"
    assert palette["button_text"] in {"#111827", "#ffffff"}


def test_theme_palette_rejects_invalid_primary_color() -> None:
    palette = build_theme_palette("dark", "azul")

    assert palette["primary"] == "#1f6feb"
    assert palette["app_bg"].startswith("#")


def test_theme_palette_keeps_selection_readable() -> None:
    palette = build_theme_palette("dark", "#0f766e")

    assert palette["selection_bg"] == "#0f766e"
    assert palette["selection_text"] in {"#111827", "#ffffff"}


def test_application_icons_are_available() -> None:
    assert not build_icon("dashboard").isNull()
    assert not build_app_icon().isNull()
