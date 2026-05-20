from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QWidget


@dataclass(frozen=True)
class DisplayProfile:
    width: int
    height: int
    aspect_ratio: float
    ui_scale: float
    ui_scale_min: float
    ui_scale_max: float
    compact: bool
    should_maximize: bool
    sidebar_width: int
    collapsed_sidebar_width: int
    content_margin: int
    section_spacing: int
    dashboard_columns: int


def detect_display_profile() -> DisplayProfile:
    screen = QApplication.primaryScreen()
    if screen is None:
        return build_display_profile(1366, 768)

    geometry = screen.availableGeometry()
    return build_display_profile(geometry.width(), geometry.height())


def build_display_profile(
    width: int,
    height: int,
    ui_scale_override: float | None = None,
) -> DisplayProfile:
    safe_width = max(320, int(width))
    safe_height = max(320, int(height))
    aspect_ratio = safe_width / safe_height
    compact = safe_width < 1360 or safe_height < 820 or aspect_ratio < 1.45
    if compact:
        ui_scale_min, ui_scale_max = 0.82, 1.04
    elif safe_width >= 1900 and safe_height >= 1000:
        ui_scale_min, ui_scale_max = 0.88, 1.22
    else:
        ui_scale_min, ui_scale_max = 0.86, 1.14
    detected_scale = min(safe_width / 1600, safe_height / 900)
    ui_scale = _clamp(
        ui_scale_override if ui_scale_override is not None else detected_scale,
        ui_scale_min,
        ui_scale_max,
    )
    should_maximize = safe_width < 1440 or safe_height < 840
    dashboard_columns = 2 if compact or safe_width < 1500 else 4

    return DisplayProfile(
        width=safe_width,
        height=safe_height,
        aspect_ratio=aspect_ratio,
        ui_scale=ui_scale,
        ui_scale_min=ui_scale_min,
        ui_scale_max=ui_scale_max,
        compact=compact,
        should_maximize=should_maximize,
        sidebar_width=int(_clamp(round(68 * ui_scale), 58, 74)),
        collapsed_sidebar_width=int(_clamp(round(36 * ui_scale), 32, 38)),
        content_margin=int(_clamp(round(22 * ui_scale), 14, 28)),
        section_spacing=int(_clamp(round(14 * ui_scale), 10, 18)),
        dashboard_columns=dashboard_columns,
    )


def prepare_window_for_display(
    window: QWidget,
    preferred_size: QSize | tuple[int, int],
    minimum_size: QSize | tuple[int, int],
    *,
    margin: int = 48,
) -> DisplayProfile:
    profile = detect_display_profile()
    preferred_width, preferred_height = _as_size_tuple(preferred_size)
    minimum_width, minimum_height = _as_size_tuple(minimum_size)
    available_width = max(320, profile.width - margin)
    available_height = max(320, profile.height - margin)

    window.setMinimumSize(
        min(minimum_width, available_width),
        min(minimum_height, available_height),
    )
    target_width = min(preferred_width, int(profile.width * 0.92), available_width)
    target_height = min(preferred_height, int(profile.height * 0.90), available_height)
    window.resize(
        max(window.minimumWidth(), target_width),
        max(window.minimumHeight(), target_height),
    )

    screen = QApplication.primaryScreen()
    if screen is not None:
        geometry = screen.availableGeometry()
        frame = window.frameGeometry()
        frame.moveCenter(geometry.center())
        window.move(frame.topLeft())

    return profile


def _as_size_tuple(size: QSize | tuple[int, int]) -> tuple[int, int]:
    if isinstance(size, QSize):
        return size.width(), size.height()
    return size


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))
