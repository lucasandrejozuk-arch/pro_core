from __future__ import annotations


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
            border-radius: 6px;
            color: #79c0ff;
            font-weight: 800;
            padding: 8px 10px;
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
            background: #161b22;
            border-bottom: 1px solid #30363d;
        }
        QFrame#sessionFooter {
            background: #161b22;
            border-top: 1px solid #30363d;
        }
        QLabel#sessionFooterText,
        QLabel#sessionFooterModule {
            color: #8b949e;
            font-size: 11px;
            font-weight: 700;
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
            background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
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
        QLabel#sidebarSessionInfo {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #8b949e;
            font-size: 12px;
            padding: 10px;
        }
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
            border-left: 3px solid transparent;
        }
        QPushButton#navButton:hover {
            background: rgba(31, 111, 235, 0.10);
            border-left-color: #1f6feb;
        }
        QPushButton#navButton[active="true"] {
            background: rgba(31, 111, 235, 0.14);
            color: #79c0ff;
            font-weight: 600;
            border-left-color: #1f6feb;
        }
        QPushButton#sidebarFooterButton {
            background: transparent;
            color: #8b949e;
            border-radius: 6px;
            padding: 6px;
            margin: 2px 4px;
        }
        QPushButton#sidebarFooterButton:hover {
            background: rgba(31, 111, 235, 0.10);
            color: #e6edf7;
        }
        QPushButton#adminMenuButton {
            background: #161b22;
            border: 1px solid #30363d;
            color: #e6edf7;
            text-align: left;
            min-height: 44px;
            padding-left: 14px;
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
