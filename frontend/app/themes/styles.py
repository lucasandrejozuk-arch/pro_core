from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication, theme: str = "light", primary_color: str | None = None) -> None:
    app.setFont(QFont("Segoe UI", 10))
    is_dark = theme == "dark"
    default_color = "#1f6feb" if is_dark else "#0969da"
    accent_color = _safe_hex_color(primary_color, default_color)
    stylesheet = _dark_stylesheet() if is_dark else _light_stylesheet()
    app.setStyleSheet(stylesheet.replace(default_color, accent_color))


def _safe_hex_color(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    color = value.strip()
    if len(color) != 7 or not color.startswith("#"):
        return fallback
    if any(character not in "0123456789abcdefABCDEF" for character in color[1:]):
        return fallback
    return color


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
