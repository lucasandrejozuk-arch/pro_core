from __future__ import annotations


def _light_base_section() -> str:
    return """
        QWidget {
            color: #24292f;
            selection-background-color: #0969da;
            selection-color: #ffffff;
            font-size: 14px;
        }
        QWidget#splash,
        QWidget#loginWindow,
        QWidget#passwordWindow,
        QWidget#dashboardWindow {
            background: #f6f8fa;
        }
        QLabel#splashTitle,
        QLabel#brandTitle {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        QLabel#splashSubtitle,
        QLabel#brandSubtitle,
        QLabel#mutedText,
        QLabel#cardMeta {
            color: #57606a;
            font-size: 13px;
        }
        QLabel#errorText {
            color: #b42318;
            font-weight: 600;
        }
        QLabel#formTitle,
        QLabel#pageTitle {
            font-size: 20px;
            font-weight: 800;
        }
        QLabel#sectionTitle {
            font-size: 15px;
            font-weight: 700;
        }
        QLabel#dashboardGreeting {
            color: #24292f;
            font-size: 13px;
            font-weight: 700;
        }
        QLabel#cardTitle {
            font-size: 14px;
            font-weight: 700;
        }
        QLabel#dashboardCardMarker {
            font-size: 10px;
            font-weight: 700;
        }
        QLabel#dashboardCardValue {
            font-size: 24px;
            font-weight: 800;
        }
        QLabel#dashboardCardLabel {
            color: #24292f;
            font-size: 11px;
            font-weight: 700;
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
            border-radius: 5px;
            color: #0969da;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 9px;
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
        QFrame#topCommandBar {
            background: #ffffff;
            border-bottom: 1px solid #d0d7de;
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
        QLabel#moduleCountBadge {
            background: #ddf4ff;
            border: 1px solid #0969da;
            border-radius: 5px;
            color: #0969da;
            font-size: 11px;
            font-weight: 800;
            padding: 3px 7px;
        }
        QLabel#moduleActionHint {
            color: #57606a;
            font-size: 11px;
            font-weight: 500;
        }
        QFrame#dashboardKpiCard,
        QFrame#dashboardAlertsFrame {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            margin-bottom: 6px;
            padding: 10px 12px 8px 12px;
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
        QFrame#headerBar,
        QFrame#recordSummaryPanel {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
        }
        QFrame#sidebar {
            background: linear-gradient(180deg, #f1f5f9 0%, #eef2f7 100%);
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
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            color: #57606a;
            font-size: 12px;
            padding: 10px;
        }
    """
