from __future__ import annotations

from PySide6.QtGui import QIcon, QPixmap

ICON_PATHS = {
    "app": """
        <path d="M6 17V7l6-3 6 3v10l-6 3z"/>
        <path d="M9 9h6"/>
        <path d="M9 12h5"/>
        <path d="M9 15h3"/>
    """,
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
    "tools": """
        <path d="M14.7 6.3a4 4 0 0 0 3.1 4.8"/>
        <path d="M17.8 11.1 10.1 18.8a2.2 2.2 0 0 1-3.1 0"/>
        <path d="m7 18.8-1.8-1.8a2.2 2.2 0 0 1 0-3.1l7.7-7.7"/>
        <path d="M12.9 6.2a4 4 0 0 0 1.8.1"/>
        <path d="M16 4l4 4"/>
        <path d="M7.5 14.5l2 2"/>
    """,
    "financial": """
        <path d="M5 7h14"/>
        <path d="M5 12h14"/>
        <path d="M7 17h10"/>
        <path d="M8 4v16"/>
        <path d="M16 4v16"/>
    """,
    "reports": """
        <path d="M5 20V4"/>
        <path d="M5 20h15"/>
        <path d="M9 16v-5"/>
        <path d="M13 16V8"/>
        <path d="M17 16v-8"/>
    """,
    "notifications": """
        <path d="M6 8a6 6 0 0 1 12 0v5l2 3H4l2-3z"/>
        <path d="M10 20h4"/>
    """,
    "settings": """
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
    "users": """
        <circle cx="9" cy="8" r="3"/>
        <path d="M4 20c.8-4 3-6 5-6s4.2 2 5 6"/>
        <path d="M17 11v6"/>
        <path d="M14 14h6"/>
    """,
    "password_resets": """
        <rect x="5" y="10" width="14" height="10" rx="2"/>
        <path d="M8 10V7a4 4 0 0 1 7.6-1.8"/>
        <path d="M12 14v2"/>
    """,
    "sectors": """
        <rect x="4" y="4" width="6" height="6" rx="1.2"/>
        <rect x="14" y="4" width="6" height="6" rx="1.2"/>
        <rect x="9" y="14" width="6" height="6" rx="1.2"/>
        <path d="M10 7h4"/>
        <path d="M12 10v4"/>
    """,
    "audit_logs": """
        <rect x="5" y="4" width="14" height="16" rx="2"/>
        <path d="M8 8h8"/>
        <path d="M8 12h8"/>
        <path d="M8 16h5"/>
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
    "panel": """
        <rect x="5" y="5" width="14" height="14" rx="2"/>
        <path d="M9 5v14"/>
        <path d="M12 10h4"/>
        <path d="M12 14h3"/>
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
    return QIcon(_pixmap_from_svg(svg))


def build_app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 256 256">
            <defs>
                <linearGradient id="bg" x1="28" y1="22" x2="226" y2="232"
                                gradientUnits="userSpaceOnUse">
                    <stop stop-color="#1f6feb"/>
                    <stop offset="1" stop-color="#063b63"/>
                </linearGradient>
            </defs>
            <rect x="18" y="18" width="220" height="220" rx="46" fill="url(#bg)"/>
            <path d="M70 172V84l58-30 58 30v88l-58 30z"
                  fill="none" stroke="#ffffff" stroke-width="16"
                  stroke-linejoin="round"/>
            <path d="M96 100h66M96 128h54M96 156h36"
                  fill="none" stroke="#ffffff" stroke-width="14"
                  stroke-linecap="round"/>
        </svg>
        """
        icon.addPixmap(_pixmap_from_svg(svg))
    return icon


def _safe_color(value: str) -> str:
    color = value.strip()
    if len(color) != 7 or not color.startswith("#"):
        return "#ffffff"
    if any(character not in "0123456789abcdefABCDEF" for character in color[1:]):
        return "#ffffff"
    return color


def _pixmap_from_svg(svg: str) -> QPixmap:
    pixmap = QPixmap()
    pixmap.loadFromData(svg.encode("utf-8"), "SVG")
    return pixmap
