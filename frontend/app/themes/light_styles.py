from __future__ import annotations


def _light_stylesheet() -> str:
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
        QLabel#moduleStageBadge {
            background: #ddf4ff;
            border: 1px solid #0969da;
            border-radius: 6px;
            color: #0969da;
            font-size: 11px;
            font-weight: 800;
            padding: 4px 8px;
        }
        QLabel#moduleActionHint {
            color: #57606a;
            font-size: 11px;
            font-weight: 600;
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
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }
        QPushButton#navButton:hover {
            background: rgba(13, 110, 253, 0.08);
            border-left-color: #0969da;
        }
        QPushButton#navButton:checked,
        QPushButton#navButton[active="true"] {
            background: rgba(13, 110, 253, 0.12);
            color: #0969da;
            font-weight: 600;
            border-left-color: #0969da;
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
