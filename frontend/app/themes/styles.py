from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from frontend.app.themes.base_styles import _dark_stylesheet, _light_stylesheet
from frontend.app.themes.theme_overrides import _palette_overrides

type Rgb = tuple[int, int, int]

DEFAULT_COLOR_PALETTE = "blue"
COLOR_PALETTE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("blue", "Grafite tecnico"),
    ("green", "Verde operacional"),
    ("amber", "Ambar industrial"),
    ("ruby", "Rubi executivo"),
    ("cyan", "Ciano tecnico"),
)
ICON_COLOR_LIBRARIES: tuple[tuple[str, str, str], ...] = (
    ("paper", "Monocromatica clara", "#f8fafc"),
    ("graphite", "Monocromatica escura", "#172033"),
    ("cyan", "Monocromatica ciano", "#22d3ee"),
)

THEME_COLOR_PALETTES: dict[str, dict[str, dict[str, str]]] = {
    "light": {
        "blue": {
            "primary": "#25636f",
            "primary_hover": "#1d4f59",
            "primary_subtle": "#dff3f5",
            "app_bg": "#f3f7f8",
            "surface": "#ffffff",
            "surface_alt": "#eef4f5",
            "sidebar": "#d7e4e7",
            "panel": "#e7eff1",
            "line": "#bfced2",
            "text": "#111827",
            "muted": "#40565c",
            "input_bg": "#ffffff",
            "header_bg": "#ffffff",
            "status_bg": "#e1f1f3",
            "disabled_bg": "#8c959f",
            "selection_bg": "#dff3f5",
            "selection_text": "#111827",
        },
        "green": {
            "primary": "#0f766e",
            "primary_hover": "#0b5f59",
            "primary_subtle": "#d8f3ee",
            "app_bg": "#edf8f5",
            "surface": "#ffffff",
            "surface_alt": "#f2faf7",
            "sidebar": "#cde5df",
            "panel": "#e1f1ec",
            "line": "#accdc5",
            "text": "#10201d",
            "muted": "#3f5953",
            "input_bg": "#ffffff",
            "header_bg": "#ffffff",
            "status_bg": "#def7ef",
            "disabled_bg": "#8a9d98",
            "selection_bg": "#d8f3ee",
            "selection_text": "#10201d",
        },
        "amber": {
            "primary": "#9a6700",
            "primary_hover": "#7d4e00",
            "primary_subtle": "#fff3d6",
            "app_bg": "#fbf7ef",
            "surface": "#ffffff",
            "surface_alt": "#f7f0e3",
            "sidebar": "#eadcc4",
            "panel": "#f3eadb",
            "line": "#d8c7a9",
            "text": "#1f1b13",
            "muted": "#66563b",
            "input_bg": "#ffffff",
            "header_bg": "#ffffff",
            "status_bg": "#fff3d6",
            "disabled_bg": "#9c9588",
            "selection_bg": "#ffe8a3",
            "selection_text": "#1f1b13",
        },
        "ruby": {
            "primary": "#a12f42",
            "primary_hover": "#842436",
            "primary_subtle": "#ffe3e8",
            "app_bg": "#fbf4f5",
            "surface": "#ffffff",
            "surface_alt": "#f8edf0",
            "sidebar": "#ead2d7",
            "panel": "#f4e4e8",
            "line": "#d8bdc4",
            "text": "#201519",
            "muted": "#654850",
            "input_bg": "#ffffff",
            "header_bg": "#ffffff",
            "status_bg": "#ffe3e8",
            "disabled_bg": "#9a8b8f",
            "selection_bg": "#ffd5dd",
            "selection_text": "#201519",
        },
        "cyan": {
            "primary": "#087990",
            "primary_hover": "#056174",
            "primary_subtle": "#d8f5fb",
            "app_bg": "#f0f8fa",
            "surface": "#ffffff",
            "surface_alt": "#eaf5f7",
            "sidebar": "#cfe7ec",
            "panel": "#e2f1f4",
            "line": "#abcfd6",
            "text": "#102024",
            "muted": "#3f5960",
            "input_bg": "#ffffff",
            "header_bg": "#ffffff",
            "status_bg": "#d8f5fb",
            "disabled_bg": "#879ca0",
            "selection_bg": "#c8eef6",
            "selection_text": "#102024",
        },
    },
    "dark": {
        "blue": {
            "primary": "#38bdf8",
            "primary_hover": "#67d5ff",
            "primary_subtle": "#12313a",
            "app_bg": "#081113",
            "surface": "#101a1d",
            "surface_alt": "#17262a",
            "sidebar": "#081113",
            "panel": "#0d1b1f",
            "line": "#28434a",
            "text": "#e6edf7",
            "muted": "#91a7ad",
            "input_bg": "#0a1518",
            "header_bg": "#101a1d",
            "status_bg": "#12313a",
            "disabled_bg": "#2d444b",
            "selection_bg": "#25636f",
            "selection_text": "#ffffff",
        },
        "green": {
            "primary": "#0f766e",
            "primary_hover": "#14b8a6",
            "primary_subtle": "#123d38",
            "app_bg": "#071312",
            "surface": "#101d1b",
            "surface_alt": "#172925",
            "sidebar": "#081715",
            "panel": "#0d211f",
            "line": "#28423d",
            "text": "#e6f5f2",
            "muted": "#91aaa4",
            "input_bg": "#0a1715",
            "header_bg": "#101d1b",
            "status_bg": "#123d38",
            "disabled_bg": "#2d4641",
            "selection_bg": "#0f766e",
            "selection_text": "#ffffff",
        },
        "amber": {
            "primary": "#f2b84b",
            "primary_hover": "#ffd166",
            "primary_subtle": "#3a2b11",
            "app_bg": "#151107",
            "surface": "#211a0e",
            "surface_alt": "#2c2415",
            "sidebar": "#151107",
            "panel": "#1d170c",
            "line": "#4a3b20",
            "text": "#f7efe1",
            "muted": "#b8a98d",
            "input_bg": "#171207",
            "header_bg": "#211a0e",
            "status_bg": "#3a2b11",
            "disabled_bg": "#4a4235",
            "selection_bg": "#9a6700",
            "selection_text": "#ffffff",
        },
        "ruby": {
            "primary": "#ff8aa0",
            "primary_hover": "#ff9fb0",
            "primary_subtle": "#3b1720",
            "app_bg": "#15080c",
            "surface": "#221116",
            "surface_alt": "#2c1920",
            "sidebar": "#15080c",
            "panel": "#1d0d12",
            "line": "#4a2932",
            "text": "#faedf0",
            "muted": "#b99ca4",
            "input_bg": "#170b10",
            "header_bg": "#221116",
            "status_bg": "#3b1720",
            "disabled_bg": "#4a3a3e",
            "selection_bg": "#a12f42",
            "selection_text": "#ffffff",
        },
        "cyan": {
            "primary": "#22d3ee",
            "primary_hover": "#67e8f9",
            "primary_subtle": "#12343a",
            "app_bg": "#071314",
            "surface": "#101d1f",
            "surface_alt": "#17282b",
            "sidebar": "#071314",
            "panel": "#0d2023",
            "line": "#28464b",
            "text": "#e6f8fb",
            "muted": "#8fb0b6",
            "input_bg": "#0a1719",
            "header_bg": "#101d1f",
            "status_bg": "#12343a",
            "disabled_bg": "#2d464a",
            "selection_bg": "#087990",
            "selection_text": "#ffffff",
        },
    },
}


def apply_theme(
    app: QApplication,
    theme: str = "light",
    color_palette: str | None = None,
    ui_scale: float = 1.0,
) -> None:
    app.setFont(QFont("Segoe UI", max(8, min(round(9 * ui_scale), 12))))
    is_dark = theme == "dark"
    default_color = "#1f6feb" if is_dark else "#0969da"
    palette = build_theme_palette(theme, color_palette)
    accent_color = palette["primary"]
    stylesheet = _dark_stylesheet() if is_dark else _light_stylesheet()
    app.setStyleSheet(stylesheet.replace(default_color, accent_color) + _palette_overrides(palette))


def build_theme_palette(theme: str = "light", color_palette: str | None = None) -> dict[str, str]:
    theme_key = "dark" if theme == "dark" else "light"
    palette_id = resolve_color_palette(theme_key, color_palette)
    palette = dict(THEME_COLOR_PALETTES[theme_key][palette_id])
    primary = palette["primary"]
    icon_library_id, icon_library_label, sidebar_icon = _best_icon_library(palette["sidebar"])

    return {
        **palette,
        "color_palette": palette_id,
        "icon_library": icon_library_id,
        "icon_library_label": icon_library_label,
        "sidebar_icon": sidebar_icon,
        "button_text": _contrast_text(primary),
        "success": "#56d364" if theme_key == "dark" else "#1a7f37",
        "success_bg": "#10261a" if theme_key == "dark" else "#dafbe1",
        "warning": "#e3b341" if theme_key == "dark" else "#9a6700",
        "warning_bg": "#2d2305" if theme_key == "dark" else "#fff8c5",
        "danger": "#ff7b72" if theme_key == "dark" else "#cf222e",
        "danger_bg": "#2d1115" if theme_key == "dark" else "#ffebe9",
    }


def resolve_color_palette(theme: str = "light", color_palette: str | None = None) -> str:
    theme_key = "dark" if theme == "dark" else "light"
    value = (color_palette or "").strip().lower()
    if value in THEME_COLOR_PALETTES[theme_key]:
        return value

    legacy_color = _safe_hex_color(color_palette, "")
    if legacy_color:
        return _nearest_palette(theme_key, legacy_color)

    return DEFAULT_COLOR_PALETTE


def _nearest_palette(theme: str, color: str) -> str:
    target = _hex_to_rgb(color)
    distances = {
        palette_id: sum(
            (target_channel - palette_channel) ** 2
            for target_channel, palette_channel in zip(
                target,
                _hex_to_rgb(palette["primary"]),
                strict=True,
            )
        )
        for palette_id, palette in THEME_COLOR_PALETTES[theme].items()
    }
    return min(distances, key=distances.get)


def _best_icon_library(background: str) -> tuple[str, str, str]:
    return max(
        ICON_COLOR_LIBRARIES,
        key=lambda icon_library: _contrast_ratio(icon_library[2], background),
    )


def _safe_hex_color(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    color = value.strip()
    if len(color) != 7 or not color.startswith("#"):
        return fallback
    if any(character not in "0123456789abcdefABCDEF" for character in color[1:]):
        return fallback
    return color


def _hex_to_rgb(value: str) -> Rgb:
    return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)


def _rgb_to_hex(color: Rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(_clamp_channel(channel) for channel in color))


def _mix(first: str, second: str, second_weight: float) -> str:
    first_rgb = _hex_to_rgb(first)
    second_rgb = _hex_to_rgb(second)
    weight = max(0.0, min(second_weight, 1.0))
    return _rgb_to_hex(
        tuple(
            round(first_channel * (1.0 - weight) + second_channel * weight)
            for first_channel, second_channel in zip(first_rgb, second_rgb, strict=True)
        )
    )


def _contrast_text(background: str) -> str:
    return "#111827" if _contrast_ratio(background, "#111827") >= 4.5 else "#ffffff"


def _contrast_ratio(first: str, second: str) -> float:
    first_luminance = _relative_luminance(_hex_to_rgb(first))
    second_luminance = _relative_luminance(_hex_to_rgb(second))
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _relative_luminance(color: Rgb) -> float:
    channels = []
    for channel in color:
        normalized = channel / 255
        channels.append(
            normalized / 12.92 if normalized <= 0.03928 else ((normalized + 0.055) / 1.055) ** 2.4
        )
    red, green, blue = channels
    return (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)


def _clamp_channel(value: int | float) -> int:
    return max(0, min(round(value), 255))
