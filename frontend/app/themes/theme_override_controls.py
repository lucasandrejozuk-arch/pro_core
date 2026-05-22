from __future__ import annotations


def _palette_override_controls(palette: dict[str, str]) -> str:
    return f"""
        QLineEdit,
        QComboBox,
        QDateTimeEdit,
        QTableWidget,
        QTableView,
        QTreeWidget,
        QTextEdit,
        QTabWidget::pane {{
            background-color: {palette["input_bg"]};
            border-color: {palette["line"]};
            border-radius: 4px;
            color: {palette["text"]};
        }}
        QLineEdit,
        QComboBox,
        QDateTimeEdit {{
            min-height: 26px;
            padding: 3px 8px;
        }}
        QLineEdit:hover,
        QComboBox:hover,
        QDateTimeEdit:hover,
        QTextEdit:hover {{
            border-color: {palette["primary"]};
        }}
        QTextEdit {{
            padding: 6px 8px;
        }}
        QTabWidget::pane {{
            padding: 8px;
        }}
        QTabWidget#toolsTabs::pane,
        QTabWidget#specialtyTabs::pane {{
            background-color: {palette["surface"]};
            border: 1px solid {palette["line"]};
        }}
        QTabWidget#toolsTabs QTabBar,
        QTabWidget#specialtyTabs QTabBar {{
            background-color: {palette["surface"]};
        }}
        QTabBar::tab {{
            background-color: {palette["surface_alt"]};
            color: {palette["muted"]};
            min-height: 28px;
            padding: 4px 12px;
            border: 1px solid {palette["line"]};
            border-top: 3px solid transparent;
            border-bottom: 0;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 1px;
        }}
        QTabBar::tab:selected {{
            background-color: {palette["surface"]};
            color: {palette["text"]};
            border-color: {palette["primary"]};
            border-top-color: {palette["primary"]};
            border-bottom-color: {palette["surface"]};
        }}
        QTabBar::tab:hover {{
            background-color: {palette["primary_subtle"]};
            color: {palette["text"]};
            border-color: {palette["primary"]};
        }}
        QTabBar::tab:disabled {{
            background-color: {palette["disabled_bg"]};
            color: {palette["surface"]};
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
        QMenu {{
            background-color: {palette["surface"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
            color: {palette["text"]};
            padding: 5px;
        }}
        QMenu::item {{
            background-color: transparent;
            border-radius: 4px;
            color: {palette["text"]};
            padding: 6px 24px 6px 10px;
        }}
        QMenu::item:selected {{
            background-color: {palette["primary_subtle"]};
            color: {palette["text"]};
        }}
        QMenu::item:disabled {{
            color: {palette["muted"]};
        }}
        QMenu::separator {{
            background-color: {palette["line"]};
            height: 1px;
            margin: 4px 6px;
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
        QPushButton:pressed {{
            background-color: {palette["primary_subtle"]};
            color: {palette["text"]};
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
        QPushButton#forgotPasswordButton {{
            background-color: {palette["surface_alt"]};
            border: 1px solid {palette["danger"]};
            color: {palette["danger"]};
        }}
        QPushButton#forgotPasswordButton:hover {{
            background-color: {palette["primary_subtle"]};
        }}
        QPushButton#dangerButton {{
            background-color: {palette["surface_alt"]};
            color: {palette["danger"]};
        }}
        QPushButton#dangerButton:hover {{
            background-color: {palette["danger_bg"]};
        }}
        QPushButton#warningButton {{
            background-color: {palette["warning_bg"]};
            color: {palette["warning"]};
        }}
        QPushButton#warningButton:hover {{
            background-color: {palette["primary_subtle"]};
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
        QPushButton#sidebarFooterButton[variant="warning"] {{
            color: {palette["warning"]};
            border: 1px solid {palette["warning"]};
        }}
        QPushButton#sidebarFooterButton[variant="danger"] {{
            color: {palette["danger"]};
            border: 1px solid {palette["danger"]};
        }}
        QLabel#topCommandContextTab {{
            background-color: {palette["surface"]};
            border: 1px solid {palette["line"]};
            border-top: 3px solid {palette["primary"]};
            border-bottom: 0;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: {palette["text"]};
            font-size: 11px;
            font-weight: 800;
            padding: 6px 12px 7px 12px;
        }}
        QPushButton#topCommandButton {{
            background-color: {palette["surface_alt"]};
            border: 1px solid {palette["line"]};
            border-top: 3px solid transparent;
            border-bottom: 0;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: {palette["text"]};
            min-height: 28px;
            padding: 4px 11px 6px 11px;
        }}
        QPushButton#topCommandButton:hover {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
            border-top-color: {palette["primary"]};
        }}
        QPushButton#topCommandButton:disabled {{
            background-color: {palette["surface_alt"]};
            border-color: {palette["line"]};
            color: {palette["muted"]};
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
        QPushButton#summaryCopyButton {{
            background-color: {palette["surface_alt"]};
            border: 1px solid {palette["line"]};
            border-radius: 4px;
            padding: 0;
        }}
        QPushButton#summaryCopyButton:hover {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
        }}
        QPushButton#navButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-left: 4px solid transparent;
            border-radius: 7px;
            margin: 1px 0 1px 4px;
            padding: 0;
            text-align: center;
            min-width: 42px;
            max-width: 42px;
            min-height: 42px;
            max-height: 42px;
        }}
        QPushButton#navButton:hover {{
            background-color: rgba(56, 189, 248, 0.16);
            border-color: {palette["primary"]};
        }}
        QPushButton#navButton[active="true"] {{
            background-color: rgba(56, 189, 248, 0.26);
            border-color: {palette["primary"]};
            border-left-color: {palette["primary"]};
            border-right: 0;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }}
        QPushButton#adminMenuButton {{
            background-color: {palette["surface"]};
            border-color: {palette["line"]};
            color: {palette["text"]};
            min-height: 38px;
            padding-left: 12px;
        }}
        QPushButton#adminMenuButton:hover {{
            background-color: {palette["primary_subtle"]};
            border-color: {palette["primary"]};
        }}
        QTableWidget#dataTable {{
            background-color: {palette["surface"]};
            alternate-background-color: {palette["surface_alt"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
            color: {palette["text"]};
            gridline-color: {palette["line"]};
        }}
        QTableWidget::item {{
            color: {palette["text"]};
            padding: 4px;
        }}
        QTableWidget::item:selected {{
            background-color: {palette["selection_bg"]};
            color: {palette["selection_text"]};
        }}
        QTableWidget::item:hover {{
            background-color: {palette["primary_subtle"]};
        }}
        QHeaderView::section {{
            background-color: {palette["surface_alt"]};
            border: 0;
            border-bottom: 1px solid {palette["line"]};
            color: {palette["text"]};
            font-weight: 700;
            min-height: 26px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {palette["line"]};
        }}
    """
