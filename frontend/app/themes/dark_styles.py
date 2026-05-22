from __future__ import annotations

from frontend.app.themes.dark_style_controls import _dark_controls_section
from frontend.app.themes.dark_style_sections import _dark_base_section


def _dark_stylesheet() -> str:
    return _dark_base_section() + _dark_controls_section()
