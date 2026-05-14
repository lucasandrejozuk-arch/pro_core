from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication, theme: str = "light") -> None:
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(_dark_stylesheet() if theme == "dark" else _light_stylesheet())


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
        QLabel#cardTitle {
            font-size: 15px;
            font-weight: 800;
        }
        QLabel#sidebarCaption {
            color: #8b949e;
            font-size: 11px;
            font-weight: 800;
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
            background: #0f1117;
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
        QLineEdit,
        QComboBox,
        QTreeWidget {
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
            background: #0969da;
            color: #ffffff;
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
        QLabel#cardTitle {
            font-size: 15px;
            font-weight: 800;
        }
        QLabel#sidebarCaption {
            color: #8b949e;
            font-size: 11px;
            font-weight: 800;
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
        QLineEdit,
        QComboBox,
        QTreeWidget {
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
