from __future__ import annotations

from frontend.app.screens.dashboard_content import build_dashboard_content
from frontend.app.screens.dashboard_footer import build_dashboard_footer
from frontend.app.screens.dashboard_sidebar import build_dashboard_sidebar


def build_dashboard_layout(window) -> None:
    build_dashboard_sidebar(window)
    scroll_area = build_dashboard_content(window)
    build_dashboard_footer(window, scroll_area)
