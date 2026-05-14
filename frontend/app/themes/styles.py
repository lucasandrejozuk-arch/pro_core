from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication, theme: str = "light") -> None:
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(_dark_stylesheet() if theme == "dark" else _light_stylesheet())


def _light_stylesheet() -> str:
    return """
        QWidget {
            color: #172033;
        }
        QWidget#splash,
        QWidget#loginWindow,
        QWidget#passwordWindow,
        QWidget#dashboardWindow {
            background: #f7f9fc;
        }
        QLabel#splashTitle,
        QLabel#brandTitle {
            font-size: 34px;
            font-weight: 800;
            letter-spacing: 0;
        }
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta {
            color: #5b667a;
            font-size: 15px;
        }
        QLabel#errorText {
            color: #b42318;
            font-weight: 600;
        }
        QLabel#formTitle,
        QLabel#pageTitle {
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#sectionTitle {
            font-size: 16px;
            font-weight: 700;
        }
        QLabel#cardTitle {
            font-size: 15px;
            font-weight: 700;
        }
        QProgressBar {
            height: 8px;
            border: 0;
            border-radius: 4px;
            background: #dde5ef;
        }
        QProgressBar::chunk {
            border-radius: 4px;
            background: #1f6feb;
        }
        QFrame#brandPanel {
            background: #edf3fb;
        }
        QFrame#formPanel,
        QFrame#contentPanel,
        QFrame#moduleCard {
            background: #ffffff;
            border: 1px solid #d8e0ea;
            border-radius: 8px;
        }
        QFrame#sidebar {
            background: #172033;
        }
        QLabel#sidebarTitle {
            color: #ffffff;
            font-size: 20px;
            font-weight: 800;
        }
        QLabel#sidebarText {
            color: #b9c4d3;
        }
        QLineEdit,
        QComboBox {
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 0 12px;
            background: #ffffff;
            min-height: 42px;
        }
        QLineEdit:focus,
        QComboBox:focus {
            border-color: #1f6feb;
        }
        QPushButton {
            border: 0;
            border-radius: 6px;
            background: #1f6feb;
            color: #ffffff;
            font-weight: 700;
            min-height: 42px;
            padding: 0 14px;
        }
        QPushButton:hover {
            background: #195cc5;
        }
        QPushButton:disabled {
            background: #94a3b8;
        }
        QPushButton#secondaryButton {
            background: #e8eef7;
            color: #172033;
        }
        QPushButton#secondaryButton:hover {
            background: #dbe5f1;
        }
        QPushButton#navButton {
            background: transparent;
            color: #d7deea;
            text-align: left;
            padding-left: 14px;
        }
        QPushButton#navButton:hover {
            background: #243047;
        }
        QTableWidget#dataTable {
            background: #ffffff;
            alternate-background-color: #f8fafc;
            border: 1px solid #d8e0ea;
            border-radius: 6px;
            gridline-color: #e5ebf3;
        }
        QHeaderView::section {
            background: #edf3fb;
            border: 0;
            border-bottom: 1px solid #d8e0ea;
            padding: 8px;
            font-weight: 700;
        }
        """


def _dark_stylesheet() -> str:
    return """
        QWidget {
            color: #e6edf7;
        }
        QWidget#splash,
        QWidget#loginWindow,
        QWidget#passwordWindow,
        QWidget#dashboardWindow {
            background: #111827;
        }
        QLabel#splashTitle,
        QLabel#brandTitle {
            font-size: 34px;
            font-weight: 800;
            letter-spacing: 0;
        }
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta {
            color: #aab6c7;
            font-size: 15px;
        }
        QLabel#errorText {
            color: #ffb4ab;
            font-weight: 600;
        }
        QLabel#formTitle,
        QLabel#pageTitle {
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#sectionTitle {
            font-size: 16px;
            font-weight: 700;
        }
        QLabel#cardTitle {
            font-size: 15px;
            font-weight: 700;
        }
        QProgressBar {
            height: 8px;
            border: 0;
            border-radius: 4px;
            background: #263244;
        }
        QProgressBar::chunk {
            border-radius: 4px;
            background: #3b82f6;
        }
        QFrame#brandPanel {
            background: #172033;
        }
        QFrame#formPanel,
        QFrame#contentPanel,
        QFrame#moduleCard {
            background: #172033;
            border: 1px solid #2c3a4f;
            border-radius: 8px;
        }
        QFrame#sidebar {
            background: #0b1220;
        }
        QLabel#sidebarTitle {
            color: #ffffff;
            font-size: 20px;
            font-weight: 800;
        }
        QLabel#sidebarText {
            color: #94a3b8;
        }
        QLineEdit,
        QComboBox {
            border: 1px solid #3a4a63;
            border-radius: 6px;
            padding: 0 12px;
            background: #111827;
            color: #e6edf7;
            min-height: 42px;
        }
        QLineEdit:focus,
        QComboBox:focus {
            border-color: #3b82f6;
        }
        QPushButton {
            border: 0;
            border-radius: 6px;
            background: #2563eb;
            color: #ffffff;
            font-weight: 700;
            min-height: 42px;
            padding: 0 14px;
        }
        QPushButton:hover {
            background: #1d4ed8;
        }
        QPushButton:disabled {
            background: #475569;
            color: #cbd5e1;
        }
        QPushButton#secondaryButton {
            background: #263244;
            color: #e6edf7;
        }
        QPushButton#secondaryButton:hover {
            background: #31415a;
        }
        QPushButton#navButton {
            background: transparent;
            color: #d7deea;
            text-align: left;
            padding-left: 14px;
        }
        QPushButton#navButton:hover {
            background: #172033;
        }
        QTableWidget#dataTable {
            background: #172033;
            alternate-background-color: #1d293a;
            border: 1px solid #2c3a4f;
            border-radius: 6px;
            gridline-color: #2c3a4f;
        }
        QHeaderView::section {
            background: #1d293a;
            border: 0;
            border-bottom: 1px solid #2c3a4f;
            padding: 8px;
            font-weight: 700;
        }
        """
