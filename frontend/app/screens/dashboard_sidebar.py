from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


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
    self.module_icon_names = {
        "dashboard": "dashboard",
        "service_orders": "service_orders",
        "customers": "customers",
        "equipment": "equipment",
        "inventory": "inventory",
        "tools": "tools",
        "sectors": "sectors",
        "users": "users",
        "password_resets": "password_resets",
        "settings": "settings",
        "audit_logs": "audit_logs",
        "admin_area": "settings",
    }
    self.module_labels = {
        "dashboard": "Dashboard",
        "service_orders": "Ordens de Servico",
        "customers": "Clientes",
        "equipment": "Equipamentos",
        "inventory": "Estoque",
        "tools": "Ferramentas",
        "sectors": "Setores",
        "users": "Usuarios",
        "password_resets": "Solicitacoes de senha",
        "settings": "Configuracoes",
        "audit_logs": "Logs/Auditoria",
        "admin_area": "Area administrativa",
    }
    self.module_descriptions = {
        "dashboard": "Indicadores operacionais e alertas do dia",
        "service_orders": "Fluxo operacional de ordens de servico",
        "customers": "Cadastro e relacionamento de clientes",
        "equipment": "Gestao hierarquica de ativos, objetos e componentes",
        "inventory": "Estoque, custos e niveis minimos",
        "tools": "Calculadoras e utilitarios por perfil operacional",
        "sectors": "Setores, liderancas e estrutura operacional",
        "users": "Contas, perfis, setores e seguranca",
        "password_resets": "Atendimento de solicitacoes de acesso",
        "settings": "Identidade visual, empresa, tema e backup",
        "audit_logs": "Rastreabilidade administrativa e operacional",
        "admin_area": "Central de administracao, usuarios e auditoria",
    }
    self.searchable_module_keys = {
        "service_orders",
        "customers",
        "inventory",
        "sectors",
        "users",
        "password_resets",
        "audit_logs",
    }
    self.record_module_keys = self.searchable_module_keys
    module_groups = [
        ("OPERACAO", ("dashboard", "service_orders", "tools")),
        ("CADASTROS", ("customers", "equipment", "inventory")),
    ]

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
        button.clicked.connect(
            lambda checked=False, key=module_key: self.module_selected.emit(key)
        )
        self.module_buttons[module_key] = button
        sidebar_nav_layout.addWidget(button)

    self.sidebar_layout.addWidget(self.sidebar_nav_container)

    self.sidebar_layout.addStretch()

    self.session_info_label = QLabel("")
    self.session_info_label.setObjectName("sidebarSessionInfo")
    self.session_info_label.setWordWrap(True)
    self.session_info_label.hide()

    self.session_button = QPushButton("")
    self.session_button.setObjectName("sidebarFooterButton")
    self.session_button.setCursor(Qt.CursorShape.PointingHandCursor)
    self._configure_sidebar_button(
        self.session_button,
        "settings",
        "Personalizacao e configuracoes",
    )
    self.session_button.clicked.connect(lambda: self.module_selected.emit("settings"))
    self.sidebar_layout.addWidget(self.session_button)

    self.logout_button = QPushButton("")
    self.logout_button.setObjectName("sidebarFooterButton")
    self.logout_button.setToolTip("Sair")
    self._configure_sidebar_button(self.logout_button, "logout", "Sair")
    self.logout_button.clicked.connect(self.logout_requested.emit)
    self.sidebar_layout.addWidget(self.logout_button)
