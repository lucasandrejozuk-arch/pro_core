from __future__ import annotations

from PySide6.QtGui import QIcon, QPixmap

ICON_PATHS = {
    "menu": """
        <path d="M4 6h16"/>
        <path d="M4 12h16"/>
        <path d="M4 18h16"/>
    """,
    "dashboard": """
        <rect x="4" y="4" width="7" height="7" rx="1.6"/>
        <rect x="13" y="4" width="7" height="7" rx="1.6"/>
        <rect x="4" y="13" width="7" height="7" rx="1.6"/>
        <rect x="13" y="13" width="7" height="7" rx="1.6"/>
    """,
    "service_orders": """
        <path d="M8 4h8"/>
        <path d="M9 3h6l1 3H8z"/>
        <rect x="5" y="5" width="14" height="16" rx="2"/>
        <path d="M8 11h8"/>
        <path d="M8 15h6"/>
    """,
    "customers": """
        <circle cx="9" cy="8" r="3"/>
        <path d="M4 20c.8-4 3-6 5-6s4.2 2 5 6"/>
        <circle cx="16.5" cy="9" r="2.4"/>
        <path d="M15 15c2 .4 3.6 2 4.2 5"/>
    """,
    "equipment": """
        <rect x="6" y="6" width="12" height="12" rx="2"/>
        <path d="M9 2v4"/>
        <path d="M15 2v4"/>
        <path d="M9 18v4"/>
        <path d="M15 18v4"/>
        <path d="M2 9h4"/>
        <path d="M2 15h4"/>
        <path d="M18 9h4"/>
        <path d="M18 15h4"/>
        <rect x="10" y="10" width="4" height="4" rx=".8"/>
    """,
    "inventory": """
        <path d="M4 7l8-4 8 4-8 4z"/>
        <path d="M4 7v10l8 4 8-4V7"/>
        <path d="M12 11v10"/>
        <path d="M8 5l8 4"/>
    """,
    "admin": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 2v3"/>
        <path d="M12 19v3"/>
        <path d="M4.9 4.9 7 7"/>
        <path d="M17 17l2.1 2.1"/>
        <path d="M2 12h3"/>
        <path d="M19 12h3"/>
        <path d="M4.9 19.1 7 17"/>
        <path d="M17 7l2.1-2.1"/>
    """,
    "logout": """
        <path d="M10 5H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4"/>
        <path d="M14 8l4 4-4 4"/>
        <path d="M18 12H9"/>
    """,
    "session": """
        <circle cx="12" cy="8" r="3.5"/>
        <path d="M5 21c1-4.5 3.4-7 7-7s6 2.5 7 7"/>
    """,
}


def build_icon(name: str, color: str = "#ffffff", size: int = 24) -> QIcon:
    icon_color = _safe_color(color)
    paths = ICON_PATHS.get(name, ICON_PATHS["dashboard"])
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
        <g fill="none"
           stroke="{icon_color}"
           stroke-width="1.9"
           stroke-linecap="round"
           stroke-linejoin="round">
            {paths}
        </g>
    </svg>
    """
    pixmap = QPixmap()
    pixmap.loadFromData(svg.encode("utf-8"), "SVG")
    return QIcon(pixmap)


def _safe_color(value: str) -> str:
    color = value.strip()
    if len(color) != 7 or not color.startswith("#"):
        return "#ffffff"
    if any(character not in "0123456789abcdefABCDEF" for character in color[1:]):
        return "#ffffff"
    return color
