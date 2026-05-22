from __future__ import annotations

from frontend.app.themes.theme_override_base import _palette_override_base
from frontend.app.themes.theme_override_controls import _palette_override_controls


def _palette_overrides(palette: dict[str, str]) -> str:
    return _palette_override_base(palette) + _palette_override_controls(palette)
