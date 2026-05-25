from __future__ import annotations

from frontend.app.core.display import build_display_profile
from frontend.app.core.icons import build_app_icon, build_icon
from frontend.app.themes.styles import build_theme_palette
from frontend.app.themes.theme_overrides import _palette_overrides


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


def test_display_profile_reduces_dashboard_density_for_high_scale() -> None:
    profile = build_display_profile(1920, 1080, 1.5)

    assert profile.ui_scale == 1.5
    assert profile.ui_scale_max == 1.5
    assert profile.dashboard_columns == 2
    assert profile.should_maximize is True


def test_theme_palette_uses_named_palette() -> None:
    palette = build_theme_palette("light", "green")

    assert palette["primary"] == "#0f766e"
    assert palette["color_palette"] == "green"
    assert palette["app_bg"] == "#edf8f5"
    assert palette["surface"] == "#ffffff"
    assert palette["button_text"] in {"#111827", "#ffffff"}


def test_theme_palette_rejects_invalid_palette() -> None:
    palette = build_theme_palette("dark", "azul")

    assert palette["primary"] == "#38bdf8"
    assert palette["color_palette"] == "blue"
    assert palette["app_bg"].startswith("#")


def test_theme_palette_maps_legacy_primary_color_to_nearest_palette() -> None:
    palette = build_theme_palette("light", "#0f766e")

    assert palette["color_palette"] == "green"
    assert palette["primary"] == "#0f766e"


def test_theme_palette_keeps_selection_readable() -> None:
    palette = build_theme_palette("dark", "green")

    assert palette["selection_bg"] == "#0f766e"
    assert palette["selection_text"] in {"#111827", "#ffffff"}


def test_theme_palette_selects_safe_monochrome_icon_library() -> None:
    light_palette = build_theme_palette("light", "amber")
    dark_palette = build_theme_palette("dark", "amber")

    assert light_palette["icon_library"] == "graphite"
    assert light_palette["sidebar_icon"] == "#172033"
    assert dark_palette["icon_library"] == "paper"
    assert dark_palette["sidebar_icon"] == "#f8fafc"


def test_application_icons_are_available(qtbot) -> None:
    assert not build_icon("dashboard").isNull()
    assert not build_app_icon().isNull()


def test_sidebar_active_navigation_uses_binder_tab_frame() -> None:
    stylesheet = _palette_overrides(build_theme_palette("dark", "blue"))

    assert 'QPushButton#navButton[active="true"]' in stylesheet
    assert "border-right: 0;" in stylesheet
    assert "border-top-right-radius: 0;" in stylesheet
    assert "border-bottom-right-radius: 0;" in stylesheet


def test_top_command_bar_uses_binder_tab_style() -> None:
    stylesheet = _palette_overrides(build_theme_palette("dark", "green"))

    assert "QLabel#topCommandContextTab" in stylesheet
    assert "QPushButton#topCommandButton" in stylesheet
    assert "QLabel#listCountBadge" in stylesheet
    assert "border-top: 3px solid" in stylesheet
    assert "border-bottom: 0;" in stylesheet


def test_theme_overrides_include_hover_feedback() -> None:
    stylesheet = _palette_overrides(build_theme_palette("light", "cyan"))

    assert "QPushButton#navButton:hover" in stylesheet
    assert "QTableWidget::item:hover" in stylesheet
    assert "QFrame#contentPanel:hover" not in stylesheet
    assert "QFrame#recordListPanel:hover" not in stylesheet
