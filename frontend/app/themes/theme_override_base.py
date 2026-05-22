from __future__ import annotations


def _palette_override_base(palette: dict[str, str]) -> str:
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
        QLabel#brandTitle {{
            font-size: 46px;
            font-weight: 800;
            letter-spacing: 1px;
            color: {palette["button_text"]};
        }}
        QLabel#brandSubtitle {{
            font-size: 19px;
            font-weight: 600;
            color: {palette["button_text"]};
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
        QLabel#moduleCountBadge {{
            background-color: {palette["primary_subtle"]};
            border: 1px solid {palette["primary"]};
            border-radius: 5px;
            color: {palette["primary"]};
            font-size: 11px;
            font-weight: 800;
            padding: 3px 7px;
        }}
        QLabel#listCountBadge {{
            background-color: {palette["surface"]};
            border: 1px solid {palette["line"]};
            border-radius: 5px;
            color: {palette["muted"]};
            font-size: 10px;
            font-weight: 800;
            padding: 3px 7px;
        }}
        QLabel#moduleActionHint {{
            color: {palette["muted"]};
            font-size: 11px;
            font-weight: 500;
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
        QFrame#footerMessageFrame {{
            background-color: {palette["surface_alt"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
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
            border-radius: 5px;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 9px;
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
        QFrame#dashboardBodyPanel,
        QFrame#dashboardAlertsFrame,
        QFrame#recordListPanel {{
            background-color: {palette["surface"]};
            border-color: {palette["line"]};
        }}
        QFrame#dashboardBodyPanel {{
            border: 0;
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
        QFrame#recordPaginationBar,
        QFrame#serviceOrderSideMenu {{
            background-color: {palette["surface_alt"]};
            border: 1px solid {palette["line"]};
            border-radius: 6px;
        }}
        QFrame#headerBar {{
            background-color: transparent;
            border: 0;
        }}
        QFrame#formSubPanel,
        QFrame#toolPanel,
        QFrame#toolResultPanel,
        QFrame#workflowPanel,
        QFrame#adminDetailsPanel,
        QFrame#dashboardAlertRow,
        QFrame#equipmentSection,
        QFrame#equipmentDetailsPanel {{
            background-color: {palette["surface_alt"]};
            border-color: {palette["line"]};
        }}
        QFrame#toolPanel,
        QFrame#toolResultPanel,
        QFrame#adminDetailsPanel,
        QFrame#equipmentDetailsPanel {{
            border: 1px solid {palette["line"]};
            border-radius: 6px;
        }}
        QFrame#topCommandBar {{
            background-color: {palette["sidebar"]};
            border-bottom: 1px solid {palette["line"]};
        }}
        QFrame#sessionFooter {{
            background-color: {palette["sidebar"]};
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
    """
