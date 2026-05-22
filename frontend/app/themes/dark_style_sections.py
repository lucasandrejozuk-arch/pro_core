from __future__ import annotations


def _dark_base_section() -> str:
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
            font-size: 46px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta {
            color: #8b949e;
            font-size: 15px;
        }
        QLabel#brandSubtitle {
            font-size: 19px;
            font-weight: 600;
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
            border-radius: 5px;
            color: #79c0ff;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 9px;
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
        QFrame#topCommandBar {
            background: #091628;
            border-bottom: 1px solid #26435b;
        }
        QFrame#sessionFooter {
            background: #0a192a;
            border-top: 1px solid #26435b;
        }
        QLabel#sessionFooterText,
        QLabel#sessionFooterModule {
            color: #8b949e;
            font-size: 11px;
            font-weight: 700;
        }
        QLabel#moduleCountBadge {
            background: #102a43;
            border: 1px solid #1f6feb;
            border-radius: 5px;
            color: #79c0ff;
            font-size: 11px;
            font-weight: 800;
            padding: 3px 7px;
        }
        QLabel#moduleActionHint {
            color: #8b949e;
            font-size: 11px;
            font-weight: 500;
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
        QFrame#headerBar,
        QFrame#recordSummaryPanel {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        QFrame#sidebar {
            background: linear-gradient(180deg, #091628 0%, #0b1b2d 100%);
            border-right: 1px solid #26435b;
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
    """
