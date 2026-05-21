from __future__ import annotations


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
        QLabel#footerMessage[level="success"],
        QLabel#footerStatusDot[level="success"] {{
            color: {palette["success"]};
        }}
        QLabel#footerMessage[level="warning"],
        QLabel#footerStatusDot[level="warning"] {{
            color: {palette["warning"]};
        }}
        QLabel#footerMessage[level="error"],
        QLabel#footerStatusDot[level="error"] {{
            color: {palette["danger"]};
        }}
        QLabel#footerMessage[level="info"] {{
            color: {palette["muted"]};
        }}
        QLabel#emptyAlertText {{
            color: {palette["muted"]};
            font-size: 22px;
            font-weight: 700;
        }}
        QLabel#emptyStateText {{
            color: {palette["muted"]};
            font-size: 17px;
            font-weight: 700;
            padding: 8px;
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
            border: 1px solid {palette["line"]};
            border-radius: 4px;
            color: {palette["text"]};
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
        QFrame#recordEditorPanel,
        QFrame#recordSummaryPanel {{
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
        QFrame#topCommandBar {{
            background-color: {palette["surface"]};
            border-bottom: 1px solid {palette["line"]};
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
        QWidget#dashboardGrid {{
            background-color: transparent;
        }}
        QFrame#sidebar {{
            background: linear-gradient(
                180deg,
                {palette["sidebar"]} 0%,
                {palette["surface_alt"]} 100%
            );
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
        QTextEdit {{
            padding: 6px 8px;
        }}
        QTabWidget::pane {{
            padding: 8px;
        }}
        QTabBar::tab {{
            background-color: {palette["surface_alt"]};
            color: {palette["muted"]};
            min-height: 28px;
            padding: 4px 10px;
            border: 1px solid {palette["line"]};
            border-bottom: 2px solid {palette["line"]};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {palette["surface"]};
            color: {palette["text"]};
            border-bottom-color: {palette["primary"]};
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
