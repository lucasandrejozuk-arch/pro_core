from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
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
    content.setLayout(self.content_layout)

    self.title_label = QLabel("Dashboard")
    self.title_label.setObjectName("pageTitle")

    self.user_label = QLabel("")
    self.user_label.setObjectName("mutedText")

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
        QSizePolicy.Policy.Minimum,
    )
    self.dashboard_alerts_layout = QVBoxLayout(self.dashboard_alerts_frame)
    self.dashboard_alerts_layout.setContentsMargins(10, 10, 10, 10)
    self.dashboard_alerts_layout.setSpacing(6)

    self.data_title = QLabel("Dados")
    self.data_title.setObjectName("sectionTitle")

    self.data_description = QLabel("")
    self.data_description.setObjectName("mutedText")
    self.data_description.setWordWrap(True)
    self.record_count_label = QLabel("")
    self.record_count_label.setObjectName("mutedText")

    self.module_search_input = QLineEdit()
    self.module_search_input.setObjectName("moduleSearch")
    self.module_search_input.setPlaceholderText("BUSCAR REGISTROS...")
    self.module_search_input.setMinimumHeight(30)
    self.module_search_input.textChanged.connect(self._apply_current_filter)

    self.empty_label = QLabel("Selecione um modulo para carregar dados.")
    self.empty_label.setObjectName("mutedText")

    self.table = QTableWidget()
    self.table.setObjectName("dataTable")
    self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
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
    record_list_layout.addWidget(self.record_count_label)
    record_list_layout.addWidget(self.module_search_input)
    record_list_layout.addWidget(self.empty_label)
    record_list_layout.addWidget(self.table)
    record_list_layout.addStretch(1)
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
    generic_form_layout.addWidget(self.customer_form_panel)
    generic_form_layout.addWidget(self.inventory_form_panel)
    generic_form_layout.addWidget(self.service_order_form_panel)
    generic_form_layout.addWidget(self.sector_form_panel)
    generic_form_layout.addWidget(self.user_form_panel)
    generic_form_layout.addWidget(self.password_reset_form_panel)
    generic_form_layout.addWidget(self.audit_form_panel)

    self.record_toggle_rail = QFrame()
    self.record_toggle_rail.setObjectName("recordToggleRail")
    self.record_toggle_rail.setFixedWidth(0)
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
    self.generic_form_column.setParent(self.generic_record_container)
    self.generic_form_column.hide()
    generic_record_layout.addWidget(self.record_list_panel, 1)

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

    return scroll_area
