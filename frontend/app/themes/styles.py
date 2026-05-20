from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

type Rgb = tuple[int, int, int]


def apply_theme(
    app: QApplication,
    theme: str = "light",
    primary_color: str | None = None,
    ui_scale: float = 1.0,
) -> None:
    app.setFont(QFont("Segoe UI", max(8, min(round(9 * ui_scale), 12))))
    is_dark = theme == "dark"
    default_color = "#1f6feb" if is_dark else "#0969da"
    accent_color = _safe_hex_color(primary_color, default_color)
    palette = build_theme_palette(theme, accent_color)
    stylesheet = _dark_stylesheet() if is_dark else _light_stylesheet()
    app.setStyleSheet(stylesheet.replace(default_color, accent_color) + _palette_overrides(palette))


def build_theme_palette(theme: str = "light", primary_color: str | None = None) -> dict[str, str]:
    is_dark = theme == "dark"
    fallback = "#1f6feb" if is_dark else "#0969da"
    primary = _safe_hex_color(primary_color, fallback)

    if is_dark:
        app_bg = _mix(primary, "#05070d", 0.82)
        surface = _mix(primary, "#111827", 0.82)
        surface_alt = _mix(primary, "#1f2937", 0.80)
        sidebar = _mix(primary, "#030712", 0.76)
        panel = _mix(primary, "#0b1220", 0.72)
        line = _mix(primary, "#374151", 0.70)
        text = "#f8fafc"
        muted = _mix(primary, "#cbd5e1", 0.72)
        primary_hover = _mix(primary, "#ffffff", 0.14)
        primary_subtle = _mix(primary, "#0b1220", 0.52)
        status_bg = _mix(primary, "#0b1220", 0.48)
        input_bg = _mix(primary, "#030712", 0.80)
        header_bg = surface
        disabled_bg = _mix(primary, "#475569", 0.76)
        selection_bg = primary
        selection_text = _contrast_text(primary)
    else:
        app_bg = _mix(primary, "#ffffff", 0.88)
        surface = _mix(primary, "#ffffff", 0.96)
        surface_alt = _mix(primary, "#ffffff", 0.91)
        sidebar = _mix(primary, "#ffffff", 0.84)
        panel = _mix(primary, "#ffffff", 0.82)
        line = _mix(primary, "#d0d7de", 0.78)
        text = "#111827"
        muted = _mix("#57606a", primary, 0.22)
        primary_hover = _mix(primary, "#000000", 0.16)
        primary_subtle = _mix(primary, "#ffffff", 0.84)
        status_bg = _mix(primary, "#ffffff", 0.82)
        input_bg = _mix(primary, "#ffffff", 0.98)
        header_bg = surface
        disabled_bg = _mix(primary, "#8c959f", 0.65)
        selection_bg = primary_subtle
        selection_text = text

    return {
        "primary": primary,
        "primary_hover": primary_hover,
        "primary_subtle": primary_subtle,
        "app_bg": app_bg,
        "surface": surface,
        "surface_alt": surface_alt,
        "sidebar": sidebar,
        "panel": panel,
        "line": line,
        "text": text,
        "muted": muted,
        "input_bg": input_bg,
        "header_bg": header_bg,
        "status_bg": status_bg,
        "disabled_bg": disabled_bg,
        "button_text": _contrast_text(primary),
        "selection_bg": selection_bg,
        "selection_text": selection_text,
        "success": "#56d364" if is_dark else "#1a7f37",
        "success_bg": "#10261a" if is_dark else "#dafbe1",
        "warning": "#e3b341" if is_dark else "#9a6700",
        "warning_bg": "#2d2305" if is_dark else "#fff8c5",
        "danger": "#ff7b72" if is_dark else "#cf222e",
        "danger_bg": "#2d1115" if is_dark else "#ffebe9",
    }


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


def _palette_overrides(palette: dict[str, str]) -> str:
    return f"""
        QWidget {{
            color: {palette["text"]};
            selection-background-color: {palette["selection_bg"]};
            selection-color: {palette["selection_text"]};
        }}
        QWidget#splash,
        QWidget#loginWindow,
        QWidget#passwordWindow,
        QWidget#dashboardWindow,
        QMessageBox,
        QDialog#adminMenuDialog,
        QDialog#assetDialog {{
            background-color: {palette["app_bg"]};
        }}
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta,
        QLabel#sidebarText {{
            color: {palette["muted"]};
        }}
        QLabel#dashboardGreeting,
        QLabel#dashboardCardLabel,
        QLabel#pageTitle,
        QLabel#formTitle,
        QLabel#sectionTitle,
        QLabel#cardTitle,
        QLabel#sidebarTitle {{
            color: {palette["text"]};
        }}
        QLabel#pageTitle {{
            font-size: 18px;
            font-weight: 700;
        }}
        QLabel#sectionTitle {{
            font-size: 13px;
            font-weight: 700;
        }}
        QLabel#dashboardGreeting {{
            font-size: 12px;
            font-weight: 600;
        }}
        QLabel#dashboardCardMarker,
        QLabel#formGroupTitle,
        QLabel#sidebarCaption {{
            font-size: 10px;
            font-weight: 700;
        }}
        QLabel#dashboardCardValue {{
            font-size: 24px;
            font-weight: 700;
        }}
        QLabel#dashboardCardLabel {{
            font-size: 11px;
            font-weight: 600;
        }}
        QLabel#formGroupTitle,
        QLabel#sidebarCaption {{
            color: {palette["muted"]};
        }}
        QLabel#sessionFooterText,
        QLabel#sessionFooterModule {{
            color: {palette["muted"]};
        }}
        QLabel#errorText {{
            color: {palette["danger"]};
        }}
        QMessageBox QLabel {{
            color: {palette["text"]};
            background-color: transparent;
        }}
        QLabel#statusBanner {{
            background-color: {palette["status_bg"]};
            border-color: {palette["primary"]};
            color: {palette["primary"]};
            font-weight: 600;
            padding: 6px 8px;
        }}
        QLabel#statusBanner[level="warning"] {{
            background-color: {palette["warning_bg"]};
            border-color: {palette["warning"]};
            color: {palette["warning"]};
        }}
        QLabel#statusBanner[level="error"] {{
            background-color: {palette["danger_bg"]};
            border-color: {palette["danger"]};
            color: {palette["danger"]};
        }}
        QLabel#workflowStep {{
            background-color: {palette["surface_alt"]};
            border-color: {palette["line"]};
            color: {palette["muted"]};
        }}
        QLabel#workflowStep[stage="active"] {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
            color: {palette["primary"]};
        }}
        QLabel#workflowStep[stage="done"] {{
            background-color: {palette["success_bg"]};
            border-color: {palette["success"]};
            color: {palette["success"]};
        }}
        QProgressBar {{
            background-color: {palette["surface_alt"]};
        }}
        QProgressBar::chunk {{
            background-color: {palette["primary"]};
        }}
        QFrame#brandPanel {{
            background-color: {palette["primary"]};
        }}
        QFrame#brandPanel QLabel#brandTitle {{
            color: {palette["button_text"]};
        }}
        QFrame#brandPanel QLabel#brandSubtitle {{
            color: {palette["button_text"]};
        }}
        QFrame#formPanel,
        QFrame#recordEditorPanel {{
            background-color: {palette["surface"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
        }}
        QFrame#moduleCard,
        QFrame#dashboardKpiCard,
        QFrame#dashboardAlertsFrame,
        QFrame#recordListPanel {{
            background-color: {palette["surface"]};
            border-color: {palette["line"]};
        }}
        QFrame#recordModuleContainer {{
            background-color: transparent;
            border: 0;
        }}
        QFrame#recordToggleRail {{
            background-color: {palette["surface"]};
            border-left: 1px solid {palette["line"]};
            border-right: 1px solid {palette["line"]};
        }}
        QFrame#headerBar {{
            background-color: transparent;
            border: 0;
        }}
        QFrame#formSubPanel,
        QFrame#workflowPanel,
        QFrame#dashboardAlertRow,
        QFrame#equipmentSection {{
            background-color: {palette["surface_alt"]};
            border-color: {palette["line"]};
        }}
        QFrame#sessionFooter {{
            background-color: {palette["surface"]};
            border-top-color: {palette["line"]};
        }}
        QFrame#dashboardKpiCard:hover {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
        }}
        QFrame#dashboardAlertRow {{
            border-left-color: {palette["primary"]};
        }}
        QFrame#dashboardAlertRow[level="warning"] {{
            border-left-color: {palette["warning"]};
        }}
        QFrame#dashboardAlertRow[level="error"] {{
            border-left-color: {palette["danger"]};
        }}
        QFrame#dashboardAlertRow[level="success"] {{
            border-left-color: {palette["success"]};
        }}
        QFrame#contentPanel {{
            background-color: {palette["surface"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
        }}
        QFrame#sidebar {{
            background-color: {palette["sidebar"]};
            border: 0;
            border-right: 1px solid {palette["line"]};
            border-radius: 0;
        }}
        QFrame#sidebarSeparator {{
            background-color: rgba(255, 255, 255, 0.24);
            border: 0;
            margin: 4px 8px;
        }}
        QLabel#sidebarSessionInfo {{
            background-color: {palette["surface"]};
            border-color: {palette["line"]};
            color: {palette["muted"]};
        }}
        QLineEdit,
        QComboBox,
        QTreeWidget,
        QTextEdit,
        QTabWidget::pane {{
            background-color: {palette["input_bg"]};
            border-color: {palette["line"]};
            border-radius: 4px;
            color: {palette["text"]};
            min-height: 26px;
            padding: 3px 8px;
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {palette["muted"]};
            min-height: 28px;
            padding: 4px 10px;
            border-bottom: 2px solid transparent;
        }}
        QTabBar::tab:selected {{
            color: {palette["text"]};
            border-bottom-color: {palette["primary"]};
        }}
        QSlider::groove:horizontal {{
            height: 4px;
            background-color: {palette["line"]};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            width: 16px;
            margin: -6px 0;
            background-color: {palette["primary"]};
            border-radius: 8px;
        }}
        QLineEdit#moduleSearch,
        QLineEdit#sectionSearch {{
            background-color: {palette["input_bg"]};
            border: 1px solid {palette["line"]};
            border-radius: 4px;
            padding: 4px 8px;
            min-height: 26px;
            color: {palette["text"]};
        }}
        QLineEdit#moduleSearch:focus,
        QLineEdit#sectionSearch:focus {{
            border-color: {palette["primary"]};
        }}
        QLineEdit:focus,
        QComboBox:focus {{
            border-color: {palette["primary"]};
        }}
        QComboBox QAbstractItemView {{
            background-color: {palette["surface"]};
            border-color: {palette["line"]};
            selection-background-color: {palette["selection_bg"]};
            selection-color: {palette["selection_text"]};
        }}
        QPushButton {{
            background-color: {palette["primary"]};
            color: {palette["button_text"]};
            border-radius: 4px;
            font-weight: 700;
            min-height: 26px;
            padding: 4px 9px;
        }}
        QPushButton:hover {{
            background-color: {palette["primary_hover"]};
        }}
        QPushButton:disabled {{
            background-color: {palette["disabled_bg"]};
            color: {palette["muted"]};
        }}
        QPushButton#secondaryButton {{
            background-color: {palette["surface_alt"]};
            color: {palette["text"]};
        }}
        QPushButton#secondaryButton:hover {{
            background-color: {palette["primary_subtle"]};
        }}
        QPushButton#dangerButton {{
            background-color: {palette["surface_alt"]};
            color: {palette["danger"]};
        }}
        QPushButton#dangerButton:hover {{
            background-color: {palette["danger_bg"]};
        }}
        QPushButton#sidebarToggleButton,
        QPushButton#sidebarFooterButton {{
            background-color: rgba(255, 255, 255, 0.14);
            border-radius: 6px;
            padding: 0;
            text-align: center;
        }}
        QPushButton#sidebarToggleButton:hover,
        QPushButton#sidebarFooterButton:hover {{
            background-color: rgba(255, 255, 255, 0.22);
        }}
        QPushButton#recordEditorToggleButton {{
            background-color: {palette["surface_alt"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
            color: {palette["primary"]};
            padding: 0;
            text-align: center;
        }}
        QPushButton#recordEditorToggleButton:hover {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
        }}
        QPushButton#recordEditorToggleButton[collapsed="false"] {{
            background-color: {palette["primary"]};
            border-color: {palette["primary"]};
            color: {palette["button_text"]};
        }}
        QPushButton#navButton {{
            background-color: transparent;
            border-radius: 6px;
            padding: 0;
            text-align: center;
            min-width: 42px;
            max-width: 42px;
            min-height: 42px;
            max-height: 42px;
        }}
        QPushButton#navButton:hover {{
            background-color: rgba(255, 255, 255, 0.16);
        }}
        QPushButton#navButton[active="true"] {{
            background-color: rgba(255, 255, 255, 0.26);
        }}
        QPushButton#adminMenuButton {{
            background-color: {palette["surface"]};
            border-color: {palette["line"]};
            color: {palette["text"]};
        }}
        QPushButton#adminMenuButton:hover {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
        }}
        QTableWidget#dataTable {{
            background-color: {palette["surface"]};
            alternate-background-color: {palette["surface_alt"]};
            border-color: {palette["line"]};
            border-radius: 6px;
            color: {palette["text"]};
            gridline-color: {palette["line"]};
        }}
        QHeaderView::section {{
            background-color: {palette["surface_alt"]};
            border-bottom-color: {palette["line"]};
            color: {palette["text"]};
            font-weight: 700;
            min-height: 26px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {palette["line"]};
        }}
        """


def _light_stylesheet() -> str:
    return """
        QWidget {
            color: #24292f;
            selection-background-color: #0969da;
            selection-color: #ffffff;
        }
        QWidget#splash,
        QWidget#loginWindow,
        QWidget#passwordWindow,
        QWidget#dashboardWindow {
            background: #f6f8fa;
        }
        QLabel#splashTitle,
        QLabel#brandTitle {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: 0;
        }
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta {
            color: #57606a;
            font-size: 14px;
        }
        QLabel#errorText {
            color: #b42318;
            font-weight: 600;
        }
        QLabel#formTitle,
        QLabel#pageTitle {
            font-size: 22px;
            font-weight: 800;
        }
        QLabel#sectionTitle {
            font-size: 16px;
            font-weight: 800;
        }
        QLabel#dashboardGreeting {
            color: #24292f;
            font-size: 14px;
            font-weight: 700;
        }
        QLabel#cardTitle {
            font-size: 15px;
            font-weight: 800;
        }
        QLabel#dashboardCardMarker {
            font-size: 10px;
            font-weight: 800;
        }
        QLabel#dashboardCardValue {
            font-size: 30px;
            font-weight: 800;
        }
        QLabel#dashboardCardLabel {
            color: #24292f;
            font-size: 12px;
            font-weight: 800;
        }
        QLabel#sidebarCaption {
            color: #8b949e;
            font-size: 11px;
            font-weight: 800;
        }
        QLabel#formGroupTitle {
            color: #57606a;
            font-size: 11px;
            font-weight: 800;
        }
        QLabel#workflowStep {
            background: #eaeef2;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            color: #57606a;
            font-size: 11px;
            font-weight: 800;
            min-height: 28px;
            padding: 0 8px;
        }
        QLabel#workflowStep[stage="active"] {
            background: #ddf4ff;
            border-color: #0969da;
            color: #0969da;
        }
        QLabel#workflowStep[stage="done"] {
            background: #dafbe1;
            border-color: #238636;
            color: #1a7f37;
        }
        QLabel#statusBanner {
            background: #ddf4ff;
            border: 1px solid #0969da;
            border-radius: 6px;
            color: #0969da;
            font-weight: 800;
            padding: 8px 10px;
        }
        QLabel#statusBanner[level="warning"] {
            background: #fff8c5;
            border-color: #d29922;
            color: #9a6700;
        }
        QLabel#statusBanner[level="error"] {
            background: #ffebe9;
            border-color: #da3633;
            color: #cf222e;
        }
        QProgressBar {
            height: 8px;
            border: 0;
            border-radius: 4px;
            background: #d0d7de;
        }
        QProgressBar::chunk {
            border-radius: 4px;
            background: #0969da;
        }
        QFrame#brandPanel {
            background: #0f1117;
        }
        QFrame#brandPanel QLabel#brandTitle {
            color: #ffffff;
        }
        QFrame#brandPanel QLabel#brandSubtitle {
            color: #8b949e;
        }
        QFrame#formPanel,
        QFrame#moduleCard {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
        }
        QFrame#formSubPanel,
        QFrame#workflowPanel {
            background: #f6f8fa;
            border: 1px solid #d0d7de;
            border-radius: 8px;
        }
        QFrame#equipmentSection {
            background: #ffffff;
            border: 0;
            border-radius: 6px;
        }
        QFrame#sessionFooter {
            background: #ffffff;
            border-top: 1px solid #d0d7de;
        }
        QLabel#sessionFooterText,
        QLabel#sessionFooterModule {
            color: #57606a;
            font-size: 11px;
            font-weight: 700;
        }
        QFrame#dashboardKpiCard,
        QFrame#dashboardAlertsFrame {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
        }
        QFrame#dashboardKpiCard:hover {
            border-color: #0969da;
            background: #f6f8fa;
        }
        QFrame#dashboardAlertRow {
            background: #f6f8fa;
            border: 1px solid #d0d7de;
            border-left: 5px solid #0969da;
            border-radius: 6px;
        }
        QFrame#dashboardAlertRow[level="warning"] {
            border-left-color: #d29922;
        }
        QFrame#dashboardAlertRow[level="error"] {
            border-left-color: #da3633;
        }
        QFrame#dashboardAlertRow[level="success"] {
            border-left-color: #238636;
        }
        QFrame#contentPanel {
            background: #f6f8fa;
            border: 0;
        }
        QFrame#headerBar {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
        }
        QFrame#sidebar {
            background: #ffffff;
            border-right: 1px solid #d0d7de;
        }
        QLabel#sidebarTitle {
            color: #24292f;
            font-size: 21px;
            font-weight: 800;
        }
        QLabel#sidebarText {
            color: #57606a;
        }
        QLabel#sidebarSessionInfo {
            background: #f6f8fa;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            color: #57606a;
            font-size: 12px;
            padding: 10px;
        }
        QLineEdit,
        QComboBox,
        QTreeWidget,
        QTextEdit {
            border: 1px solid #d0d7de;
            border-radius: 6px;
            padding: 0 12px;
            background: #ffffff;
            min-height: 38px;
        }
        QTextEdit#summaryText {
            padding: 10px 12px;
        }
        QLineEdit:focus,
        QComboBox:focus {
            border-color: #0969da;
        }
        QComboBox::drop-down {
            border: 0;
            width: 28px;
        }
        QComboBox QAbstractItemView {
            background: #ffffff;
            border: 1px solid #d0d7de;
            selection-background-color: #ddf4ff;
            selection-color: #24292f;
        }
        QCheckBox {
            spacing: 8px;
        }
        QPushButton {
            border: 0;
            border-radius: 6px;
            background: #0969da;
            color: #ffffff;
            font-weight: 800;
            min-height: 38px;
            padding: 0 14px;
        }
        QPushButton:hover {
            background: #0550ae;
        }
        QPushButton:disabled {
            background: #8c959f;
        }
        QPushButton#secondaryButton {
            background: #eaeef2;
            color: #24292f;
        }
        QPushButton#secondaryButton:hover {
            background: #d0d7de;
        }
        QPushButton#dangerButton {
            background: #f6f8fa;
            color: #cf222e;
        }
        QPushButton#dangerButton:hover {
            background: #ffebe9;
        }
        QPushButton#sidebarToggleButton {
            background: #eaeef2;
            color: #24292f;
            text-align: left;
            min-height: 32px;
            padding-left: 12px;
        }
        QPushButton#sidebarToggleButton:hover {
            background: #d0d7de;
        }
        QPushButton#navButton {
            background: transparent;
            color: #24292f;
            text-align: left;
            padding-left: 16px;
            min-height: 40px;
            border-radius: 8px;
        }
        QPushButton#navButton:hover {
            background: #eaeef2;
        }
        QPushButton#navButton[active="true"] {
            background: #0969da;
            color: #ffffff;
        }
        QPushButton#adminMenuButton {
            background: #ffffff;
            border: 1px solid #d0d7de;
            color: #24292f;
            text-align: left;
            min-height: 44px;
            padding-left: 14px;
        }
        QPushButton#adminMenuButton:hover {
            border-color: #0969da;
            background: #f6f8fa;
        }
        QTableWidget#dataTable {
            background: #ffffff;
            alternate-background-color: #f6f8fa;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            gridline-color: #d8dee4;
        }
        QHeaderView::section {
            background: #eaeef2;
            border: 0;
            border-bottom: 1px solid #d0d7de;
            padding: 8px;
            font-weight: 800;
        }
        QScrollArea {
            border: 0;
            background: transparent;
        }
        QScrollBar:vertical {
            width: 10px;
            background: transparent;
        }
        QScrollBar::handle:vertical {
            background: #afb8c1;
            border-radius: 5px;
            min-height: 36px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
        """


def _dark_stylesheet() -> str:
    return """
        QWidget {
            color: #e6edf7;
            selection-background-color: #1f6feb;
            selection-color: #ffffff;
        }
        QWidget#splash,
        QWidget#loginWindow,
        QWidget#passwordWindow,
        QWidget#dashboardWindow {
            background: #0f1117;
        }
        QLabel#splashTitle,
        QLabel#brandTitle {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: 0;
        }
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta {
            color: #8b949e;
            font-size: 14px;
        }
        QLabel#errorText {
            color: #ffb4ab;
            font-weight: 600;
        }
        QLabel#formTitle,
        QLabel#pageTitle {
            font-size: 22px;
            font-weight: 800;
        }
        QLabel#sectionTitle {
            font-size: 16px;
            font-weight: 800;
        }
        QLabel#dashboardGreeting {
            color: #e6edf7;
            font-size: 14px;
            font-weight: 700;
        }
        QLabel#cardTitle {
            font-size: 15px;
            font-weight: 800;
        }
        QLabel#dashboardCardMarker {
            font-size: 10px;
            font-weight: 800;
        }
        QLabel#dashboardCardValue {
            font-size: 30px;
            font-weight: 800;
        }
        QLabel#dashboardCardLabel {
            color: #e6edf7;
            font-size: 12px;
            font-weight: 800;
        }
        QLabel#sidebarCaption {
            color: #8b949e;
            font-size: 11px;
            font-weight: 800;
        }
        QLabel#formGroupTitle {
            color: #8b949e;
            font-size: 11px;
            font-weight: 800;
        }
        QLabel#workflowStep {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #8b949e;
            font-size: 11px;
            font-weight: 800;
            min-height: 28px;
            padding: 0 8px;
        }
        QLabel#workflowStep[stage="active"] {
            background: #102a43;
            border-color: #1f6feb;
            color: #79c0ff;
        }
        QLabel#workflowStep[stage="done"] {
            background: #10261a;
            border-color: #238636;
            color: #56d364;
        }
        QLabel#statusBanner {
            background: #102a43;
            border: 1px solid #1f6feb;
            border-radius: 6px;
            color: #79c0ff;
            font-weight: 800;
            padding: 8px 10px;
        }
        QLabel#statusBanner[level="warning"] {
            background: #2d2305;
            border-color: #d29922;
            color: #e3b341;
        }
        QLabel#statusBanner[level="error"] {
            background: #2d1115;
            border-color: #da3633;
            color: #ff7b72;
        }
        QProgressBar {
            height: 8px;
            border: 0;
            border-radius: 4px;
            background: #21262d;
        }
        QProgressBar::chunk {
            border-radius: 4px;
            background: #1f6feb;
        }
        QFrame#brandPanel {
            background: #161b22;
        }
        QFrame#brandPanel QLabel#brandTitle {
            color: #ffffff;
        }
        QFrame#brandPanel QLabel#brandSubtitle {
            color: #8b949e;
        }
        QFrame#formPanel,
        QFrame#moduleCard {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        QFrame#formSubPanel,
        QFrame#workflowPanel {
            background: #0f1117;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        QFrame#equipmentSection {
            background: #161b22;
            border: 0;
            border-radius: 6px;
        }
        QFrame#sessionFooter {
            background: #161b22;
            border-top: 1px solid #30363d;
        }
        QLabel#sessionFooterText,
        QLabel#sessionFooterModule {
            color: #8b949e;
            font-size: 11px;
            font-weight: 700;
        }
        QFrame#dashboardKpiCard,
        QFrame#dashboardAlertsFrame {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        QFrame#dashboardKpiCard:hover {
            border-color: #1f6feb;
            background: #21262d;
        }
        QFrame#dashboardAlertRow {
            background: #0f1117;
            border: 1px solid #30363d;
            border-left: 5px solid #1f6feb;
            border-radius: 6px;
        }
        QFrame#dashboardAlertRow[level="warning"] {
            border-left-color: #d29922;
        }
        QFrame#dashboardAlertRow[level="error"] {
            border-left-color: #da3633;
        }
        QFrame#dashboardAlertRow[level="success"] {
            border-left-color: #238636;
        }
        QFrame#contentPanel {
            background: #0f1117;
            border: 0;
        }
        QFrame#headerBar {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        QFrame#sidebar {
            background: #0b0f16;
            border-right: 1px solid #30363d;
        }
        QLabel#sidebarTitle {
            color: #ffffff;
            font-size: 21px;
            font-weight: 800;
        }
        QLabel#sidebarText {
            color: #8b949e;
        }
        QLabel#sidebarSessionInfo {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #8b949e;
            font-size: 12px;
            padding: 10px;
        }
        QLineEdit,
        QComboBox,
        QTreeWidget,
        QTextEdit {
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 0 12px;
            background: #0f1117;
            color: #e6edf7;
            min-height: 38px;
        }
        QTextEdit#summaryText {
            padding: 10px 12px;
        }
        QLineEdit:focus,
        QComboBox:focus {
            border-color: #1f6feb;
        }
        QComboBox::drop-down {
            border: 0;
            width: 28px;
        }
        QComboBox QAbstractItemView {
            background: #161b22;
            border: 1px solid #30363d;
            selection-background-color: #1f6feb;
            selection-color: #ffffff;
        }
        QCheckBox {
            spacing: 8px;
        }
        QPushButton {
            border: 0;
            border-radius: 6px;
            background: #1f6feb;
            color: #ffffff;
            font-weight: 800;
            min-height: 38px;
            padding: 0 14px;
        }
        QPushButton:hover {
            background: #388bfd;
        }
        QPushButton:disabled {
            background: #30363d;
            color: #8b949e;
        }
        QPushButton#secondaryButton {
            background: #21262d;
            color: #e6edf7;
        }
        QPushButton#secondaryButton:hover {
            background: #30363d;
        }
        QPushButton#dangerButton {
            background: #21262d;
            color: #ff7b72;
        }
        QPushButton#dangerButton:hover {
            background: #2d1115;
        }
        QPushButton#sidebarToggleButton {
            background: #21262d;
            color: #e6edf7;
            text-align: left;
            min-height: 32px;
            padding-left: 12px;
        }
        QPushButton#sidebarToggleButton:hover {
            background: #30363d;
        }
        QPushButton#navButton {
            background: transparent;
            color: #c9d1d9;
            text-align: left;
            padding-left: 16px;
            min-height: 40px;
            border-radius: 8px;
        }
        QPushButton#navButton:hover {
            background: #21262d;
        }
        QPushButton#navButton[active="true"] {
            background: #1f6feb;
            color: #ffffff;
        }
        QPushButton#adminMenuButton {
            background: #161b22;
            border: 1px solid #30363d;
            color: #e6edf7;
            text-align: left;
            min-height: 44px;
            padding-left: 14px;
        }
        QPushButton#adminMenuButton:hover {
            border-color: #1f6feb;
            background: #21262d;
        }
        QTableWidget#dataTable {
            background: #161b22;
            alternate-background-color: #0f1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            gridline-color: #30363d;
        }
        QHeaderView::section {
            background: #21262d;
            border: 0;
            border-bottom: 1px solid #30363d;
            padding: 8px;
            font-weight: 800;
        }
        QScrollArea {
            border: 0;
            background: transparent;
        }
        QScrollBar:vertical {
            width: 10px;
            background: transparent;
        }
        QScrollBar::handle:vertical {
            background: #30363d;
            border-radius: 5px;
            min-height: 36px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }
        """
