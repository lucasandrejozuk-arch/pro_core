from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.grid import (
    add_widget,
    create_grid,
)
from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
    confirm_destructive_action,
)
from frontend.app.screens.dashboard_mixins_1 import DashboardMixin1
from frontend.app.screens.dashboard_mixins_2 import DashboardMixin2
from frontend.app.screens.dashboard_mixins_3 import DashboardMixin3
from frontend.app.screens.dashboard_mixins_4 import DashboardMixin4
from frontend.app.screens.dashboard_mixins_5 import DashboardMixin5
from frontend.app.screens.dashboard_mixins_6 import DashboardMixin6
from frontend.app.screens.dashboard_mixins_7 import DashboardMixin7
from frontend.app.widgets import DashboardKpiCard

__all__ = [
    "DashboardWindow",
    "EquipmentAssetDialog",
    "EquipmentDefectCasesDialog",
    "QFileDialog",
    "QMessageBox",
    "confirm_destructive_action",
]


class DashboardWindow(
    DashboardMixin1,
    DashboardMixin2,
    DashboardMixin3,
    DashboardMixin4,
    DashboardMixin5,
    DashboardMixin6,
    DashboardMixin7,
    QWidget,
):
    logout_requested = Signal()
    module_selected = Signal(str)
    refresh_requested = Signal()
    customer_create_requested = Signal(dict)
    customer_update_requested = Signal(str, dict)
    customer_delete_requested = Signal(str)
    customer_document_upload_requested = Signal(str, str, str)
    equipment_create_requested = Signal(dict)
    equipment_update_requested = Signal(str, dict)
    equipment_delete_requested = Signal(str)
    equipment_board_create_requested = Signal(str, dict)
    equipment_board_update_requested = Signal(str, str, dict)
    equipment_board_delete_requested = Signal(str, str)
    equipment_component_create_requested = Signal(str, str, dict)
    equipment_component_update_requested = Signal(str, str, str, dict)
    equipment_component_delete_requested = Signal(str, str, str)
    equipment_defect_cases_requested = Signal(str)
    equipment_import_requested = Signal(str, bool)
    equipment_export_requested = Signal(str, str)
    inventory_create_requested = Signal(dict)
    inventory_update_requested = Signal(str, dict)
    inventory_delete_requested = Signal(str)
    sector_create_requested = Signal(dict)
    sector_update_requested = Signal(str, dict)
    service_order_create_requested = Signal(dict)
    service_order_update_requested = Signal(str, dict)
    service_order_delete_requested = Signal(str)
    service_order_diagnosis_requested = Signal(str, str)
    service_order_budget_item_requested = Signal(str, dict)
    service_order_submit_quote_requested = Signal(str)
    service_order_approve_requested = Signal(str)
    service_order_reject_requested = Signal(str, str)
    service_order_start_requested = Signal(str)
    service_order_complete_requested = Signal(str)
    service_order_document_upload_requested = Signal(str, str, str)
    user_create_requested = Signal(dict)
    user_update_requested = Signal(str, dict)
    user_password_reset_requested = Signal(str, str)
    password_reset_resolve_requested = Signal(str, str)
    settings_update_requested = Signal(dict)
    ui_scale_changed = Signal(float)
    backup_run_requested = Signal()
    report_view_requested = Signal(str)
    report_export_requested = Signal(str, str, str)
    financial_create_requested = Signal(dict)
    financial_mark_paid_requested = Signal(str)
    financial_cancel_requested = Signal(str)
    financial_delete_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.active_module_key = "dashboard"
        self.current_rows: list[dict[str, Any]] = []
        self.all_rows: list[dict[str, Any]] = []
        self.current_columns: list[tuple[str, str]] = []
        self.equipment_visible_rows: list[dict[str, Any]] = []
        self.equipment_board_visible_rows: list[dict[str, Any]] = []
        self.equipment_component_visible_rows: list[dict[str, Any]] = []
        self.selected_customer_id: str | None = None
        self.selected_customer_document_path: str | None = None
        self.selected_equipment_id: str | None = None
        self.selected_equipment_board_id: str | None = None
        self.selected_equipment_component_id: str | None = None
        self.selected_inventory_item_id: str | None = None
        self.selected_service_order_id: str | None = None
        self.selected_sector_id: str | None = None
        self.selected_user_id: str | None = None
        self.selected_password_reset_request_id: str | None = None
        self.selected_financial_record_id: str | None = None
        self.selected_service_order_document_path: str | None = None
        self.current_report_module_key = "service_orders"
        self.current_tools: list[dict[str, Any]] = []
        self.current_settings: dict[str, Any] = {}
        self.current_selected_record: dict[str, Any] | None = None
        self.current_selected_summary = "Nenhum item selecionado."
        self.record_editor_dialog: QDialog | None = None
        self.record_details_dialog: QDialog | None = None
        self.record_editor_popup_layout: QVBoxLayout | None = None
        self.ui_scale_min = 0.82
        self.ui_scale_max = 1.18
        self.ui_scale_value = 1.0
        self.current_user_role = ""
        self.equipment_customers: list[dict[str, Any]] = []
        self.service_order_customers: list[dict[str, Any]] = []
        self.service_order_equipment: list[dict[str, Any]] = []
        self.service_order_technicians: list[dict[str, Any]] = []
        self.user_sectors: list[dict[str, Any]] = []
        self.current_user: dict[str, Any] = {}
        self.session_login_at: datetime | None = None
        self.sidebar_collapsed = False
        self.record_editor_collapsed = True
        self.record_editor_width = 720
        self.admin_module_keys = (
            "sectors",
            "users",
            "password_resets",
            "audit_logs",
        )
        self.management_module_keys = ("financial", "reports", "notifications")
        self.dashboard_grid_columns = 4

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
            "financial": "financial",
            "notifications": "notifications",
            "sectors": "sectors",
            "users": "users",
            "password_resets": "password_resets",
            "settings": "settings",
            "reports": "reports",
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
            "reports": "Relatorios",
            "financial": "Financeiro",
            "audit_logs": "Logs/Auditoria",
            "notifications": "Notificacoes",
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
            "reports": "Relatorios operacionais e exportacoes",
            "financial": "Lancamentos, vencimentos e baixas",
            "audit_logs": "Rastreabilidade administrativa e operacional",
            "notifications": "Fila de comunicacoes e eventos",
            "admin_area": "Central de administracao, usuarios e auditoria",
        }
        self.searchable_module_keys = {
            "service_orders",
            "customers",
            "inventory",
            "sectors",
            "users",
            "password_resets",
            "financial",
            "audit_logs",
            "notifications",
        }
        self.record_module_keys = self.searchable_module_keys | {"reports"}
        module_groups = [
            ("OPERACAO", ("dashboard", "service_orders", "tools")),
            ("CADASTROS", ("customers", "equipment", "inventory")),
            ("GESTAO", ("financial", "reports", "notifications")),
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
        self.session_button.clicked.connect(self._open_settings_dialog)
        self.sidebar_layout.addWidget(self.session_button)

        self.logout_button = QPushButton("")
        self.logout_button.setObjectName("sidebarFooterButton")
        self.logout_button.setToolTip("Sair")
        self._configure_sidebar_button(self.logout_button, "logout", "Sair")
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.sidebar_layout.addWidget(self.logout_button)

        content = QFrame()
        content.setObjectName("contentPanel")
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_layout = create_grid(spacing=20, margins=(28, 28, 28, 28))
        content.setLayout(self.content_layout)

        self.title_label = QLabel("Dashboard")
        self.title_label.setObjectName("pageTitle")

        self.user_label = QLabel("")
        self.user_label.setObjectName("mutedText")

        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh_requested.emit)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)
        header_text_layout.addWidget(self.title_label)
        header_text_layout.addWidget(self.user_label)

        header_bar = QFrame()
        header_bar.setObjectName("headerBar")
        self.header_bar = header_bar
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(0, 0, 0, 2)
        header_layout.setSpacing(6)
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        self.dashboard_section_title = QLabel("Dashboard")
        self.dashboard_section_title.setObjectName("sectionTitle")

        self.dashboard_greeting_label = QLabel("")
        self.dashboard_greeting_label.setObjectName("dashboardGreeting")

        self.dashboard_last_refresh_label = QLabel("")
        self.dashboard_last_refresh_label.setObjectName("mutedText")

        self.dashboard_grid_widget = QWidget()
        self.dashboard_grid_widget.setObjectName("dashboardGrid")
        self.dashboard_grid_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self.dashboard_grid_layout = create_grid(spacing=4)
        self.dashboard_grid_widget.setLayout(self.dashboard_grid_layout)
        self.dashboard_grid_layout.setSpacing(4)
        self.dashboard_cards: dict[str, DashboardKpiCard] = {}
        self.dashboard_card_order: list[str] = []
        dashboard_cards = [
            ("service_orders_open", "OS", "OS abertas", "#238636", "service_orders"),
            (
                "service_orders_pending",
                "APROVACAO",
                "Aguardando aprovacao",
                "#d29922",
                "service_orders",
            ),
            ("inventory_total", "ESTOQUE", "Itens em estoque", "#0969da", "inventory"),
            ("inventory_low", "ALERTA", "Estoque critico", "#da3633", "inventory"),
            ("customers_total", "CLIENTES", "Clientes ativos", "#8250df", "customers"),
            ("equipment_total", "EQUIP", "Equipamentos cadastrados", "#1a7f37", "equipment"),
            ("users_total", "USUARIOS", "Usuarios ativos", "#bf8700", "users"),
            ("system_health", "SAUDE", "Pendencias operacionais", "#238636", None),
        ]

        for index, (key, marker, label, accent, target_module) in enumerate(dashboard_cards):
            card = DashboardKpiCard(key, marker, label, accent, target_module)
            card.clicked.connect(self.module_selected.emit)
            self.dashboard_cards[key] = card
            self.dashboard_card_order.append(key)
            self.dashboard_grid_layout.addWidget(card, index // 4, (index % 4) * 3, 1, 3)

        self.dashboard_alerts_frame = QFrame()
        self.dashboard_alerts_frame.setObjectName("dashboardAlertsFrame")
        self.dashboard_alerts_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.dashboard_alerts_layout = QVBoxLayout(self.dashboard_alerts_frame)
        self.dashboard_alerts_layout.setContentsMargins(10, 10, 10, 10)
        self.dashboard_alerts_layout.setSpacing(6)

        self.data_title = QLabel("Dados")
        self.data_title.setObjectName("sectionTitle")

        self.data_description = QLabel("")
        self.data_description.setObjectName("mutedText")
        self.data_description.setWordWrap(True)

        self.module_search_input = QLineEdit()
        self.module_search_input.setObjectName("moduleSearch")
        self.module_search_input.setPlaceholderText("BUSCAR REGISTROS...")
        self.module_search_input.setMinimumHeight(30)
        self.module_search_input.textChanged.connect(self._apply_current_filter)

        self.empty_label = QLabel("Selecione um modulo para carregar dados.")
        self.empty_label.setObjectName("mutedText")

        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setMinimumHeight(220)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_record_table_context_menu)
        self.table.itemSelectionChanged.connect(self._handle_table_selection)
        self.table.viewport().installEventFilter(self)

        self.customer_form_panel = self._build_customer_form()
        self.customer_form_panel.hide()
        self.equipment_form_panel = self._build_equipment_form()
        self.equipment_form_panel.hide()
        self.tools_form_panel = self._build_tools_form()
        self.tools_form_panel.hide()
        self.inventory_form_panel = self._build_inventory_form()
        self.inventory_form_panel.hide()
        self.service_order_form_panel = self._build_service_order_form()
        self.service_order_form_panel.hide()
        self.sector_form_panel = self._build_sector_form()
        self.sector_form_panel.hide()
        self.user_form_panel = self._build_user_form()
        self.user_form_panel.hide()
        self.password_reset_form_panel = self._build_password_reset_form()
        self.password_reset_form_panel.hide()
        self.settings_form_panel = self._build_settings_form()
        self.settings_form_panel.hide()
        self.report_form_panel = self._build_report_form()
        self.report_form_panel.hide()
        self.financial_form_panel = self._build_financial_form()
        self.financial_form_panel.hide()
        self.admin_area_panel = self._build_admin_area_panel()
        self.admin_area_panel.hide()
        self.audit_form_panel = self._build_audit_form()
        self.audit_form_panel.hide()
        self.notifications_form_panel = self._build_notifications_form()
        self.notifications_form_panel.hide()
        for module_panel in (
            self.equipment_form_panel,
            self.tools_form_panel,
            self.settings_form_panel,
            self.customer_form_panel,
            self.inventory_form_panel,
            self.service_order_form_panel,
            self.sector_form_panel,
            self.user_form_panel,
            self.password_reset_form_panel,
            self.report_form_panel,
            self.financial_form_panel,
            self.admin_area_panel,
            self.audit_form_panel,
            self.notifications_form_panel,
        ):
            module_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.record_list_panel = QFrame()
        self.record_list_panel.setObjectName("recordListPanel")
        self.record_list_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        record_list_layout = QVBoxLayout(self.record_list_panel)
        record_list_layout.setContentsMargins(0, 0, 0, 0)
        record_list_layout.setSpacing(7)
        record_list_layout.addWidget(self.data_title)
        record_list_layout.addWidget(self.data_description)
        record_list_layout.addWidget(self.module_search_input)
        record_list_layout.addWidget(self.empty_label)
        record_list_layout.addWidget(self.table, 1)

        self.generic_form_column = QFrame()
        self.generic_form_column.setObjectName("recordEditorPanel")
        self.generic_form_column.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        generic_form_layout = QVBoxLayout(self.generic_form_column)
        generic_form_layout.setContentsMargins(0, 0, 0, 0)
        generic_form_layout.setSpacing(0)
        generic_form_layout.addWidget(self.customer_form_panel)
        generic_form_layout.addWidget(self.inventory_form_panel)
        generic_form_layout.addWidget(self.service_order_form_panel)
        generic_form_layout.addWidget(self.sector_form_panel)
        generic_form_layout.addWidget(self.user_form_panel)
        generic_form_layout.addWidget(self.password_reset_form_panel)
        generic_form_layout.addWidget(self.report_form_panel)
        generic_form_layout.addWidget(self.financial_form_panel)
        generic_form_layout.addWidget(self.audit_form_panel)
        generic_form_layout.addWidget(self.notifications_form_panel)

        self.record_details_button = QPushButton("D\na\nd\no\ns")
        self.record_details_button.setObjectName("recordEditorToggleButton")
        self.record_details_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_details_button.setToolTip("Abrir dados completos do item selecionado")
        self.record_details_button.setFixedSize(42, 120)
        self.record_details_button.clicked.connect(self._open_record_details)

        self.record_editor_toggle_button = QPushButton("E\nd\ni\nt\no\nr")
        self.record_editor_toggle_button.setObjectName("recordEditorToggleButton")
        self.record_editor_toggle_button.setCheckable(True)
        self.record_editor_toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_editor_toggle_button.setToolTip("Abrir editor de registro")
        self.record_editor_toggle_button.setFixedSize(42, 132)
        self.record_editor_toggle_button.toggled.connect(self._set_record_editor_open)

        self.record_toggle_rail = QFrame()
        self.record_toggle_rail.setObjectName("recordToggleRail")
        self.record_toggle_rail.setFixedWidth(56)
        self.record_toggle_rail.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        record_toggle_layout = QVBoxLayout(self.record_toggle_rail)
        record_toggle_layout.setContentsMargins(4, 2, 4, 0)
        record_toggle_layout.setSpacing(6)
        record_toggle_layout.addWidget(
            self.record_details_button,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        )
        record_toggle_layout.addWidget(
            self.record_editor_toggle_button,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        )
        record_toggle_layout.addStretch()

        self.generic_record_container = QFrame()
        self.generic_record_container.setObjectName("recordModuleContainer")
        self.generic_record_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        generic_record_layout = QHBoxLayout(self.generic_record_container)
        generic_record_layout.setContentsMargins(0, 0, 0, 0)
        generic_record_layout.setSpacing(8)
        self.generic_form_column.setParent(self.generic_record_container)
        self.generic_form_column.hide()
        generic_record_layout.addWidget(self.record_list_panel, 1)
        generic_record_layout.addWidget(self.record_toggle_rail)

        add_widget(self.content_layout, header_bar, 0)
        add_widget(self.content_layout, self.dashboard_section_title, 1)
        add_widget(self.content_layout, self.dashboard_greeting_label, 2)
        add_widget(self.content_layout, self.dashboard_last_refresh_label, 3)
        add_widget(self.content_layout, self.dashboard_grid_widget, 4)
        add_widget(self.content_layout, self.dashboard_alerts_frame, 5)
        add_widget(self.content_layout, self.generic_record_container, 6)
        add_widget(self.content_layout, self.equipment_form_panel, 7)
        add_widget(self.content_layout, self.tools_form_panel, 8)
        add_widget(self.content_layout, self.settings_form_panel, 9)
        add_widget(self.content_layout, self.admin_area_panel, 10)
        self._reset_content_row_stretches()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area.setWidget(content)

        self.session_footer = QFrame()
        self.session_footer.setObjectName("sessionFooter")
        session_footer_layout = QHBoxLayout(self.session_footer)
        session_footer_layout.setContentsMargins(10, 4, 10, 4)
        session_footer_layout.setSpacing(8)
        self.session_footer_label = QLabel("Sessao: -")
        self.session_footer_label.setObjectName("sessionFooterText")
        self.backend_status_dot = QLabel("●")
        self.backend_status_dot.setObjectName("footerStatusDot")
        self.backend_status_dot.setProperty("level", "error")
        self.backend_status_text = QLabel("Backend: desconectado")
        self.backend_status_text.setObjectName("sessionFooterText")
        self.internal_server_status_dot = QLabel("●")
        self.internal_server_status_dot.setObjectName("footerStatusDot")
        self.internal_server_status_dot.setProperty("level", "warning")
        self.internal_server_status_text = QLabel("Servidor interno: pendente")
        self.internal_server_status_text.setObjectName("sessionFooterText")
        self.footer_message_label = QLabel("")
        self.footer_message_label.setObjectName("footerMessage")
        self.footer_message_label.setProperty("level", "info")
        self.session_module_label = QLabel("Painel Principal")
        self.session_module_label.setObjectName("sessionFooterModule")
        session_footer_layout.addWidget(self.session_footer_label)
        session_footer_layout.addStretch()
        session_footer_layout.addWidget(self.footer_message_label, 1)
        session_footer_layout.addWidget(self.backend_status_dot)
        session_footer_layout.addWidget(self.backend_status_text)
        session_footer_layout.addWidget(self.internal_server_status_dot)
        session_footer_layout.addWidget(self.internal_server_status_text)
        session_footer_layout.addWidget(self.session_module_label)

        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self._refresh_session_footer)
        self.session_timer.start()

        main_area = QFrame()
        main_area.setObjectName("mainArea")
        main_area_layout = QHBoxLayout(main_area)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)
        main_area_layout.addWidget(self.sidebar)
        main_area_layout.addWidget(scroll_area, 1)

        self.menu_bar = QMenuBar()
        file_menu = self.menu_bar.addMenu("Arquivo")
        settings_action = QAction("Configuracoes", self)
        settings_action.triggered.connect(lambda: self.module_selected.emit("settings"))
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        logout_action = QAction("Sair", self)
        logout_action.triggered.connect(self.logout_requested.emit)
        file_menu.addAction(logout_action)

        edit_menu = self.menu_bar.addMenu("Editar")
        details_action = QAction("Dados completos", self)
        details_action.triggered.connect(self._open_record_details)
        edit_menu.addAction(details_action)
        editor_action = QAction("Editor de registro", self)
        editor_action.triggered.connect(self._open_record_editor)
        edit_menu.addAction(editor_action)

        selection_menu = self.menu_bar.addMenu("Selecao")
        clear_selection_action = QAction("Limpar selecao", self)
        clear_selection_action.triggered.connect(self._clear_current_selection)
        selection_menu.addAction(clear_selection_action)

        about_menu = self.menu_bar.addMenu("Sobre")
        about_action = QAction("Sobre o Pro Core", self)
        about_action.triggered.connect(
            lambda: QMessageBox.information(
                self,
                "Sobre",
                "PRO CORE\nSistema de gestao operacional.",
            )
        )
        about_menu.addAction(about_action)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.menu_bar)
        layout.addWidget(main_area, 1)
        layout.addWidget(self.session_footer)
        self._apply_compact_density()
        self._install_input_guards()
        self.apply_display_profile()
        self._set_record_editor_open(False)
        self._mark_active_nav(self.active_module_key)

