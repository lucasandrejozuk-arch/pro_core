from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from frontend.app.screens.dashboard_modules import MODULE_STAGES


def build_dashboard_sidebar(self) -> None:
    self.setWindowTitle("PRO CORE - Dashboard")
    self.setMinimumSize(1120, 720)
    self.setObjectName("dashboardWindow")

    self.sidebar_expanded_width = 68
    self.sidebar_collapsed_width = 36
    self.sidebar_margin = 18
    self.sidebar_icon_color = "#ffffff"
    self.record_editor_icon_color = "#0969da"
    self.record_editor_active_icon_color = "#ffffff"
    self.sidebar_icon_size = QSize(22, 22)
    self.sidebar_buttons_by_icon: dict[QPushButton, str] = {}

    self.sidebar = QFrame()
    self.sidebar.setObjectName("sidebar")
    self.sidebar.setFixedWidth(self.sidebar_expanded_width)

    self.sidebar_title = QLabel("PRO CORE")
    self.sidebar_title.setObjectName("sidebarTitle")
    self.sidebar_title.hide()

    self.sidebar_text = QLabel("Assistencia tecnica")
    self.sidebar_text.setObjectName("sidebarText")
    self.sidebar_text.hide()

    self.sidebar_layout = QVBoxLayout(self.sidebar)
    self.sidebar_layout.setContentsMargins(8, 8, 8, 8)
    self.sidebar_layout.setSpacing(8)

    self.sidebar_collapsed_label = QLabel("")
    self.sidebar_collapsed_label.setObjectName("sidebarSessionInfo")
    self.sidebar_collapsed_label.setWordWrap(True)
    self.sidebar_collapsed_label.hide()

    self.sidebar_nav_container = QWidget()
    sidebar_nav_layout = QVBoxLayout(self.sidebar_nav_container)
    sidebar_nav_layout.setContentsMargins(0, 8, 0, 0)
    sidebar_nav_layout.setSpacing(10)

    self.module_buttons: dict[str, QPushButton] = {}
    self.module_icon_names = {stage.key: stage.icon_name for stage in MODULE_STAGES}
    self.module_labels = {stage.key: stage.label for stage in MODULE_STAGES}
    self.module_descriptions = {stage.key: stage.description for stage in MODULE_STAGES}
    self.module_action_hints = {stage.key: stage.action_hint for stage in MODULE_STAGES}
    self.module_stage_numbers = {stage.key: stage.stage for stage in MODULE_STAGES}
    self.module_groups = {stage.key: stage.group for stage in MODULE_STAGES}
    self.searchable_module_keys = {stage.key for stage in MODULE_STAGES if stage.searchable}
    self.record_module_keys = {stage.key for stage in MODULE_STAGES if stage.record_module}
    module_groups = (
        ("OPERACAO", ("dashboard", "service_orders", "tools")),
        ("CADASTROS", ("customers", "equipment", "inventory")),
    )

    for caption, module_keys in module_groups:
        if sidebar_nav_layout.count() > 0:
            separator = QFrame()
            separator.setObjectName("sidebarSeparator")
            separator.setFixedHeight(1)
            sidebar_nav_layout.addWidget(separator)
        for module_key in module_keys:
            button = QPushButton("")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setProperty("active", "false")
            self._configure_sidebar_button(
                button,
                self.module_icon_names[module_key],
                f"{caption.title()} - {self.module_labels[module_key]}",
            )
            button.clicked.connect(
                lambda checked=False, key=module_key: self.module_selected.emit(key)
            )
            self.module_buttons[module_key] = button
            sidebar_nav_layout.addWidget(button)

    separator = QFrame()
    separator.setObjectName("sidebarSeparator")
    separator.setFixedHeight(1)
    sidebar_nav_layout.addWidget(separator)

    for module_key in ("admin_area", "settings"):
        button = QPushButton("")
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setProperty("active", "false")
        self._configure_sidebar_button(
            button,
            self.module_icon_names[module_key],
            self.module_labels[module_key],
        )
        button.clicked.connect(lambda checked=False, key=module_key: self.module_selected.emit(key))
        self.module_buttons[module_key] = button
        sidebar_nav_layout.addWidget(button)

    self.sidebar_layout.addWidget(self.sidebar_nav_container)

    self.sidebar_layout.addStretch()

    self.session_info_label = QLabel("")
    self.session_info_label.setObjectName("sidebarSessionInfo")
    self.session_info_label.setWordWrap(True)
    self.session_info_label.hide()

    self.logout_button = QPushButton("")
    self.logout_button.setObjectName("sidebarFooterButton")
    self.logout_button.setProperty("variant", "warning")
    self.logout_button.setToolTip("Logout")
    self._configure_sidebar_button(self.logout_button, "logout", "Logout")
    self.logout_button.clicked.connect(self.logout_requested.emit)
    self.sidebar_layout.addWidget(self.logout_button)

    self.exit_button = QPushButton("")
    self.exit_button.setObjectName("sidebarFooterButton")
    self.exit_button.setProperty("variant", "danger")
    self.exit_button.setToolTip("Sair")
    self._configure_sidebar_button(self.exit_button, "exit", "Sair")
    self.exit_button.clicked.connect(self.request_exit)
    self.sidebar_layout.addWidget(self.exit_button)

