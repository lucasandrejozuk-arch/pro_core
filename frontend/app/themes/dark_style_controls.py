from __future__ import annotations


def _dark_controls_section() -> str:
    return """
        QLineEdit,
        QComboBox,
        QDateTimeEdit,
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
        QPushButton#forgotPasswordButton {
            background: #21262d;
            border: 1px solid #ff7b72;
            color: #ff7b72;
        }
        QPushButton#forgotPasswordButton:hover {
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
            background: linear-gradient(
                90deg,
                rgba(31, 111, 235, 0.12) 0%,
                rgba(31, 111, 235, 0.06) 100%
            );
            color: #e6edf7;
            text-align: left;
            min-height: 32px;
            padding-left: 12px;
            border: 1px solid rgba(31, 111, 235, 0.16);
            border-radius: 6px;
        }
        QPushButton#sidebarToggleButton:hover {
            background: linear-gradient(
                90deg,
                rgba(31, 111, 235, 0.18) 0%,
                rgba(31, 111, 235, 0.10) 100%
            );
            border-color: rgba(31, 111, 235, 0.24);
        }
        QPushButton#navButton {
            background: transparent;
            color: #c9d1d9;
            text-align: left;
            padding-left: 16px;
            min-height: 40px;
            border-radius: 8px;
            margin: 2px 4px;
            border: 1px solid transparent;
            border-left: 4px solid transparent;
        }
        QPushButton#navButton:hover {
            background: rgba(56, 189, 248, 0.12);
            border-left-color: #38bdf8;
            border-color: rgba(56, 189, 248, 0.24);
        }
        QPushButton#navButton[active="true"] {
            background: rgba(56, 189, 248, 0.20);
            color: #c5efff;
            font-weight: 600;
            border: 1px solid #38bdf8;
            border-left-color: #38bdf8;
            border-right: 0;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }
        QPushButton#sidebarFooterButton {
            background: transparent;
            color: #8b949e;
            border-radius: 6px;
            padding: 6px;
            margin: 2px 4px;
        }
        QPushButton#sidebarFooterButton:hover {
            background: rgba(56, 189, 248, 0.12);
            color: #e6edf7;
        }
        QFrame#recordPaginationBar,
        QFrame#serviceOrderSideMenu {
            background: #111e31;
            border: 1px solid #26435b;
            border-radius: 8px;
        }
        QFrame#recordToggleRail {
            background: #0d1826;
            border: 1px solid #26435b;
            border-radius: 8px;
        }
        QPushButton#adminMenuButton {
            background: #161b22;
            border: 1px solid #30363d;
            color: #e6edf7;
            text-align: left;
            min-height: 38px;
            padding-left: 12px;
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
