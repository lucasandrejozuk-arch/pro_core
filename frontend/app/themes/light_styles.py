from __future__ import annotations

from frontend.app.themes.light_style_controls import _light_controls_section
from frontend.app.themes.light_style_sections import _light_base_section


def _light_stylesheet() -> str:
    return _light_base_section() + _light_controls_section()
