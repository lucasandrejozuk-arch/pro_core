from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from frontend.app.themes.base_styles import _dark_stylesheet, _light_stylesheet
from frontend.app.themes.theme_overrides import _palette_overrides

type Rgb = tuple[int, int, int]

DEFAULT_COLOR_PALETTE = "blue"
COLOR_PALETTE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("blue", "Azul tecnico"),
    ("green", "Verde operacional"),
)

THEME_COLOR_PALETTES: dict[str, dict[str, dict[str, str]]] = {
    "light": {
        "blue": {
            "primary": "#0969da",
            "primary_hover": "#0550ae",
            "primary_subtle": "#ddf4ff",
            "app_bg": "#eef6ff",
            "surface": "#ffffff",
            "surface_alt": "#f4f8fc",
            "sidebar": "#d3e4f8",
            "panel": "#e8f1fb",
            "line": "#b6c8da",
            "text": "#111827",
            "muted": "#3f5267",
            "input_bg": "#ffffff",
            "header_bg": "#ffffff",
            "status_bg": "#e5f2ff",
            "disabled_bg": "#8c959f",
            "selection_bg": "#ddf4ff",
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
    },
    "dark": {
        "blue": {
            "primary": "#1f6feb",
            "primary_hover": "#388bfd",
            "primary_subtle": "#102a43",
            "app_bg": "#0d1117",
            "surface": "#161b22",
            "surface_alt": "#21262d",
            "sidebar": "#0d1117",
            "panel": "#111827",
            "line": "#30363d",
            "text": "#e6edf7",
            "muted": "#8b949e",
            "input_bg": "#0f1117",
            "header_bg": "#161b22",
            "status_bg": "#102a43",
            "disabled_bg": "#30363d",
            "selection_bg": "#1f6feb",
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

    return {
        **palette,
        "color_palette": palette_id,
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
