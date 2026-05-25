from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.grid import add_widget, create_grid
from frontend.app.widgets import DashboardKpiCard, create_summary_text


def build_dashboard_content(self) -> QScrollArea:
    content = QFrame()
    content.setObjectName("contentPanel")
    content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.content_layout = create_grid(spacing=20, margins=(28, 28, 28, 28))
    self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    content.setLayout(self.content_layout)

    self.title_label = QLabel("Dashboard")
    self.title_label.setObjectName("pageTitle")

    self.user_label = QLabel("")
    self.user_label.setObjectName("mutedText")

    header_text_layout = QVBoxLayout()
    header_text_layout.setContentsMargins(0, 0, 0, 0)
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
    header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
            "APROVAÇÃO",
            "Aguardando aprovação",
            "#d29922",
            "service_orders",
        ),
        ("inventory_total", "ESTOQUE", "Itens em estoque", "#0969da", "inventory"),
        ("inventory_low", "ALERTA", "Estoque critico", "#da3633", "inventory"),
        ("customers_total", "CLIENTES", "Clientes ativos", "#8250df", "customers"),
        ("equipment_total", "EQUIP", "Equipamentos cadastrados", "#1a7f37", "equipment"),
        ("users_total", "USUÁRIOS", "Usuários ativos", "#bf8700", "users"),
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
        QSizePolicy.Policy.Minimum,
    )
    self.dashboard_alerts_layout = QVBoxLayout(self.dashboard_alerts_frame)
    self.dashboard_alerts_layout.setContentsMargins(10, 10, 10, 10)
    self.dashboard_alerts_layout.setSpacing(6)

    self.dashboard_body_panel = QFrame()
    self.dashboard_body_panel.setObjectName("dashboardBodyPanel")
    self.dashboard_body_panel.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Minimum,
    )
    dashboard_body_layout = QVBoxLayout(self.dashboard_body_panel)
    dashboard_body_layout.setContentsMargins(0, 0, 0, 0)
    dashboard_body_layout.setSpacing(8)
    dashboard_body_layout.addWidget(self.dashboard_section_title)
    dashboard_body_layout.addWidget(self.dashboard_greeting_label)
    dashboard_body_layout.addWidget(self.dashboard_last_refresh_label)
    dashboard_body_layout.addWidget(self.dashboard_grid_widget)
    dashboard_body_layout.addWidget(self.dashboard_alerts_frame)

    self.data_title = QLabel("Dados")
    self.data_title.setObjectName("sectionTitle")

    self.data_description = QLabel("")
    self.data_description.setObjectName("mutedText")
    self.data_description.setWordWrap(True)
    self.module_guidance_label = QLabel("")
    self.module_guidance_label.setObjectName("mutedText")
    self.module_guidance_label.setWordWrap(True)
    self.module_guidance_label.hide()
    self.record_count_label = QLabel("")
    self.record_count_label.setObjectName("mutedText")

    self.module_search_input = QLineEdit()
    self.module_search_input.setObjectName("moduleSearch")
    self.module_search_input.setPlaceholderText("BUSCAR REGISTROS...")
    self.module_search_input.setMinimumHeight(30)
    self.module_search_input.textChanged.connect(self._apply_current_filter)

    self.empty_label = QLabel("Selecione um modulo para carregar dados.")
    self.empty_label.setObjectName("emptyStateText")
    self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
    self.table.setMinimumHeight(150)
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
    self.resource_access_form_panel = self._build_resource_access_form()
    self.resource_access_form_panel.hide()
    self.password_reset_form_panel = self._build_password_reset_form()
    self.password_reset_form_panel.hide()
    self.settings_form_panel = self._build_settings_form()
    self.settings_form_panel.hide()
    self.admin_area_panel = self._build_admin_area_panel()
    self.admin_area_panel.hide()
    self.audit_form_panel = self._build_audit_form()
    self.audit_form_panel.hide()
    for module_panel in (
        self.equipment_form_panel,
        self.tools_form_panel,
        self.settings_form_panel,
        self.customer_form_panel,
        self.inventory_form_panel,
        self.service_order_form_panel,
        self.sector_form_panel,
        self.user_form_panel,
        self.resource_access_form_panel,
        self.password_reset_form_panel,
        self.admin_area_panel,
        self.audit_form_panel,
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
    record_list_layout.addWidget(self.module_guidance_label)
    record_list_layout.addWidget(self.record_count_label)
    record_list_layout.addWidget(self.module_search_input)
    record_list_layout.addWidget(self.empty_label)
    record_list_layout.addWidget(self.table, 1)

    self.pagination_bar = QFrame()
    self.pagination_bar.setObjectName("recordPaginationBar")
    pagination_layout = QHBoxLayout(self.pagination_bar)
    pagination_layout.setContentsMargins(0, 0, 0, 0)
    pagination_layout.setSpacing(8)

    self.pagination_prev_button = QPushButton("Anterior")
    self.pagination_prev_button.setObjectName("secondaryButton")
    self.pagination_prev_button.clicked.connect(self._go_previous_page)

    self.pagination_next_button = QPushButton("Proxima")
    self.pagination_next_button.setObjectName("secondaryButton")
    self.pagination_next_button.clicked.connect(self._go_next_page)

    self.pagination_label = QLabel("Pagina 1 de 1")
    self.pagination_label.setObjectName("mutedText")

    self.pagination_size_combo = QComboBox()
    self.pagination_size_combo.setObjectName("sectionSearch")
    self.pagination_size_combo.addItem("10 por pagina", 10)
    self.pagination_size_combo.addItem("20 por pagina", 20)
    self.pagination_size_combo.addItem("50 por pagina", 50)
    self.pagination_size_combo.currentIndexChanged.connect(self._set_page_size)

    pagination_layout.addWidget(self.pagination_prev_button)
    pagination_layout.addWidget(self.pagination_next_button)
    pagination_layout.addWidget(self.pagination_label)
    pagination_layout.addStretch()
    pagination_layout.addWidget(self.pagination_size_combo)
    self.pagination_bar.hide()
    record_list_layout.addWidget(self.pagination_bar)

    self.record_summary_panel = QFrame()
    self.record_summary_panel.setObjectName("recordSummaryPanel")
    record_summary_layout = QVBoxLayout(self.record_summary_panel)
    record_summary_layout.setContentsMargins(10, 10, 10, 10)
    record_summary_layout.setSpacing(6)
    self.record_summary_title = QLabel("Resumo do item selecionado")
    self.record_summary_title.setObjectName("formGroupTitle")
    self.record_summary_text = create_summary_text(78, 118)
    self.record_summary_text.setPlainText("Nenhum item selecionado.")
    record_summary_layout.addWidget(self.record_summary_title)
    record_summary_layout.addWidget(self.record_summary_text)
    record_list_layout.addWidget(self.record_summary_panel)

    self.generic_form_column = QFrame()
    self.generic_form_column.setObjectName("recordEditorPanel")
    self.generic_form_column.setSizePolicy(
        QSizePolicy.Policy.Fixed,
        QSizePolicy.Policy.Expanding,
    )
    generic_form_layout = QVBoxLayout(self.generic_form_column)
    generic_form_layout.setContentsMargins(0, 0, 0, 0)
    generic_form_layout.setSpacing(0)
    generic_form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    generic_form_layout.addWidget(self.customer_form_panel)
    generic_form_layout.addWidget(self.inventory_form_panel)
    generic_form_layout.addWidget(self.service_order_form_panel)
    generic_form_layout.addWidget(self.sector_form_panel)
    generic_form_layout.addWidget(self.user_form_panel)
    generic_form_layout.addWidget(self.resource_access_form_panel)
    generic_form_layout.addWidget(self.password_reset_form_panel)
    generic_form_layout.addWidget(self.audit_form_panel)

    self.record_toggle_rail = QFrame()
    self.record_toggle_rail.setObjectName("recordToggleRail")
    self.record_toggle_rail.setFixedWidth(34)
    rail_layout = QVBoxLayout(self.record_toggle_rail)
    rail_layout.setContentsMargins(4, 10, 4, 10)
    rail_layout.setSpacing(0)
    self.record_toggle_button = QPushButton("E\nD\nI\nT\nO\nR")
    self.record_toggle_button.setObjectName("recordEditorToggleButton")
    self.record_toggle_button.setToolTip("Abrir editor")
    self.record_toggle_button.clicked.connect(self._open_record_editor)
    rail_layout.addWidget(self.record_toggle_button)
    rail_layout.addStretch()
    self.record_toggle_rail.setParent(self)
    self.record_toggle_rail.hide()

    self.generic_record_container = QFrame()
    self.generic_record_container.setObjectName("recordModuleContainer")
    self.generic_record_container.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding,
    )
    generic_record_layout = QHBoxLayout(self.generic_record_container)
    generic_record_layout.setContentsMargins(0, 0, 0, 0)
    generic_record_layout.setSpacing(8)
    self.generic_form_column.setParent(self)
    self.generic_form_column.hide()
    generic_record_layout.addWidget(self.record_list_panel, 1)
    self.generic_record_container.hide()

    add_widget(self.content_layout, header_bar, 0)
    add_widget(self.content_layout, self.dashboard_body_panel, 1)
    add_widget(self.content_layout, self.generic_record_container, 1)
    add_widget(self.content_layout, self.equipment_form_panel, 1)
    add_widget(self.content_layout, self.tools_form_panel, 1)
    add_widget(self.content_layout, self.settings_form_panel, 1)
    add_widget(self.content_layout, self.admin_area_panel, 1)
    self._reset_content_row_stretches()

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.Shape.NoFrame)
    scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    scroll_area.setWidget(content)
    self.main_scroll_area = scroll_area

    return scroll_area
