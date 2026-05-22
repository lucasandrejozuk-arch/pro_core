from __future__ import annotations


def _light_controls_section() -> str:
    return """
        QLineEdit,
        QComboBox,
        QDateTimeEdit,
        QTreeWidget,
        QTextEdit {
            border: 1px solid #d0d7de;
            border-radius: 6px;
            padding: 0 8px;
            background: #ffffff;
            min-height: 32px;
        }
        QTextEdit#summaryText {
            padding: 6px 8px;
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
            min-height: 32px;
            padding: 0 10px;
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
        QPushButton#forgotPasswordButton {
            background: #eaeef2;
            border: 1px solid #cf222e;
            color: #cf222e;
        }
        QPushButton#forgotPasswordButton:hover {
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
            background: linear-gradient(
                90deg,
                rgba(13, 110, 253, 0.08) 0%,
                rgba(13, 110, 253, 0.04) 100%
            );
            color: #24292f;
            text-align: left;
            min-height: 32px;
            padding-left: 12px;
            border: 1px solid rgba(13, 110, 253, 0.12);
            border-radius: 6px;
        }
        QPushButton#sidebarToggleButton:hover {
            background: linear-gradient(
                90deg,
                rgba(13, 110, 253, 0.14) 0%,
                rgba(13, 110, 253, 0.08) 100%
            );
            border-color: rgba(13, 110, 253, 0.20);
        }
        QPushButton#navButton {
            background: transparent;
            color: #24292f;
            text-align: left;
            padding-left: 16px;
            min-height: 40px;
            border-radius: 6px;
            margin: 2px 4px;
            border: 1px solid transparent;
            border-left: 4px solid transparent;
            transition: all 0.2s;
        }
        QPushButton#navButton:hover {
            background: rgba(13, 110, 253, 0.08);
            border-left-color: #0969da;
            border-color: rgba(9, 105, 218, 0.24);
        }
        QPushButton#navButton:checked,
        QPushButton#navButton[active="true"] {
            background: rgba(13, 110, 253, 0.12);
            color: #0969da;
            font-weight: 600;
            border: 1px solid #0969da;
            border-left-color: #0969da;
            border-right: 0;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }
        QPushButton#sidebarFooterButton {
            background: transparent;
            color: #57606a;
            border-radius: 6px;
            padding: 6px;
            margin: 2px 4px;
        }
        QPushButton#sidebarFooterButton:hover {
            background: rgba(13, 110, 253, 0.08);
            color: #24292f;
        }
        QPushButton#adminMenuButton {
            background: #ffffff;
            border: 1px solid #d0d7de;
            color: #24292f;
            text-align: left;
            min-height: 38px;
            padding-left: 12px;
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
