from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.display import DisplayProfile, detect_display_profile
from frontend.app.core.icons import build_icon
from frontend.app.widgets import DashboardKpiCard, create_summary_text


class EquipmentAssetDialog(QDialog):
    def __init__(
        self,
        title: str,
        fields: list[dict[str, Any]],
        values: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setObjectName("assetDialog")
        self.fields = fields
        self.inputs: dict[str, QLineEdit | QTextEdit] = {}
        self._payload: dict[str, Any] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        values = values or {}
        for field in fields:
            key = str(field["key"])
            if field.get("multiline"):
                input_widget = QTextEdit()
                input_widget.setPlaceholderText(str(field.get("placeholder") or ""))
                input_widget.setPlainText(str(values.get(key) or ""))
                input_widget.setMinimumHeight(72)
                input_widget.setMaximumHeight(96)
            else:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(str(field.get("placeholder") or ""))
                input_widget.setText(str(values.get(key) or ""))
            self.inputs[key] = input_widget
            form_layout.addRow(str(field["label"]), input_widget)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorText")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(form_layout)
        layout.addWidget(self.error_label)
        layout.addLayout(button_layout)
        self.resize(450, 320)

    def payload(self) -> dict[str, Any]:
        return dict(self._payload)

    def _accept(self) -> None:
        try:
            self._payload = self._build_payload()
        except ValueError as exc:
            self.error_label.setText(str(exc))
            return
        self.accept()

    def _build_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for field in self.fields:
            key = str(field["key"])
            input_widget = self.inputs[key]
            if isinstance(input_widget, QTextEdit):
                raw_value = input_widget.toPlainText().strip()
            else:
                raw_value = input_widget.text().strip()

            if field.get("required") and not raw_value:
                raise ValueError(f"Informe {str(field['label']).replace(':', '').lower()}.")

            if field.get("money"):
                payload[key] = self._normalize_money(raw_value)
                continue

            payload[key] = raw_value or None

        return payload

    @staticmethod
    def _normalize_money(raw_value: str) -> str:
        value = raw_value.strip()
        if not value:
            return "0"
        if "," in value:
            value = value.replace(".", "").replace(",", ".")
        try:
            decimal_value = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("Valor unitario deve ser numerico.") from exc
        if decimal_value < 0:
            raise ValueError("Valor unitario nao pode ser negativo.")
        return str(decimal_value)


class DashboardWindow(QWidget):
    logout_requested = Signal()
    module_selected = Signal(str)
    refresh_requested = Signal()
    customer_create_requested = Signal(dict)
    customer_update_requested = Signal(str, dict)
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
    inventory_create_requested = Signal(dict)
    inventory_update_requested = Signal(str, dict)
    sector_create_requested = Signal(dict)
    sector_update_requested = Signal(str, dict)
    service_order_create_requested = Signal(dict)
    service_order_update_requested = Signal(str, dict)
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
    backup_run_requested = Signal()
    report_view_requested = Signal(str)
    report_export_requested = Signal(str, str, str)
    financial_create_requested = Signal(dict)
    financial_mark_paid_requested = Signal(str)
    financial_cancel_requested = Signal(str)

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
        self.current_user_role = ""
        self.equipment_customers: list[dict[str, Any]] = []
        self.service_order_customers: list[dict[str, Any]] = []
        self.service_order_equipment: list[dict[str, Any]] = []
        self.service_order_technicians: list[dict[str, Any]] = []
        self.user_sectors: list[dict[str, Any]] = []
        self.current_user: dict[str, Any] = {}
        self.session_login_at: datetime | None = None
        self.sidebar_collapsed = False
        self.admin_module_keys = (
            "financial",
            "notifications",
            "sectors",
            "users",
            "password_resets",
            "settings",
            "reports",
            "audit_logs",
        )
        self.dashboard_grid_columns = 4

        self.setWindowTitle("PRO CORE - Dashboard")
        self.setMinimumSize(1120, 720)
        self.setObjectName("dashboardWindow")

        self.sidebar_expanded_width = 72
        self.sidebar_collapsed_width = 44
        self.sidebar_margin = 18
        self.sidebar_icon_color = "#ffffff"
        self.sidebar_icon_size = QSize(22, 22)
        self.sidebar_buttons_by_icon: dict[QPushButton, str] = {}

        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(self.sidebar_expanded_width)

        self.sidebar_title = QLabel("PRO CORE")
        self.sidebar_title.setObjectName("sidebarTitle")
        self.sidebar_title.hide()

        self.sidebar_text = QLabel("Assistencia tecnica")
        self.sidebar_text.setObjectName("sidebarText")
        self.sidebar_text.hide()

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        self.sidebar_toggle_button = QPushButton("")
        self.sidebar_toggle_button.setObjectName("sidebarToggleButton")
        self.sidebar_toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sidebar_toggle_button.setToolTip("Recolher menu")
        self.sidebar_toggle_button.clicked.connect(self._toggle_sidebar)
        self._configure_sidebar_button(self.sidebar_toggle_button, "menu", "Recolher menu")
        sidebar_layout.addWidget(self.sidebar_toggle_button)

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
            "admin_menu": "admin",
        }
        self.module_labels = {
            "dashboard": "Dashboard",
            "service_orders": "Ordens de Servico",
            "customers": "Clientes",
            "equipment": "Equipamentos",
            "inventory": "Estoque",
            "sectors": "Setores",
            "users": "Usuarios",
            "password_resets": "Solicitacoes de senha",
            "settings": "Configuracoes",
            "reports": "Relatorios",
            "financial": "Financeiro",
            "audit_logs": "Logs/Auditoria",
            "notifications": "Notificacoes",
        }
        self.module_descriptions = {
            "dashboard": "Indicadores operacionais e alertas do dia",
            "service_orders": "Fluxo operacional de ordens de servico",
            "customers": "Cadastro e relacionamento de clientes",
            "equipment": "Gestao hierarquica de ativos, objetos e componentes",
            "inventory": "Estoque, custos e niveis minimos",
            "sectors": "Setores, liderancas e estrutura operacional",
            "users": "Contas, perfis, setores e seguranca",
            "password_resets": "Atendimento de solicitacoes de acesso",
            "settings": "Identidade visual, empresa, tema e backup",
            "reports": "Relatorios operacionais e exportacoes",
            "financial": "Lancamentos, vencimentos e baixas",
            "audit_logs": "Rastreabilidade administrativa e operacional",
            "notifications": "Fila de comunicacoes e eventos",
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
            ("OPERACAO", ("dashboard", "service_orders")),
            ("CADASTROS", ("customers", "equipment", "inventory")),
            ("GESTAO", ("admin_menu",)),
        ]

        for caption, module_keys in module_groups:
            if sidebar_nav_layout.count() > 0:
                separator = QFrame()
                separator.setObjectName("sidebarSeparator")
                separator.setFixedHeight(1)
                sidebar_nav_layout.addWidget(separator)
            for module_key in module_keys:
                button_label = (
                    "Area Administrativa"
                    if module_key == "admin_menu"
                    else self.module_labels[module_key]
                )
                button = QPushButton("")
                button.setObjectName("navButton")
                button.setCheckable(module_key != "admin_menu")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setProperty("active", "false")
                self._configure_sidebar_button(
                    button,
                    self.module_icon_names[module_key],
                    f"{caption.title()} - {button_label}",
                )
                if module_key == "admin_menu":
                    button.clicked.connect(self._open_admin_menu)
                    self.admin_menu_button = button
                else:
                    button.clicked.connect(
                        lambda checked=False, key=module_key: self.module_selected.emit(key)
                    )
                    self.module_buttons[module_key] = button
                sidebar_nav_layout.addWidget(button)

        sidebar_layout.addWidget(self.sidebar_nav_container)

        sidebar_layout.addStretch()

        self.session_info_label = QLabel("")
        self.session_info_label.setObjectName("sidebarSessionInfo")
        self.session_info_label.setWordWrap(True)
        self.session_info_label.hide()

        self.session_button = QPushButton("")
        self.session_button.setObjectName("sidebarFooterButton")
        self.session_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._configure_sidebar_button(self.session_button, "session", "Sessao ativa")
        sidebar_layout.addWidget(self.session_button)

        self.logout_button = QPushButton("")
        self.logout_button.setObjectName("sidebarFooterButton")
        self.logout_button.setToolTip("Sair")
        self._configure_sidebar_button(self.logout_button, "logout", "Sair")
        self.logout_button.clicked.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(self.logout_button)

        content = QFrame()
        content.setObjectName("contentPanel")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(28, 28, 28, 28)
        self.content_layout.setSpacing(20)

        self.title_label = QLabel("Dashboard")
        self.title_label.setObjectName("pageTitle")

        self.user_label = QLabel("")
        self.user_label.setObjectName("mutedText")

        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh_requested.emit)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(6)
        header_text_layout.addWidget(self.title_label)
        header_text_layout.addWidget(self.user_label)

        header_bar = QFrame()
        header_bar.setObjectName("headerBar")
        self.header_bar = header_bar
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(10)
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
        self.dashboard_grid_layout = QGridLayout(self.dashboard_grid_widget)
        self.dashboard_grid_layout.setSpacing(8)
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
            self.dashboard_grid_layout.addWidget(card, index // 4, index % 4)

        self.dashboard_alerts_frame = QFrame()
        self.dashboard_alerts_frame.setObjectName("dashboardAlertsFrame")
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
        self.table.itemSelectionChanged.connect(self._handle_table_selection)

        self.customer_form_panel = self._build_customer_form()
        self.customer_form_panel.hide()
        self.equipment_form_panel = self._build_equipment_form()
        self.equipment_form_panel.hide()
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
        self.audit_form_panel = self._build_audit_form()
        self.audit_form_panel.hide()
        self.notifications_form_panel = self._build_notifications_form()
        self.notifications_form_panel.hide()

        self.record_list_panel = QFrame()
        self.record_list_panel.setObjectName("recordListPanel")
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

        self.generic_record_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.generic_record_splitter.setObjectName("recordModuleSplitter")
        self.generic_record_splitter.addWidget(self.record_list_panel)
        self.generic_record_splitter.addWidget(self.generic_form_column)
        self.generic_record_splitter.setStretchFactor(0, 3)
        self.generic_record_splitter.setStretchFactor(1, 4)
        self.generic_record_splitter.setSizes([760, 980])

        self.content_layout.addWidget(header_bar)
        self.content_layout.addWidget(self.dashboard_section_title)
        self.content_layout.addWidget(self.dashboard_greeting_label)
        self.content_layout.addWidget(self.dashboard_last_refresh_label)
        self.content_layout.addWidget(self.dashboard_grid_widget)
        self.content_layout.addWidget(self.dashboard_alerts_frame)
        self.content_layout.addWidget(self.generic_record_splitter)
        self.content_layout.addWidget(self.equipment_form_panel)
        self.content_layout.addWidget(self.settings_form_panel)
        self.content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(content)

        self.session_footer = QFrame()
        self.session_footer.setObjectName("sessionFooter")
        session_footer_layout = QHBoxLayout(self.session_footer)
        session_footer_layout.setContentsMargins(10, 4, 10, 4)
        session_footer_layout.setSpacing(8)
        self.session_footer_label = QLabel("Sessao: -")
        self.session_footer_label.setObjectName("sessionFooterText")
        self.session_module_label = QLabel("Painel Principal")
        self.session_module_label.setObjectName("sessionFooterModule")
        session_footer_layout.addWidget(self.session_footer_label)
        session_footer_layout.addStretch()
        session_footer_layout.addWidget(self.session_module_label)

        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self._refresh_session_footer)
        self.session_timer.start()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(scroll_area)
        layout.addWidget(self.session_footer)
        self._apply_compact_density()
        self._install_input_guards()
        self.apply_display_profile()
        self.sidebar.raise_()
        self._mark_active_nav(self.active_module_key)

    def _configure_sidebar_button(self, button: QPushButton, icon_name: str, tooltip: str) -> None:
        button.setText("")
        button.setToolTip(tooltip)
        button.setIcon(build_icon(icon_name, self.sidebar_icon_color))
        button.setIconSize(self.sidebar_icon_size)
        button.setFixedSize(44, 44)
        self.sidebar_buttons_by_icon[button] = icon_name

    def _apply_compact_density(self) -> None:
        for frame in self.findChildren(QFrame):
            layout = frame.layout()
            if layout is None:
                continue

            object_name = frame.objectName()
            if object_name == "formPanel":
                layout.setContentsMargins(10, 10, 10, 10)
                layout.setSpacing(8)
            elif object_name in {"formSubPanel", "workflowPanel", "equipmentSection"}:
                layout.setContentsMargins(8, 8, 8, 8)
                layout.setSpacing(6)

        for form_layout in self.findChildren(QFormLayout):
            form_layout.setHorizontalSpacing(8)
            form_layout.setVerticalSpacing(6)

        for table in self.findChildren(QTableWidget):
            table.verticalHeader().setDefaultSectionSize(34)
            table.horizontalHeader().setMinimumSectionSize(96)
            table.setShowGrid(False)
            table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def apply_sidebar_icon_color(self, color: str) -> None:
        self.sidebar_icon_color = color
        for button, icon_name in self.sidebar_buttons_by_icon.items():
            button.setIcon(build_icon(icon_name, color))
            button.setIconSize(self.sidebar_icon_size)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel and isinstance(watched, (QComboBox, QAbstractSpinBox)):
            return True

        return super().eventFilter(watched, event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if not hasattr(self, "dashboard_grid_layout"):
            return
        if self.width() < 1320:
            self._set_dashboard_grid_columns(2)
        elif self.width() >= 1500:
            self._set_dashboard_grid_columns(4)
        self._position_sidebar()

    def apply_display_profile(self, profile: DisplayProfile | None = None) -> None:
        active_profile = profile or detect_display_profile()
        self.sidebar_expanded_width = active_profile.sidebar_width
        self.sidebar_collapsed_width = active_profile.collapsed_sidebar_width
        self.sidebar_margin = active_profile.content_margin
        self.sidebar.setFixedWidth(
            self.sidebar_collapsed_width if self.sidebar_collapsed else self.sidebar_expanded_width
        )
        self.content_layout.setContentsMargins(
            active_profile.content_margin + active_profile.sidebar_width + 18,
            active_profile.content_margin,
            active_profile.content_margin,
            active_profile.content_margin,
        )
        self.content_layout.setSpacing(active_profile.section_spacing)
        self.dashboard_grid_layout.setSpacing(max(6, active_profile.section_spacing // 2))
        self._set_dashboard_grid_columns(active_profile.dashboard_columns)
        self._position_sidebar()

    def _position_sidebar(self) -> None:
        if not hasattr(self, "sidebar"):
            return

        footer_height = self.session_footer.height() if hasattr(self, "session_footer") else 0
        height = max(280, self.height() - footer_height - (self.sidebar_margin * 2))
        width = (
            self.sidebar_collapsed_width if self.sidebar_collapsed else self.sidebar_expanded_width
        )
        self.sidebar.setGeometry(self.sidebar_margin, self.sidebar_margin, width, height)
        self.sidebar.raise_()

    def _set_dashboard_grid_columns(self, columns: int) -> None:
        normalized_columns = max(1, min(columns, 4))
        if normalized_columns == self.dashboard_grid_columns:
            return

        while self.dashboard_grid_layout.count():
            self.dashboard_grid_layout.takeAt(0)

        for index, key in enumerate(self.dashboard_card_order):
            self.dashboard_grid_layout.addWidget(
                self.dashboard_cards[key],
                index // normalized_columns,
                index % normalized_columns,
            )
        self.dashboard_grid_columns = normalized_columns

    def set_user(self, user: dict[str, Any]) -> None:
        self.current_user = dict(user)
        role_key = str(user.get("role", ""))
        self.current_user_role = role_key
        role = self._format_value(role_key) or role_key.replace("_", " ").title()
        full_name = user.get("full_name", "Usuario")
        email = user.get("email", "")
        self.user_label.setText(f"{full_name} | {email} | Perfil: {role}")
        self.session_info_label.setText(
            "\n".join(
                [
                    "Sessao ativa",
                    str(full_name or "Usuario"),
                    str(email or "-"),
                    f"Perfil: {role}",
                ]
            )
        )
        self.session_button.setToolTip(self.session_info_label.text())
        self.admin_menu_button.setVisible(
            not self.sidebar_collapsed and bool(self._allowed_admin_modules())
        )
        if "users_total" in self.dashboard_cards:
            self.dashboard_cards["users_total"].setVisible(role_key in {"admin", "manager"})
        self._refresh_session_footer()

    def set_session_login_at(self, login_at: datetime | None) -> None:
        self.session_login_at = login_at
        self._refresh_session_footer()

    def _refresh_session_footer(self) -> None:
        if not hasattr(self, "session_footer_label"):
            return

        role = self._format_value(self.current_user.get("role")) or "Usuario"
        sector = (
            str(self.current_user.get("sector_name") or "").strip()
            or self._lookup_label(
                self.user_sectors,
                self.current_user.get("sector_id"),
                "name",
                "",
            )
            or "Sem setor"
        )
        if self.session_login_at is None:
            login_text = "-"
            elapsed_text = "00:00:00"
        else:
            login_text = self.session_login_at.strftime("%Y-%m-%d %H:%M:%S")
            total_seconds = max(0, int((datetime.now() - self.session_login_at).total_seconds()))
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.session_footer_label.setText(
            f"* Sessao: {role} | Setor: {sector} | Login: {login_text} | Tempo: {elapsed_text}"
        )

    def apply_branding(self, settings: dict[str, Any]) -> None:
        brand_name = str(
            settings.get("brand_name")
            or settings.get("trade_name")
            or settings.get("company_name")
            or "PRO CORE"
        ).strip()
        brand_subtitle = str(
            settings.get("brand_subtitle") or settings.get("trade_name") or "Assistencia tecnica"
        ).strip()
        self.sidebar_title.setText(brand_name or "PRO CORE")
        self.sidebar_text.setText(brand_subtitle or "Assistencia tecnica")
        self.sidebar.setToolTip(
            f"{brand_name or 'PRO CORE'}\n{brand_subtitle or 'Assistencia tecnica'}"
        )
        self.setWindowTitle(f"{brand_name or 'PRO CORE'} - {self.title_label.text()}")

    def _toggle_sidebar(self) -> None:
        self._set_sidebar_collapsed(not self.sidebar_collapsed)

    def _set_sidebar_collapsed(self, collapsed: bool) -> None:
        self.sidebar_collapsed = collapsed
        self.sidebar_nav_container.setVisible(not collapsed)
        self.session_button.setVisible(not collapsed)
        self.logout_button.setVisible(not collapsed)
        self.admin_menu_button.setVisible(not collapsed and bool(self._allowed_admin_modules()))
        tooltip = "Expandir menu" if collapsed else "Recolher menu"
        self.sidebar_toggle_button.setToolTip(tooltip)
        self.sidebar_toggle_button.setFixedSize(
            32 if collapsed else 44,
            44,
        )
        self.sidebar.setFixedWidth(
            self.sidebar_collapsed_width if collapsed else self.sidebar_expanded_width
        )
        self._position_sidebar()

    def _open_admin_menu(self) -> None:
        allowed_modules = self._allowed_admin_modules()
        if not allowed_modules:
            return

        dialog = QDialog(self)
        dialog.setObjectName("adminMenuDialog")
        dialog.setWindowTitle("Area Administrativa")
        dialog.setModal(True)
        dialog.resize(480, 420)

        title = QLabel("Area Administrativa")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Acesse configuracoes e rotinas administrativas.")
        subtitle.setObjectName("mutedText")
        subtitle.setWordWrap(True)

        descriptions = {
            "financial": "Lancamentos, baixas e controle financeiro.",
            "notifications": "Fila de notificacoes por email, WhatsApp e sistema.",
            "sectors": "Setores e estrutura operacional.",
            "users": "Usuarios, perfis e redefinicao de senha.",
            "password_resets": "Solicitacoes de recuperacao de acesso.",
            "settings": "Identidade visual, empresa, tema e backup.",
            "reports": "Relatorios operacionais e exportacoes.",
            "audit_logs": "Rastreabilidade administrativa e operacional.",
        }

        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        for module_key in allowed_modules:
            button = QPushButton(self.module_labels[module_key])
            button.setObjectName("adminMenuButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(descriptions[module_key])
            button.clicked.connect(
                lambda checked=False, key=module_key: self._select_admin_module(dialog, key)
            )
            actions_layout.addWidget(button)

        close_button = QPushButton("Fechar")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(actions_layout)
        layout.addStretch()
        layout.addWidget(close_button)

        dialog.exec()

    def _select_admin_module(self, dialog: QDialog, module_key: str) -> None:
        dialog.accept()
        self.module_selected.emit(module_key)

    def _allowed_admin_modules(self) -> tuple[str, ...]:
        if self.current_user_role == "admin":
            return self.admin_module_keys
        if self.current_user_role == "manager":
            return ("financial", "notifications", "sectors", "users", "password_resets")
        return ()

    def render_loading(self, title: str, module_key: str) -> None:
        self._set_active_module(module_key)
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText(title)
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.empty_label.setText("Carregando dados...")
        self.empty_label.show()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def render_error(self, title: str, message: str, module_key: str) -> None:
        self._set_active_module(module_key)
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText(title)
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.empty_label.setText(message)
        self.empty_label.show()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def render_dashboard(self, summary: dict[str, Any] | None = None) -> None:
        self._set_active_module("dashboard")
        self.current_rows = []
        self.all_rows = []
        self.current_columns = []
        self.title_label.setText("Painel Principal")
        self.dashboard_section_title.setText("VISAO GERAL")
        self.empty_label.hide()
        self.table.hide()
        self._apply_dashboard_summary(summary or {})

    def render_rows(
        self,
        title: str,
        rows: list[dict[str, Any]],
        columns: list[tuple[str, str]],
        module_key: str,
    ) -> None:
        if module_key == "equipment":
            self._render_equipment_rows(title, rows)
            return

        self._set_active_module(module_key)
        self.all_rows = list(rows)
        self.current_columns = list(columns)
        self.data_title.setText(title)
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.module_search_input.setPlaceholderText(self._module_search_placeholder(module_key))
        self._populate_current_table(self._filtered_rows())

    def _populate_current_table(self, rows: list[dict[str, Any]]) -> None:
        columns = self.current_columns
        self.current_rows = rows
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for label, _key in columns])
        self.table.setRowCount(len(rows))

        if not rows:
            message = "Nenhum registro encontrado."
            if self.module_search_input.text().strip():
                message = "Nenhum registro encontrado para a busca."
            self.empty_label.setText(message)
            self.empty_label.show()
            return

        self.empty_label.hide()
        for row_index, row in enumerate(rows):
            for column_index, (_label, key) in enumerate(columns):
                value = self._format_value(row.get(key))
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)
            self.table.setRowHeight(row_index, 34)

        if self.active_module_key in self.searchable_module_keys:
            self.table.selectRow(0)

    def _apply_current_filter(self) -> None:
        if self.active_module_key not in self.searchable_module_keys:
            return
        self._populate_current_table(self._filtered_rows())

    def _filtered_rows(self) -> list[dict[str, Any]]:
        search_text = self.module_search_input.text().strip().lower()
        if not search_text:
            return list(self.all_rows)
        return [row for row in self.all_rows if self._row_matches_search(row, search_text)]

    def _row_matches_search(self, value: Any, search_text: str) -> bool:
        if isinstance(value, dict):
            return any(self._row_matches_search(child, search_text) for child in value.values())
        if isinstance(value, list):
            return any(self._row_matches_search(child, search_text) for child in value)
        return search_text in self._format_value(value).lower()

    def _module_search_placeholder(self, module_key: str) -> str:
        label = self.module_labels.get(module_key, "registros")
        return f"BUSCAR {label.upper()}..."

    def render_settings(self, settings: dict[str, Any]) -> None:
        self._set_active_module("settings")
        self.current_rows = []
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText("Configuracoes")
        self.data_description.setText(self.module_descriptions["settings"])
        self.empty_label.hide()
        self.table.hide()
        self._populate_settings_form(settings)

    def render_report(self, report: dict[str, Any]) -> None:
        self._set_active_module("reports")
        self.current_rows = report.get("rows") or []
        self.all_rows = list(self.current_rows)
        self.current_report_module_key = str(report.get("module") or self.current_report_module_key)
        self._select_combo_value(self.report_module_combo, self.current_report_module_key)
        self.data_title.setText(str(report.get("title") or "Relatorios"))
        self.data_description.setText(self.module_descriptions["reports"])
        self.report_summary_label.setText(f"Total de registros: {report.get('total_records', 0)}")
        self.report_full_summary.setPlainText(self._format_report_summary(report))
        self.empty_label.hide()
        self.table.show()

        columns = [
            (str(column.get("label")), str(column.get("key")))
            for column in report.get("columns", [])
        ]
        self.current_columns = columns
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for label, _key in columns])
        self.table.setRowCount(len(self.current_rows))
        for row_index, row in enumerate(self.current_rows):
            for column_index, (_label, key) in enumerate(columns):
                item = QTableWidgetItem(self._format_value(row.get(key)))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)

        if not self.current_rows:
            self.empty_label.setText("Nenhum registro encontrado.")
            self.empty_label.show()

    @staticmethod
    def _build_module_card(title: str, description: str) -> QFrame:
        card = QFrame()
        card.setObjectName("moduleCard")
        card.setMinimumHeight(88)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        description_label = QLabel(description)
        description_label.setObjectName("cardMeta")
        description_label.setWordWrap(True)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return card

    def _apply_dashboard_summary(self, summary: dict[str, Any]) -> None:
        greeting = str(summary.get("greeting") or "Painel operacional do PRO CORE.")
        self.dashboard_greeting_label.setText(greeting)
        self.dashboard_last_refresh_label.setText(str(summary.get("last_refresh") or ""))

        cards = summary.get("cards") or {}
        for key, card in self.dashboard_cards.items():
            card.set_value(cards.get(key, 0))

        self._clear_layout(self.dashboard_alerts_layout)
        alerts = summary.get("alerts") or []
        if not alerts:
            alerts = [{"message": "Nenhum alerta ativo. Tudo em ordem.", "level": "info"}]

        for alert in alerts:
            row = QFrame()
            row.setObjectName("dashboardAlertRow")
            row.setProperty("level", str(alert.get("level") or "info"))
            message = QLabel(str(alert.get("message") or "Alerta operacional."))
            message.setWordWrap(True)
            layout = QHBoxLayout(row)
            layout.setContentsMargins(10, 7, 10, 7)
            layout.addWidget(message)
            self.dashboard_alerts_layout.addWidget(row)

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _install_input_guards(self) -> None:
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QComboBox, QAbstractSpinBox)):
                widget.installEventFilter(self)

    def _mark_active_nav(self, module_key: str) -> None:
        for key, button in self.module_buttons.items():
            is_active = key == module_key
            button.setChecked(is_active)
            button.setProperty("active", "true" if is_active else "false")
            button.style().unpolish(button)
            button.style().polish(button)

        admin_active = module_key in self.admin_module_keys
        self.admin_menu_button.setProperty("active", "true" if admin_active else "false")
        self.admin_menu_button.style().unpolish(self.admin_menu_button)
        self.admin_menu_button.style().polish(self.admin_menu_button)

    def _build_customer_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Cliente")
        title.setObjectName("sectionTitle")

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Nome")

        self.customer_email_input = QLineEdit()
        self.customer_email_input.setPlaceholderText("Email")

        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText("(11) 99999-9999")
        self.customer_phone_input.setInputMask("(00) 00000-0000;_")

        self.customer_address_input = QLineEdit()
        self.customer_address_input.setPlaceholderText("Endereco")

        self.customer_notes_input = QLineEdit()
        self.customer_notes_input.setPlaceholderText("Observacoes")

        self.customer_active_checkbox = QCheckBox("Cliente ativo")
        self.customer_active_checkbox.setChecked(True)

        identity_title = QLabel("DADOS DO CLIENTE")
        identity_title.setObjectName("formGroupTitle")
        identity_form_layout = QFormLayout()
        identity_form_layout.setSpacing(10)
        identity_form_layout.addRow("Nome", self.customer_name_input)
        identity_form_layout.addRow("Email", self.customer_email_input)
        identity_form_layout.addRow("Telefone", self.customer_phone_input)
        identity_form_layout.addRow("", self.customer_active_checkbox)

        identity_panel = QFrame()
        identity_panel.setObjectName("formSubPanel")
        identity_layout = QVBoxLayout(identity_panel)
        identity_layout.setContentsMargins(12, 12, 12, 12)
        identity_layout.setSpacing(8)
        identity_layout.addWidget(identity_title)
        identity_layout.addLayout(identity_form_layout)

        contact_title = QLabel("ENDERECO E OBSERVACOES")
        contact_title.setObjectName("formGroupTitle")
        contact_form_layout = QFormLayout()
        contact_form_layout.setSpacing(10)
        contact_form_layout.addRow("Endereco", self.customer_address_input)
        contact_form_layout.addRow("Observacoes", self.customer_notes_input)

        contact_panel = QFrame()
        contact_panel.setObjectName("formSubPanel")
        contact_layout = QVBoxLayout(contact_panel)
        contact_layout.setContentsMargins(12, 12, 12, 12)
        contact_layout.setSpacing(8)
        contact_layout.addWidget(contact_title)
        contact_layout.addLayout(contact_form_layout)

        fields_layout = QGridLayout()
        fields_layout.setSpacing(12)
        fields_layout.addWidget(identity_panel, 0, 0)
        fields_layout.addWidget(contact_panel, 0, 1)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        self.customer_form_status = QLabel("")
        self.customer_form_status.setObjectName("mutedText")

        self.customer_new_button = QPushButton("Novo")
        self.customer_new_button.setObjectName("secondaryButton")
        self.customer_new_button.clicked.connect(self.clear_customer_form)

        self.customer_save_button = QPushButton("Salvar cliente")
        self.customer_save_button.clicked.connect(self._request_customer_save)

        self.customer_document_path_input = QLineEdit()
        self.customer_document_path_input.setPlaceholderText("Anexo do cliente")
        self.customer_document_path_input.setReadOnly(True)

        self.customer_select_document_button = QPushButton("Selecionar anexo")
        self.customer_select_document_button.setObjectName("secondaryButton")
        self.customer_select_document_button.clicked.connect(self._select_customer_document)

        self.customer_upload_document_button = QPushButton("Enviar anexo")
        self.customer_upload_document_button.clicked.connect(self._request_customer_document_upload)

        details_title = QLabel("DADOS COMPLETOS")
        details_title.setObjectName("formGroupTitle")

        self.customer_full_summary = create_summary_text()

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.customer_new_button)
        actions.addWidget(self.customer_save_button)

        document_actions = QHBoxLayout()
        document_actions.addWidget(self.customer_document_path_input, 1)
        document_actions.addWidget(self.customer_select_document_button)
        document_actions.addWidget(self.customer_upload_document_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(fields_layout)
        layout.addWidget(details_title)
        layout.addWidget(self.customer_full_summary)
        layout.addLayout(document_actions)
        layout.addWidget(self.customer_form_status)
        layout.addLayout(actions)

        return panel

    def _build_equipment_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EQUIPAMENTOS")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Gestao hierarquica de ativos, objetos e componentes")
        subtitle.setObjectName("mutedText")

        self.equipment_search_input = QLineEdit()
        self.equipment_search_input.setObjectName("sectionSearch")
        self.equipment_search_input.setPlaceholderText("BUSCAR EQUIPAMENTOS...")
        self.equipment_search_input.textChanged.connect(self._refresh_equipment_table)
        self.equipment_table = QTableWidget()
        self._configure_equipment_table(
            self.equipment_table,
            ["ID", "TIPO", "MARCA", "MODELO", "NO ESPECIAL"],
            210,
        )
        self.equipment_table.itemSelectionChanged.connect(self._handle_equipment_table_selection)
        self.equipment_full_summary = create_summary_text(150, 220)
        self.equipment_full_summary.setPlainText(
            "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
        )

        self.equipment_new_button = QPushButton("+Equipamento")
        self.equipment_new_button.clicked.connect(self._open_equipment_create_dialog)
        self.equipment_edit_button = QPushButton("Editar")
        self.equipment_edit_button.setObjectName("secondaryButton")
        self.equipment_edit_button.clicked.connect(self._open_equipment_edit_dialog)
        self.equipment_remove_button = QPushButton("Remover")
        self.equipment_remove_button.setObjectName("dangerButton")
        self.equipment_remove_button.clicked.connect(self._request_equipment_delete)

        self.equipment_context_label = QLabel("_SELECIONE UM EQUIPAMENTO_")
        self.equipment_context_label.setObjectName("mutedText")
        self.board_search_input = QLineEdit()
        self.board_search_input.setObjectName("sectionSearch")
        self.board_search_input.setPlaceholderText("BUSCAR OBJETO VINCULADO...")
        self.board_search_input.textChanged.connect(self._refresh_equipment_boards_table)
        self.equipment_boards_table = QTableWidget()
        self._configure_equipment_table(
            self.equipment_boards_table,
            ["ID", "NOME", "NO ESPECIAL", "MODELO", "REVISAO"],
            190,
        )
        self.equipment_boards_table.itemSelectionChanged.connect(
            self._handle_equipment_board_table_selection
        )
        self.board_full_summary = create_summary_text(150, 220)
        self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
        self.board_add_button = QPushButton("+Objeto Vinculado")
        self.board_add_button.clicked.connect(self._request_equipment_board_create)
        self.board_edit_button = QPushButton("Editar")
        self.board_edit_button.setObjectName("secondaryButton")
        self.board_edit_button.clicked.connect(self._open_equipment_board_edit_dialog)
        self.board_remove_button = QPushButton("Remover")
        self.board_remove_button.setObjectName("dangerButton")
        self.board_remove_button.clicked.connect(self._request_equipment_board_delete)

        self.board_context_label = QLabel("_SELECIONE UM OBJETO VINCULADO_")
        self.board_context_label.setObjectName("mutedText")
        self.component_search_input = QLineEdit()
        self.component_search_input.setObjectName("sectionSearch")
        self.component_search_input.setPlaceholderText("BUSCAR COMPONENTE...")
        self.component_search_input.textChanged.connect(self._refresh_equipment_components_table)
        self.equipment_components_table = QTableWidget()
        self._configure_equipment_table(
            self.equipment_components_table,
            ["ID", "CATEGORIA", "DADOS", "MODELO/PART NUMBER", "LOCALIZACAO", "OBSERVACOES"],
            190,
        )
        self.equipment_components_table.itemSelectionChanged.connect(
            self._handle_equipment_component_table_selection
        )
        self.component_full_summary = create_summary_text(150, 220)
        self.component_full_summary.setPlainText(
            "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
        )
        self.component_add_button = QPushButton("+Componente")
        self.component_add_button.clicked.connect(self._request_equipment_component_create)
        self.component_edit_button = QPushButton("Editar")
        self.component_edit_button.setObjectName("secondaryButton")
        self.component_edit_button.clicked.connect(self._open_equipment_component_edit_dialog)
        self.component_remove_button = QPushButton("Remover")
        self.component_remove_button.setObjectName("dangerButton")
        self.component_remove_button.clicked.connect(self._request_equipment_component_delete)

        self.equipment_form_status = QLabel("")
        self.equipment_form_status.setObjectName("mutedText")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(
            self._build_equipment_section(
                "EQUIPAMENTOS",
                self.equipment_search_input,
                self.equipment_table,
                self.equipment_full_summary,
                [
                    self.equipment_new_button,
                    self.equipment_edit_button,
                    self.equipment_remove_button,
                ],
            )
        )
        layout.addWidget(self.equipment_context_label)
        layout.addWidget(
            self._build_equipment_section(
                "OBJETOS VINCULADOS",
                self.board_search_input,
                self.equipment_boards_table,
                self.board_full_summary,
                [
                    self.board_add_button,
                    self.board_edit_button,
                    self.board_remove_button,
                ],
            )
        )
        layout.addWidget(self.board_context_label)
        layout.addWidget(
            self._build_equipment_section(
                "COMPONENTES VINCULADOS",
                self.component_search_input,
                self.equipment_components_table,
                self.component_full_summary,
                [
                    self.component_add_button,
                    self.component_edit_button,
                    self.component_remove_button,
                ],
            )
        )
        layout.addWidget(self.equipment_form_status)

        return panel

    def _build_equipment_section(
        self,
        title: str,
        search_input: QLineEdit,
        table: QTableWidget,
        summary: QTextEdit,
        buttons: list[QPushButton],
    ) -> QFrame:
        section = QFrame()
        section.setObjectName("equipmentSection")

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        details_title = QLabel("DADOS COMPLETOS:")
        details_title.setObjectName("formGroupTitle")

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(6)
        table_layout.addWidget(search_input)
        table_layout.addWidget(table)

        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(6)
        details_layout.addWidget(details_title)
        details_layout.addWidget(summary)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.addLayout(table_layout, 0, 0)
        grid_layout.addLayout(details_layout, 0, 1)
        grid_layout.setColumnStretch(0, 3)
        grid_layout.setColumnStretch(1, 2)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        for button in buttons:
            actions.addWidget(button)
        actions.addStretch()

        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(title_label)
        layout.addLayout(grid_layout)
        layout.addLayout(actions)
        return section

    def _configure_equipment_table(
        self,
        table: QTableWidget,
        columns: list[str],
        minimum_height: int,
    ) -> None:
        table.setObjectName("dataTable")
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setMinimumHeight(minimum_height)

    def _build_inventory_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Estoque")
        title.setObjectName("sectionTitle")

        self.inventory_sku_input = QLineEdit()
        self.inventory_sku_input.setPlaceholderText("SKU")

        self.inventory_name_input = QLineEdit()
        self.inventory_name_input.setPlaceholderText("Nome")

        self.inventory_category_input = QLineEdit()
        self.inventory_category_input.setPlaceholderText("Categoria")

        self.inventory_quantity_input = QLineEdit()
        self.inventory_quantity_input.setPlaceholderText("Quantidade")

        self.inventory_minimum_quantity_input = QLineEdit()
        self.inventory_minimum_quantity_input.setPlaceholderText("Quantidade minima")

        self.inventory_unit_cost_input = QLineEdit()
        self.inventory_unit_cost_input.setPlaceholderText("Custo unitario")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("SKU", self.inventory_sku_input)
        form_layout.addRow("Nome", self.inventory_name_input)
        form_layout.addRow("Categoria", self.inventory_category_input)
        form_layout.addRow("Quantidade", self.inventory_quantity_input)
        form_layout.addRow("Minimo", self.inventory_minimum_quantity_input)
        form_layout.addRow("Custo", self.inventory_unit_cost_input)

        inventory_fields_title = QLabel("DADOS DO ITEM")
        inventory_fields_title.setObjectName("formGroupTitle")
        inventory_fields_panel = QFrame()
        inventory_fields_panel.setObjectName("formSubPanel")
        inventory_fields_panel_layout = QVBoxLayout(inventory_fields_panel)
        inventory_fields_panel_layout.setContentsMargins(12, 12, 12, 12)
        inventory_fields_panel_layout.setSpacing(8)
        inventory_fields_panel_layout.addWidget(inventory_fields_title)
        inventory_fields_panel_layout.addLayout(form_layout)

        self.inventory_stock_status = QLabel("Status: novo item.")
        self.inventory_stock_status.setObjectName("statusBanner")
        self.inventory_stock_status.setProperty("level", "info")
        self.inventory_stock_status.setWordWrap(True)

        inventory_details_title = QLabel("DADOS COMPLETOS")
        inventory_details_title.setObjectName("formGroupTitle")
        self.inventory_full_summary = create_summary_text()

        self.inventory_form_status = QLabel("")
        self.inventory_form_status.setObjectName("mutedText")

        self.inventory_new_button = QPushButton("Novo")
        self.inventory_new_button.setObjectName("secondaryButton")
        self.inventory_new_button.clicked.connect(self.clear_inventory_form)

        self.inventory_save_button = QPushButton("Salvar item")
        self.inventory_save_button.clicked.connect(self._request_inventory_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.inventory_new_button)
        actions.addWidget(self.inventory_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(inventory_fields_panel)
        layout.addWidget(self.inventory_stock_status)
        layout.addWidget(inventory_details_title)
        layout.addWidget(self.inventory_full_summary)
        layout.addWidget(self.inventory_form_status)
        layout.addLayout(actions)

        return panel

    def _build_service_order_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Ordem de Servico")
        title.setObjectName("sectionTitle")

        self.service_order_workflow_hint = QLabel(
            "TRIAGEM -> DIAGNOSTICO -> ORCAMENTO -> APROVACAO -> EXECUCAO -> CONCLUSAO"
        )
        self.service_order_workflow_hint.setObjectName("mutedText")

        workflow_panel = QFrame()
        workflow_panel.setObjectName("workflowPanel")
        workflow_layout = QHBoxLayout(workflow_panel)
        workflow_layout.setContentsMargins(10, 10, 10, 10)
        workflow_layout.setSpacing(8)
        self.service_order_workflow_steps: list[QLabel] = []
        for label in ["Triagem", "Diagnostico", "Orcamento", "Aprovacao", "Execucao", "Conclusao"]:
            step_label = QLabel(label)
            step_label.setObjectName("workflowStep")
            step_label.setProperty("stage", "future")
            step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.service_order_workflow_steps.append(step_label)
            workflow_layout.addWidget(step_label)

        self.service_order_customer_combo = QComboBox()
        self.service_order_customer_combo.currentIndexChanged.connect(
            self._refresh_service_order_equipment_combo
        )

        self.service_order_equipment_combo = QComboBox()
        self.service_order_technician_combo = QComboBox()

        self.service_order_priority_combo = QComboBox()
        self.service_order_priority_combo.addItem("Baixa", "low")
        self.service_order_priority_combo.addItem("Normal", "normal")
        self.service_order_priority_combo.addItem("Alta", "high")
        self.service_order_priority_combo.addItem("Urgente", "urgent")

        self.service_order_sla_input = QLineEdit()
        self.service_order_sla_input.setPlaceholderText("AAAA-MM-DDTHH:MM:SS")

        self.service_order_problem_input = QLineEdit()
        self.service_order_problem_input.setPlaceholderText("Problema informado")

        self.service_order_diagnosis_input = QLineEdit()
        self.service_order_diagnosis_input.setPlaceholderText("Diagnostico tecnico")

        self.service_order_rejection_input = QLineEdit()
        self.service_order_rejection_input.setPlaceholderText("Motivo de reprovacao/observacao")

        self.service_order_budget_type_combo = QComboBox()
        self.service_order_budget_type_combo.addItem("Servico", "service")
        self.service_order_budget_type_combo.addItem("Peca", "part")
        self.service_order_budget_type_combo.addItem("Outro", "other")

        self.service_order_budget_description_input = QLineEdit()
        self.service_order_budget_description_input.setPlaceholderText("Descricao do item")

        self.service_order_budget_quantity_input = QLineEdit()
        self.service_order_budget_quantity_input.setPlaceholderText("Quantidade")
        self.service_order_budget_quantity_input.setText("1")

        self.service_order_budget_unit_price_input = QLineEdit()
        self.service_order_budget_unit_price_input.setPlaceholderText("Valor unitario")
        self.service_order_budget_unit_price_input.setText("0")

        self.service_order_document_type_combo = QComboBox()
        self.service_order_document_type_combo.addItem("Imagem", "image")
        self.service_order_document_type_combo.addItem("Video", "video")
        self.service_order_document_type_combo.addItem("PDF", "pdf")
        self.service_order_document_type_combo.addItem("Nota fiscal", "invoice")
        self.service_order_document_type_combo.addItem("Outro", "other")

        self.service_order_document_path_input = QLineEdit()
        self.service_order_document_path_input.setPlaceholderText("Arquivo selecionado")
        self.service_order_document_path_input.setReadOnly(True)

        record_fields_title = QLabel("DADOS DA OS")
        record_fields_title.setObjectName("formGroupTitle")
        record_form_layout = QFormLayout()
        record_form_layout.setSpacing(10)
        record_form_layout.addRow("Cliente", self.service_order_customer_combo)
        record_form_layout.addRow("Equipamento", self.service_order_equipment_combo)
        record_form_layout.addRow("Tecnico", self.service_order_technician_combo)
        record_form_layout.addRow("Prioridade", self.service_order_priority_combo)
        record_form_layout.addRow("Prazo SLA", self.service_order_sla_input)
        record_form_layout.addRow("Problema", self.service_order_problem_input)

        record_fields = QFrame()
        record_fields.setObjectName("formSubPanel")
        record_fields_layout = QVBoxLayout(record_fields)
        record_fields_layout.setContentsMargins(12, 12, 12, 12)
        record_fields_layout.setSpacing(8)
        record_fields_layout.addWidget(record_fields_title)
        record_fields_layout.addLayout(record_form_layout)

        technical_fields_title = QLabel("FLUXO TECNICO")
        technical_fields_title.setObjectName("formGroupTitle")
        technical_form_layout = QFormLayout()
        technical_form_layout.setSpacing(10)
        technical_form_layout.addRow("Diagnostico", self.service_order_diagnosis_input)
        technical_form_layout.addRow("Observacao", self.service_order_rejection_input)
        technical_form_layout.addRow("Tipo do item", self.service_order_budget_type_combo)
        technical_form_layout.addRow("Item", self.service_order_budget_description_input)
        technical_form_layout.addRow("Quantidade", self.service_order_budget_quantity_input)
        technical_form_layout.addRow("Valor unitario", self.service_order_budget_unit_price_input)
        technical_form_layout.addRow("Tipo do anexo", self.service_order_document_type_combo)
        technical_form_layout.addRow("Arquivo", self.service_order_document_path_input)

        technical_fields = QFrame()
        technical_fields.setObjectName("formSubPanel")
        technical_fields_layout = QVBoxLayout(technical_fields)
        technical_fields_layout.setContentsMargins(12, 12, 12, 12)
        technical_fields_layout.setSpacing(8)
        technical_fields_layout.addWidget(technical_fields_title)
        technical_fields_layout.addLayout(technical_form_layout)

        fields_layout = QGridLayout()
        fields_layout.setSpacing(12)
        fields_layout.addWidget(record_fields, 0, 0)
        fields_layout.addWidget(technical_fields, 0, 1)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        self.service_order_form_status = QLabel("")
        self.service_order_form_status.setObjectName("mutedText")

        self.service_order_current_status = QLabel("Status: -")
        self.service_order_current_status.setObjectName("mutedText")

        self.service_order_budget_summary = QLabel("Orcamento: nenhum item.")
        self.service_order_budget_summary.setObjectName("mutedText")
        self.service_order_budget_summary.setWordWrap(True)

        self.service_order_documents_summary = QLabel("Anexos: nenhum arquivo.")
        self.service_order_documents_summary.setObjectName("mutedText")
        self.service_order_documents_summary.setWordWrap(True)

        details_title = QLabel("DADOS COMPLETOS")
        details_title.setObjectName("formGroupTitle")

        self.service_order_full_summary = create_summary_text(96, 130)

        self.service_order_new_button = QPushButton("Nova")
        self.service_order_new_button.setObjectName("secondaryButton")
        self.service_order_new_button.clicked.connect(self.clear_service_order_form)

        self.service_order_save_button = QPushButton("Salvar OS")
        self.service_order_save_button.clicked.connect(self._request_service_order_save)

        self.service_order_diagnosis_button = QPushButton("Registrar diagnostico")
        self.service_order_diagnosis_button.setObjectName("secondaryButton")
        self.service_order_diagnosis_button.clicked.connect(self._request_service_order_diagnosis)

        self.service_order_add_budget_button = QPushButton("Adicionar item")
        self.service_order_add_budget_button.setObjectName("secondaryButton")
        self.service_order_add_budget_button.clicked.connect(
            self._request_service_order_budget_item
        )

        self.service_order_submit_quote_button = QPushButton("Enviar orcamento")
        self.service_order_submit_quote_button.setObjectName("secondaryButton")
        self.service_order_submit_quote_button.clicked.connect(
            self._request_service_order_submit_quote
        )

        self.service_order_approve_button = QPushButton("Aprovar")
        self.service_order_approve_button.setObjectName("secondaryButton")
        self.service_order_approve_button.clicked.connect(self._request_service_order_approve)

        self.service_order_reject_button = QPushButton("Reprovar")
        self.service_order_reject_button.setObjectName("secondaryButton")
        self.service_order_reject_button.clicked.connect(self._request_service_order_reject)

        self.service_order_start_button = QPushButton("Iniciar")
        self.service_order_start_button.setObjectName("secondaryButton")
        self.service_order_start_button.clicked.connect(self._request_service_order_start)

        self.service_order_complete_button = QPushButton("Concluir")
        self.service_order_complete_button.setObjectName("secondaryButton")
        self.service_order_complete_button.clicked.connect(self._request_service_order_complete)

        self.service_order_select_document_button = QPushButton("Selecionar anexo")
        self.service_order_select_document_button.setObjectName("secondaryButton")
        self.service_order_select_document_button.clicked.connect(
            self._select_service_order_document
        )

        self.service_order_upload_document_button = QPushButton("Enviar anexo")
        self.service_order_upload_document_button.setObjectName("secondaryButton")
        self.service_order_upload_document_button.clicked.connect(
            self._request_service_order_document_upload
        )

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.service_order_new_button)
        actions.addWidget(self.service_order_save_button)

        flow_actions = QHBoxLayout()
        flow_actions.addStretch()
        flow_actions.addWidget(self.service_order_diagnosis_button)
        flow_actions.addWidget(self.service_order_add_budget_button)
        flow_actions.addWidget(self.service_order_submit_quote_button)
        flow_actions.addWidget(self.service_order_approve_button)
        flow_actions.addWidget(self.service_order_reject_button)
        flow_actions.addWidget(self.service_order_start_button)
        flow_actions.addWidget(self.service_order_complete_button)

        document_actions = QHBoxLayout()
        document_actions.addStretch()
        document_actions.addWidget(self.service_order_select_document_button)
        document_actions.addWidget(self.service_order_upload_document_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(self.service_order_workflow_hint)
        layout.addWidget(workflow_panel)
        layout.addLayout(fields_layout)
        layout.addWidget(self.service_order_current_status)
        layout.addWidget(details_title)
        layout.addWidget(self.service_order_full_summary)
        layout.addWidget(self.service_order_budget_summary)
        layout.addWidget(self.service_order_documents_summary)
        layout.addWidget(self.service_order_form_status)
        layout.addLayout(actions)
        layout.addLayout(flow_actions)
        layout.addLayout(document_actions)

        return panel

    def _build_sector_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Setor")
        title.setObjectName("sectionTitle")

        self.sector_name_input = QLineEdit()
        self.sector_name_input.setPlaceholderText("Nome do setor")

        self.sector_description_input = QLineEdit()
        self.sector_description_input.setPlaceholderText("Descricao")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Nome", self.sector_name_input)
        form_layout.addRow("Descricao", self.sector_description_input)

        sector_fields_panel = QFrame()
        sector_fields_panel.setObjectName("formSubPanel")
        sector_fields_panel_layout = QVBoxLayout(sector_fields_panel)
        sector_fields_panel_layout.setContentsMargins(12, 12, 12, 12)
        sector_fields_panel_layout.setSpacing(8)
        sector_fields_title = QLabel("DADOS DO SETOR")
        sector_fields_title.setObjectName("formGroupTitle")
        sector_fields_panel_layout.addWidget(sector_fields_title)
        sector_fields_panel_layout.addLayout(form_layout)

        sector_details_title = QLabel("DADOS COMPLETOS")
        sector_details_title.setObjectName("formGroupTitle")
        self.sector_full_summary = create_summary_text(78, 110)

        self.sector_form_status = QLabel("")
        self.sector_form_status.setObjectName("mutedText")

        self.sector_new_button = QPushButton("Novo")
        self.sector_new_button.setObjectName("secondaryButton")
        self.sector_new_button.clicked.connect(self.clear_sector_form)

        self.sector_save_button = QPushButton("Salvar setor")
        self.sector_save_button.clicked.connect(self._request_sector_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.sector_new_button)
        actions.addWidget(self.sector_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(sector_fields_panel)
        layout.addWidget(sector_details_title)
        layout.addWidget(self.sector_full_summary)
        layout.addWidget(self.sector_form_status)
        layout.addLayout(actions)

        return panel

    def _build_user_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Usuario")
        title.setObjectName("sectionTitle")

        self.user_full_name_input = QLineEdit()
        self.user_full_name_input.setPlaceholderText("Nome completo")

        self.user_email_input = QLineEdit()
        self.user_email_input.setPlaceholderText("Email de login")

        self.user_role_combo = QComboBox()
        self.user_role_combo.addItem("Administrador", "admin")
        self.user_role_combo.addItem("Gestor/Lider", "manager")
        self.user_role_combo.addItem("Tecnico", "technician")
        self.user_role_combo.addItem("Cliente", "customer")

        self.user_sector_combo = QComboBox()

        self.user_initial_password_input = QLineEdit()
        self.user_initial_password_input.setPlaceholderText("Senha inicial")
        self.user_initial_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.user_active_checkbox = QCheckBox("Usuario ativo")
        self.user_active_checkbox.setChecked(True)

        self.user_reset_password_input = QLineEdit()
        self.user_reset_password_input.setPlaceholderText("Nova senha")
        self.user_reset_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        identity_layout = QFormLayout()
        identity_layout.setSpacing(10)
        identity_layout.addRow("Nome", self.user_full_name_input)
        identity_layout.addRow("Email", self.user_email_input)
        identity_layout.addRow("Perfil", self.user_role_combo)
        identity_layout.addRow("Setor", self.user_sector_combo)
        identity_layout.addRow("", self.user_active_checkbox)

        identity_panel = QFrame()
        identity_panel.setObjectName("formSubPanel")
        identity_panel_layout = QVBoxLayout(identity_panel)
        identity_panel_layout.setContentsMargins(12, 12, 12, 12)
        identity_panel_layout.setSpacing(8)
        identity_title = QLabel("CONTA E ACESSO")
        identity_title.setObjectName("formGroupTitle")
        identity_panel_layout.addWidget(identity_title)
        identity_panel_layout.addLayout(identity_layout)

        security_layout = QFormLayout()
        security_layout.setSpacing(10)
        security_layout.addRow("Senha inicial", self.user_initial_password_input)
        security_layout.addRow("Redefinir senha", self.user_reset_password_input)

        security_panel = QFrame()
        security_panel.setObjectName("formSubPanel")
        security_panel_layout = QVBoxLayout(security_panel)
        security_panel_layout.setContentsMargins(12, 12, 12, 12)
        security_panel_layout.setSpacing(8)
        security_title = QLabel("SEGURANCA")
        security_title.setObjectName("formGroupTitle")
        security_panel_layout.addWidget(security_title)
        security_panel_layout.addLayout(security_layout)

        fields_layout = QGridLayout()
        fields_layout.setSpacing(12)
        fields_layout.addWidget(identity_panel, 0, 0)
        fields_layout.addWidget(security_panel, 0, 1)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        user_details_title = QLabel("DADOS COMPLETOS")
        user_details_title.setObjectName("formGroupTitle")
        self.user_full_summary = create_summary_text()

        self.user_form_status = QLabel("")
        self.user_form_status.setObjectName("mutedText")

        self.user_new_button = QPushButton("Novo")
        self.user_new_button.setObjectName("secondaryButton")
        self.user_new_button.clicked.connect(self.clear_user_form)

        self.user_reset_password_button = QPushButton("Redefinir senha")
        self.user_reset_password_button.setObjectName("secondaryButton")
        self.user_reset_password_button.clicked.connect(self._request_user_password_reset)

        self.user_save_button = QPushButton("Salvar usuario")
        self.user_save_button.clicked.connect(self._request_user_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.user_new_button)
        actions.addWidget(self.user_reset_password_button)
        actions.addWidget(self.user_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(fields_layout)
        layout.addWidget(user_details_title)
        layout.addWidget(self.user_full_summary)
        layout.addWidget(self.user_form_status)
        layout.addLayout(actions)

        return panel

    def _build_password_reset_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("SOLICITACOES DE REDEFINICAO DE SENHA")
        title.setObjectName("sectionTitle")

        self.password_reset_requester_label = QLabel("Selecione uma solicitacao.")
        self.password_reset_requester_label.setObjectName("mutedText")
        self.password_reset_requester_label.setWordWrap(True)

        self.password_reset_new_password_input = QLineEdit()
        self.password_reset_new_password_input.setPlaceholderText("Nova senha temporaria")
        self.password_reset_new_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Nova senha", self.password_reset_new_password_input)

        password_reset_panel = QFrame()
        password_reset_panel.setObjectName("formSubPanel")
        password_reset_panel_layout = QVBoxLayout(password_reset_panel)
        password_reset_panel_layout.setContentsMargins(12, 12, 12, 12)
        password_reset_panel_layout.setSpacing(8)
        password_reset_title = QLabel("ATENDIMENTO DA SOLICITACAO")
        password_reset_title.setObjectName("formGroupTitle")
        password_reset_panel_layout.addWidget(password_reset_title)
        password_reset_panel_layout.addWidget(self.password_reset_requester_label)
        password_reset_panel_layout.addLayout(form_layout)

        password_reset_details_title = QLabel("DADOS COMPLETOS")
        password_reset_details_title.setObjectName("formGroupTitle")
        self.password_reset_full_summary = create_summary_text(78, 110)

        self.password_reset_form_status = QLabel("")
        self.password_reset_form_status.setObjectName("mutedText")

        self.password_reset_resolve_button = QPushButton("Redefinir senha")
        self.password_reset_resolve_button.clicked.connect(self._request_password_reset_resolve)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.password_reset_resolve_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(password_reset_panel)
        layout.addWidget(password_reset_details_title)
        layout.addWidget(self.password_reset_full_summary)
        layout.addWidget(self.password_reset_form_status)
        layout.addLayout(actions)

        return panel

    def _build_settings_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("CONFIGURACOES DO SISTEMA")
        title.setObjectName("sectionTitle")

        self.settings_company_name_input = QLineEdit()
        self.settings_company_name_input.setPlaceholderText("Razao social")

        self.settings_trade_name_input = QLineEdit()
        self.settings_trade_name_input.setPlaceholderText("Nome fantasia")

        self.settings_document_input = QLineEdit()
        self.settings_document_input.setPlaceholderText("Documento")

        self.settings_email_input = QLineEdit()
        self.settings_email_input.setPlaceholderText("Email")

        self.settings_phone_input = QLineEdit()
        self.settings_phone_input.setPlaceholderText("Telefone")

        self.settings_brand_name_input = QLineEdit()
        self.settings_brand_name_input.setPlaceholderText("Nome exibido no sistema")

        self.settings_brand_subtitle_input = QLineEdit()
        self.settings_brand_subtitle_input.setPlaceholderText("Subtitulo da empresa")

        self.settings_primary_color_input = QLineEdit()
        self.settings_primary_color_input.setPlaceholderText("#0969da")

        self.settings_theme_combo = QComboBox()
        self.settings_theme_combo.addItem("Claro", "light")
        self.settings_theme_combo.addItem("Escuro", "dark")

        self.settings_backup_enabled_checkbox = QCheckBox("Backup automatico ativo")
        self.settings_backup_enabled_checkbox.setChecked(True)

        self.settings_backup_interval_input = QLineEdit()
        self.settings_backup_interval_input.setPlaceholderText("Intervalo em horas")

        self.settings_backup_path_input = QLineEdit()
        self.settings_backup_path_input.setPlaceholderText("Pasta de backup")

        self.settings_backup_last_run_label = QLabel("Ultimo backup: nunca")
        self.settings_backup_last_run_label.setObjectName("mutedText")

        company_layout = QFormLayout()
        company_layout.setSpacing(10)
        company_layout.addRow("Empresa", self.settings_company_name_input)
        company_layout.addRow("Nome fantasia", self.settings_trade_name_input)
        company_layout.addRow("Documento", self.settings_document_input)
        company_layout.addRow("Email", self.settings_email_input)
        company_layout.addRow("Telefone", self.settings_phone_input)

        company_panel = QFrame()
        company_panel.setObjectName("formSubPanel")
        company_panel_layout = QVBoxLayout(company_panel)
        company_panel_layout.setContentsMargins(12, 12, 12, 12)
        company_panel_layout.setSpacing(8)
        company_title = QLabel("DADOS DA EMPRESA")
        company_title.setObjectName("formGroupTitle")
        company_panel_layout.addWidget(company_title)
        company_panel_layout.addLayout(company_layout)

        branding_layout = QFormLayout()
        branding_layout.setSpacing(10)
        branding_layout.addRow("Nome exibido", self.settings_brand_name_input)
        branding_layout.addRow("Subtitulo", self.settings_brand_subtitle_input)
        branding_layout.addRow("Cor principal", self.settings_primary_color_input)

        branding_panel = QFrame()
        branding_panel.setObjectName("formSubPanel")
        branding_panel_layout = QVBoxLayout(branding_panel)
        branding_panel_layout.setContentsMargins(12, 12, 12, 12)
        branding_panel_layout.setSpacing(8)
        branding_title = QLabel("IDENTIDADE VISUAL")
        branding_title.setObjectName("formGroupTitle")
        branding_panel_layout.addWidget(branding_title)
        branding_panel_layout.addLayout(branding_layout)

        operation_layout = QFormLayout()
        operation_layout.setSpacing(10)
        operation_layout.addRow("Tema", self.settings_theme_combo)
        operation_layout.addRow("", self.settings_backup_enabled_checkbox)
        operation_layout.addRow("Intervalo", self.settings_backup_interval_input)
        operation_layout.addRow("Destino", self.settings_backup_path_input)

        operation_panel = QFrame()
        operation_panel.setObjectName("formSubPanel")
        operation_panel_layout = QVBoxLayout(operation_panel)
        operation_panel_layout.setContentsMargins(12, 12, 12, 12)
        operation_panel_layout.setSpacing(8)
        operation_title = QLabel("TEMA E BACKUP")
        operation_title.setObjectName("formGroupTitle")
        operation_panel_layout.addWidget(operation_title)
        operation_panel_layout.addLayout(operation_layout)

        fields_layout = QGridLayout()
        fields_layout.setSpacing(12)
        fields_layout.addWidget(company_panel, 0, 0)
        fields_layout.addWidget(branding_panel, 0, 1)
        fields_layout.addWidget(operation_panel, 1, 0, 1, 2)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        settings_details_title = QLabel("RESUMO OPERACIONAL")
        settings_details_title.setObjectName("formGroupTitle")
        self.settings_full_summary = create_summary_text()

        self.settings_form_status = QLabel("")
        self.settings_form_status.setObjectName("mutedText")

        self.settings_save_button = QPushButton("Salvar configuracoes")
        self.settings_save_button.clicked.connect(self._request_settings_save)

        self.settings_run_backup_button = QPushButton("Executar backup agora")
        self.settings_run_backup_button.setObjectName("secondaryButton")
        self.settings_run_backup_button.clicked.connect(self.backup_run_requested.emit)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.settings_run_backup_button)
        actions.addWidget(self.settings_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(fields_layout)
        layout.addWidget(settings_details_title)
        layout.addWidget(self.settings_full_summary)
        layout.addWidget(self.settings_backup_last_run_label)
        layout.addWidget(self.settings_form_status)
        layout.addLayout(actions)

        return panel

    def _build_report_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("RELATORIOS E EXPORTACOES")
        title.setObjectName("sectionTitle")

        self.report_module_combo = QComboBox()
        self.report_module_combo.addItem("Ordens de Servico", "service_orders")
        self.report_module_combo.addItem("Clientes", "customers")
        self.report_module_combo.addItem("Equipamentos", "equipment")
        self.report_module_combo.addItem("Estoque", "inventory")
        self.report_module_combo.addItem("Usuarios", "users")
        self.report_module_combo.addItem("Financeiro", "financial")
        self.report_module_combo.addItem("Logs/Auditoria", "audit_logs")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Modulo", self.report_module_combo)

        report_filter_panel = QFrame()
        report_filter_panel.setObjectName("formSubPanel")
        report_filter_panel_layout = QVBoxLayout(report_filter_panel)
        report_filter_panel_layout.setContentsMargins(12, 12, 12, 12)
        report_filter_panel_layout.setSpacing(8)
        report_filter_title = QLabel("FILTRO DO RELATORIO")
        report_filter_title.setObjectName("formGroupTitle")
        report_filter_panel_layout.addWidget(report_filter_title)
        report_filter_panel_layout.addLayout(form_layout)

        self.report_summary_label = QLabel("Total de registros: 0")
        self.report_summary_label.setObjectName("statusBanner")
        self.report_summary_label.setProperty("level", "info")

        report_details_title = QLabel("VISAO GERAL")
        report_details_title.setObjectName("formGroupTitle")
        self.report_full_summary = create_summary_text()

        self.report_status_label = QLabel("")
        self.report_status_label.setObjectName("mutedText")

        self.report_load_button = QPushButton("Carregar relatorio")
        self.report_load_button.setObjectName("secondaryButton")
        self.report_load_button.clicked.connect(self._request_report_view)

        self.report_export_csv_button = QPushButton("CSV")
        self.report_export_csv_button.setObjectName("secondaryButton")
        self.report_export_csv_button.clicked.connect(lambda: self._request_report_export("csv"))

        self.report_export_xlsx_button = QPushButton("XLSX")
        self.report_export_xlsx_button.setObjectName("secondaryButton")
        self.report_export_xlsx_button.clicked.connect(lambda: self._request_report_export("xlsx"))

        self.report_export_pdf_button = QPushButton("PDF")
        self.report_export_pdf_button.setObjectName("secondaryButton")
        self.report_export_pdf_button.clicked.connect(lambda: self._request_report_export("pdf"))

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.report_load_button)
        actions.addWidget(self.report_export_csv_button)
        actions.addWidget(self.report_export_xlsx_button)
        actions.addWidget(self.report_export_pdf_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(report_filter_panel)
        layout.addWidget(self.report_summary_label)
        layout.addWidget(report_details_title)
        layout.addWidget(self.report_full_summary)
        layout.addWidget(self.report_status_label)
        layout.addLayout(actions)

        return panel

    def _build_financial_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("GESTAO FINANCEIRA")
        title.setObjectName("sectionTitle")

        self.financial_type_combo = QComboBox()
        self.financial_type_combo.addItem("Receber", "receivable")
        self.financial_type_combo.addItem("Pagar", "payable")

        self.financial_description_input = QLineEdit()
        self.financial_description_input.setPlaceholderText("Descricao")
        self.financial_amount_input = QLineEdit()
        self.financial_amount_input.setPlaceholderText("0.00")
        self.financial_due_date_input = QLineEdit()
        self.financial_due_date_input.setPlaceholderText("AAAA-MM-DD")
        self.financial_notes_input = QLineEdit()
        self.financial_notes_input.setPlaceholderText("Observacoes")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Tipo", self.financial_type_combo)
        form_layout.addRow("Descricao", self.financial_description_input)
        form_layout.addRow("Valor", self.financial_amount_input)
        form_layout.addRow("Vencimento", self.financial_due_date_input)
        form_layout.addRow("Observacoes", self.financial_notes_input)

        form_panel = QFrame()
        form_panel.setObjectName("formSubPanel")
        form_panel_layout = QVBoxLayout(form_panel)
        form_panel_layout.setContentsMargins(12, 12, 12, 12)
        form_panel_layout.setSpacing(8)
        form_title = QLabel("LANCAMENTO")
        form_title.setObjectName("formGroupTitle")
        form_panel_layout.addWidget(form_title)
        form_panel_layout.addLayout(form_layout)

        details_title = QLabel("DADOS COMPLETOS")
        details_title.setObjectName("formGroupTitle")
        self.financial_full_summary = create_summary_text()
        self.financial_form_status = QLabel("")
        self.financial_form_status.setObjectName("mutedText")

        self.financial_new_button = QPushButton("Novo")
        self.financial_new_button.setObjectName("secondaryButton")
        self.financial_new_button.clicked.connect(self.clear_financial_form)
        self.financial_paid_button = QPushButton("Marcar pago")
        self.financial_paid_button.setObjectName("secondaryButton")
        self.financial_paid_button.clicked.connect(self._request_financial_mark_paid)
        self.financial_cancel_button = QPushButton("Cancelar")
        self.financial_cancel_button.setObjectName("secondaryButton")
        self.financial_cancel_button.clicked.connect(self._request_financial_cancel)
        self.financial_save_button = QPushButton("Salvar lancamento")
        self.financial_save_button.clicked.connect(self._request_financial_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.financial_new_button)
        actions.addWidget(self.financial_paid_button)
        actions.addWidget(self.financial_cancel_button)
        actions.addWidget(self.financial_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(form_panel)
        layout.addWidget(details_title)
        layout.addWidget(self.financial_full_summary)
        layout.addWidget(self.financial_form_status)
        layout.addLayout(actions)

        return panel

    def _build_audit_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("LOGS E AUDITORIA")
        title.setObjectName("sectionTitle")
        self.audit_full_summary = create_summary_text()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(self.audit_full_summary)
        return panel

    def _build_notifications_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("NOTIFICACOES")
        title.setObjectName("sectionTitle")
        self.notifications_full_summary = create_summary_text()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(self.notifications_full_summary)
        return panel

    def clear_customer_form(self) -> None:
        self.selected_customer_id = None
        self.selected_customer_document_path = None
        self.customer_name_input.clear()
        self.customer_email_input.clear()
        self.customer_phone_input.clear()
        self.customer_address_input.clear()
        self.customer_notes_input.clear()
        self.customer_document_path_input.clear()
        self.customer_active_checkbox.setChecked(True)
        self.customer_full_summary.setPlainText("Novo registro de cliente.")
        self.customer_form_status.setText("Novo cliente.")
        self.table.clearSelection()

    def set_customer_form_status(self, message: str, is_error: bool = False) -> None:
        self.customer_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.customer_form_status.setText(message)
        self.customer_form_status.style().unpolish(self.customer_form_status)
        self.customer_form_status.style().polish(self.customer_form_status)

    def set_customer_form_loading(self, is_loading: bool) -> None:
        self.customer_save_button.setEnabled(not is_loading)
        self.customer_new_button.setEnabled(not is_loading)
        self.customer_save_button.setText("Salvando..." if is_loading else "Salvar cliente")

    def set_customer_document_upload_loading(self, is_loading: bool) -> None:
        self.customer_select_document_button.setEnabled(not is_loading)
        self.customer_upload_document_button.setEnabled(
            not is_loading and bool(self.selected_customer_id)
        )
        self.customer_upload_document_button.setText(
            "Enviando..." if is_loading else "Enviar anexo"
        )

    def set_equipment_customers(self, customers: list[dict[str, Any]]) -> None:
        self.equipment_customers = customers

    def clear_equipment_form(self) -> None:
        self.selected_equipment_id = None
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.equipment_visible_rows = []
        self.equipment_board_visible_rows = []
        self.equipment_component_visible_rows = []
        if hasattr(self, "equipment_search_input"):
            self.equipment_search_input.clear()
            self.board_search_input.clear()
            self.component_search_input.clear()
            self.equipment_table.clearSelection()
            self.equipment_boards_table.setRowCount(0)
            self.equipment_components_table.setRowCount(0)
            self.equipment_full_summary.setPlainText(
                "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
            )
            self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
            self.component_full_summary.setPlainText(
                "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
            )
            self.equipment_context_label.setText("_SELECIONE UM EQUIPAMENTO_")
            self.board_context_label.setText("_SELECIONE UM OBJETO VINCULADO_")
            self._update_equipment_action_state()
        self.equipment_form_status.setText("Selecione ou cadastre um equipamento.")
        self.table.clearSelection()

    def set_equipment_form_status(self, message: str, is_error: bool = False) -> None:
        self.equipment_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.equipment_form_status.setText(message)
        self.equipment_form_status.style().unpolish(self.equipment_form_status)
        self.equipment_form_status.style().polish(self.equipment_form_status)

    def set_equipment_form_loading(self, is_loading: bool) -> None:
        self.equipment_new_button.setEnabled(not is_loading)
        self.equipment_edit_button.setEnabled(not is_loading and bool(self.selected_equipment_id))
        self.equipment_remove_button.setEnabled(not is_loading and bool(self.selected_equipment_id))
        self.equipment_new_button.setText("Salvando..." if is_loading else "+Equipamento")

    def set_equipment_object_loading(self, is_loading: bool) -> None:
        has_equipment = bool(self.selected_equipment_id)
        has_board = bool(self.selected_equipment_board_id)
        self.board_add_button.setEnabled(not is_loading and has_equipment)
        self.board_edit_button.setEnabled(not is_loading and has_board)
        self.board_remove_button.setEnabled(not is_loading and has_board)
        self.component_add_button.setEnabled(not is_loading and has_board)
        self.component_edit_button.setEnabled(
            not is_loading and bool(self.selected_equipment_component_id)
        )
        self.component_remove_button.setEnabled(
            not is_loading and bool(self.selected_equipment_component_id)
        )
        self.board_add_button.setText("Salvando..." if is_loading else "+Objeto Vinculado")
        self.component_add_button.setText("Salvando..." if is_loading else "+Componente")

    def clear_inventory_form(self) -> None:
        self.selected_inventory_item_id = None
        self.inventory_sku_input.clear()
        self.inventory_name_input.clear()
        self.inventory_category_input.clear()
        self.inventory_quantity_input.setText("0")
        self.inventory_minimum_quantity_input.setText("0")
        self.inventory_unit_cost_input.setText("0")
        self.inventory_full_summary.setPlainText("Novo registro de estoque.")
        self._set_inventory_stock_status("Status: novo item.", "info")
        self.inventory_form_status.setText("Novo item de estoque.")
        self.table.clearSelection()

    def set_inventory_form_status(self, message: str, is_error: bool = False) -> None:
        self.inventory_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.inventory_form_status.setText(message)
        self.inventory_form_status.style().unpolish(self.inventory_form_status)
        self.inventory_form_status.style().polish(self.inventory_form_status)

    def set_inventory_form_loading(self, is_loading: bool) -> None:
        self.inventory_save_button.setEnabled(not is_loading)
        self.inventory_new_button.setEnabled(not is_loading)
        self.inventory_save_button.setText("Salvando..." if is_loading else "Salvar item")

    def _set_inventory_stock_status(self, message: str, level: str) -> None:
        self.inventory_stock_status.setText(message)
        self.inventory_stock_status.setProperty("level", level)
        self.inventory_stock_status.style().unpolish(self.inventory_stock_status)
        self.inventory_stock_status.style().polish(self.inventory_stock_status)

    def set_service_order_dependencies(
        self,
        customers: list[dict[str, Any]],
        equipment: list[dict[str, Any]],
        technicians: list[dict[str, Any]],
    ) -> None:
        current_customer_id = self.service_order_customer_combo.currentData()
        current_technician_id = self.service_order_technician_combo.currentData()

        self.service_order_customers = customers
        self.service_order_equipment = equipment
        self.service_order_technicians = technicians

        self.service_order_customer_combo.blockSignals(True)
        self.service_order_customer_combo.clear()
        for customer in customers:
            self.service_order_customer_combo.addItem(
                str(customer.get("name") or "Cliente sem nome"),
                str(customer["id"]),
            )
        self.service_order_customer_combo.blockSignals(False)

        self.service_order_technician_combo.clear()
        self.service_order_technician_combo.addItem("Sem tecnico", "")
        for technician in technicians:
            self.service_order_technician_combo.addItem(
                str(technician.get("full_name") or technician.get("email") or "Tecnico"),
                str(technician["id"]),
            )

        if current_customer_id:
            self._select_combo_value(self.service_order_customer_combo, str(current_customer_id))
        if current_technician_id:
            self._select_combo_value(
                self.service_order_technician_combo, str(current_technician_id)
            )

        self._refresh_service_order_equipment_combo()

        if not customers:
            self.set_service_order_form_status("Cadastre um cliente antes da OS.", is_error=True)
        elif not equipment:
            self.set_service_order_form_status(
                "Cadastre um equipamento antes da OS.", is_error=True
            )

    def clear_service_order_form(self) -> None:
        self.selected_service_order_id = None
        if self.service_order_customer_combo.count() > 0:
            self.service_order_customer_combo.setCurrentIndex(0)
        if self.service_order_technician_combo.count() > 0:
            self.service_order_technician_combo.setCurrentIndex(0)
        self._refresh_service_order_equipment_combo()
        self._select_combo_value(self.service_order_priority_combo, "normal")
        self.service_order_sla_input.clear()
        self.service_order_problem_input.clear()
        self.service_order_diagnosis_input.clear()
        self.service_order_rejection_input.clear()
        if self.service_order_budget_type_combo.count() > 0:
            self.service_order_budget_type_combo.setCurrentIndex(0)
        self.service_order_budget_description_input.clear()
        self.service_order_budget_quantity_input.setText("1")
        self.service_order_budget_unit_price_input.setText("0")
        if self.service_order_document_type_combo.count() > 0:
            self.service_order_document_type_combo.setCurrentIndex(0)
        self.selected_service_order_document_path = None
        self.service_order_document_path_input.clear()
        self.service_order_current_status.setText("Status: nova")
        self.service_order_budget_summary.setText("Orcamento: nenhum item.")
        self.service_order_documents_summary.setText("Anexos: nenhum arquivo.")
        self.service_order_full_summary.setPlainText("Novo registro de ordem de servico.")
        self._update_service_order_workflow(None)
        self._set_service_order_flow_buttons_enabled(False)
        self.service_order_form_status.setText("Nova ordem de servico.")
        self.table.clearSelection()

    def set_service_order_form_status(self, message: str, is_error: bool = False) -> None:
        self.service_order_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.service_order_form_status.setText(message)
        self.service_order_form_status.style().unpolish(self.service_order_form_status)
        self.service_order_form_status.style().polish(self.service_order_form_status)

    def set_service_order_form_loading(self, is_loading: bool) -> None:
        self.service_order_save_button.setEnabled(not is_loading)
        self.service_order_new_button.setEnabled(not is_loading)
        if self.selected_service_order_id:
            self._set_service_order_flow_buttons_enabled(not is_loading)
        self.service_order_save_button.setText("Salvando..." if is_loading else "Salvar OS")

    def set_service_order_action_loading(self, is_loading: bool) -> None:
        self.service_order_save_button.setEnabled(not is_loading)
        self.service_order_new_button.setEnabled(not is_loading)
        self._set_service_order_flow_buttons_enabled(
            not is_loading and bool(self.selected_service_order_id)
        )

    def _set_service_order_flow_buttons_enabled(self, enabled: bool) -> None:
        self.service_order_diagnosis_button.setEnabled(enabled)
        self.service_order_add_budget_button.setEnabled(enabled)
        self.service_order_submit_quote_button.setEnabled(enabled)
        self.service_order_approve_button.setEnabled(enabled)
        self.service_order_reject_button.setEnabled(enabled)
        self.service_order_start_button.setEnabled(enabled)
        self.service_order_complete_button.setEnabled(enabled)
        self.service_order_select_document_button.setEnabled(enabled)
        self.service_order_upload_document_button.setEnabled(enabled)

    def set_user_sectors(self, sectors: list[dict[str, Any]]) -> None:
        current_sector_id = self.user_sector_combo.currentData()
        self.user_sectors = sectors
        self.user_sector_combo.clear()
        self.user_sector_combo.addItem("Sem setor", "")

        for sector in sectors:
            self.user_sector_combo.addItem(
                str(sector.get("name") or "Setor sem nome"),
                str(sector["id"]),
            )

        if current_sector_id:
            self._select_combo_value(self.user_sector_combo, str(current_sector_id))
        elif len(sectors) == 1:
            self.user_sector_combo.setCurrentIndex(1)
        self._refresh_session_footer()

    def clear_sector_form(self) -> None:
        self.selected_sector_id = None
        self.sector_name_input.clear()
        self.sector_description_input.clear()
        self.sector_full_summary.setPlainText("Novo registro de setor.")
        self.sector_form_status.setText("Novo setor.")
        is_admin = self.current_user_role == "admin"
        self.sector_new_button.setEnabled(is_admin)
        self.sector_save_button.setEnabled(is_admin)
        self.sector_name_input.setEnabled(is_admin)
        self.sector_description_input.setEnabled(is_admin)
        if not is_admin:
            self.sector_form_status.setText("Setor disponivel apenas para consulta.")
        self.table.clearSelection()

    def set_sector_form_status(self, message: str, is_error: bool = False) -> None:
        self.sector_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.sector_form_status.setText(message)
        self.sector_form_status.style().unpolish(self.sector_form_status)
        self.sector_form_status.style().polish(self.sector_form_status)

    def set_sector_form_loading(self, is_loading: bool) -> None:
        is_admin = self.current_user_role == "admin"
        self.sector_save_button.setEnabled(is_admin and not is_loading)
        self.sector_new_button.setEnabled(is_admin and not is_loading)
        self.sector_save_button.setText("Salvando..." if is_loading else "Salvar setor")

    def clear_user_form(self) -> None:
        self.selected_user_id = None
        self.user_full_name_input.clear()
        self.user_email_input.clear()
        if self.user_role_combo.count() > 0:
            self.user_role_combo.setCurrentIndex(2)
        if self.user_sector_combo.count() > 1:
            self.user_sector_combo.setCurrentIndex(1)
        elif self.user_sector_combo.count() > 0:
            self.user_sector_combo.setCurrentIndex(0)
        self.user_initial_password_input.clear()
        self.user_initial_password_input.setEnabled(True)
        self.user_active_checkbox.setChecked(True)
        self.user_reset_password_input.clear()
        self.user_reset_password_input.setEnabled(False)
        self.user_reset_password_button.setEnabled(False)
        self.user_full_summary.setPlainText("Novo registro de usuario.")
        self.user_form_status.setText("Novo usuario.")
        self.table.clearSelection()

    def set_user_form_status(self, message: str, is_error: bool = False) -> None:
        self.user_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.user_form_status.setText(message)
        self.user_form_status.style().unpolish(self.user_form_status)
        self.user_form_status.style().polish(self.user_form_status)

    def set_user_form_loading(self, is_loading: bool) -> None:
        self.user_save_button.setEnabled(not is_loading)
        self.user_new_button.setEnabled(not is_loading)
        self.user_reset_password_button.setEnabled(not is_loading and bool(self.selected_user_id))
        self.user_save_button.setText("Salvando..." if is_loading else "Salvar usuario")

    def set_user_password_reset_loading(self, is_loading: bool) -> None:
        self.user_reset_password_button.setEnabled(not is_loading and bool(self.selected_user_id))
        self.user_save_button.setEnabled(not is_loading)
        self.user_new_button.setEnabled(not is_loading)
        self.user_reset_password_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )

    def clear_password_reset_form(self) -> None:
        self.selected_password_reset_request_id = None
        self.password_reset_requester_label.setText("Selecione uma solicitacao.")
        self.password_reset_new_password_input.clear()
        self.password_reset_resolve_button.setEnabled(False)
        self.password_reset_full_summary.setPlainText("Nenhuma solicitacao selecionada.")
        self.password_reset_form_status.setText("")
        self.table.clearSelection()

    def set_password_reset_form_status(self, message: str, is_error: bool = False) -> None:
        self.password_reset_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.password_reset_form_status.setText(message)
        self.password_reset_form_status.style().unpolish(self.password_reset_form_status)
        self.password_reset_form_status.style().polish(self.password_reset_form_status)

    def set_password_reset_form_loading(self, is_loading: bool) -> None:
        self.password_reset_resolve_button.setEnabled(
            not is_loading and bool(self.selected_password_reset_request_id)
        )
        self.password_reset_resolve_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )

    def clear_settings_form(self) -> None:
        self.settings_company_name_input.clear()
        self.settings_trade_name_input.clear()
        self.settings_document_input.clear()
        self.settings_email_input.clear()
        self.settings_phone_input.clear()
        self.settings_brand_name_input.clear()
        self.settings_brand_subtitle_input.clear()
        self.settings_primary_color_input.setText("#0969da")
        if self.settings_theme_combo.count() > 0:
            self.settings_theme_combo.setCurrentIndex(0)
        self.settings_backup_enabled_checkbox.setChecked(True)
        self.settings_backup_interval_input.setText("24")
        self.settings_backup_path_input.setText("backups")
        self.settings_backup_last_run_label.setText("Ultimo backup: nunca")
        self.settings_full_summary.setPlainText("Configuracoes ainda nao carregadas.")
        self.settings_form_status.setText("")

    def set_settings_form_status(self, message: str, is_error: bool = False) -> None:
        self.settings_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.settings_form_status.setText(message)
        self.settings_form_status.style().unpolish(self.settings_form_status)
        self.settings_form_status.style().polish(self.settings_form_status)

    def set_settings_form_loading(self, is_loading: bool) -> None:
        self.settings_save_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setEnabled(not is_loading)
        self.settings_save_button.setText("Salvando..." if is_loading else "Salvar configuracoes")

    def set_backup_run_loading(self, is_loading: bool) -> None:
        self.settings_save_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setText(
            "Executando..." if is_loading else "Executar backup agora"
        )

    def clear_report_form(self) -> None:
        self._select_combo_value(self.report_module_combo, self.current_report_module_key)
        self.report_summary_label.setText("Total de registros: 0")
        self.report_full_summary.setPlainText("Carregue um relatorio para ver a visao geral.")
        self.report_status_label.setText("")

    def set_report_status(self, message: str, is_error: bool = False) -> None:
        self.report_status_label.setObjectName("errorText" if is_error else "mutedText")
        self.report_status_label.setText(message)
        self.report_status_label.style().unpolish(self.report_status_label)
        self.report_status_label.style().polish(self.report_status_label)

    def set_report_loading(self, is_loading: bool) -> None:
        self.report_load_button.setEnabled(not is_loading)
        self.report_export_csv_button.setEnabled(not is_loading)
        self.report_export_xlsx_button.setEnabled(not is_loading)
        self.report_export_pdf_button.setEnabled(not is_loading)
        self.report_load_button.setText("Carregando..." if is_loading else "Carregar relatorio")

    def set_report_export_loading(self, is_loading: bool) -> None:
        self.report_load_button.setEnabled(not is_loading)
        self.report_export_csv_button.setEnabled(not is_loading)
        self.report_export_xlsx_button.setEnabled(not is_loading)
        self.report_export_pdf_button.setEnabled(not is_loading)

    def clear_financial_form(self) -> None:
        self.selected_financial_record_id = None
        if self.financial_type_combo.count() > 0:
            self.financial_type_combo.setCurrentIndex(0)
        self.financial_description_input.clear()
        self.financial_amount_input.clear()
        self.financial_due_date_input.clear()
        self.financial_notes_input.clear()
        self.financial_full_summary.setPlainText("Novo lancamento financeiro.")
        self.financial_form_status.setText("Novo lancamento.")
        self.financial_paid_button.setEnabled(False)
        self.financial_cancel_button.setEnabled(False)
        self.table.clearSelection()

    def set_financial_form_status(self, message: str, is_error: bool = False) -> None:
        self.financial_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.financial_form_status.setText(message)
        self.financial_form_status.style().unpolish(self.financial_form_status)
        self.financial_form_status.style().polish(self.financial_form_status)

    def set_financial_form_loading(self, is_loading: bool) -> None:
        has_selection = bool(self.selected_financial_record_id)
        self.financial_save_button.setEnabled(not is_loading)
        self.financial_new_button.setEnabled(not is_loading)
        self.financial_paid_button.setEnabled(not is_loading and has_selection)
        self.financial_cancel_button.setEnabled(not is_loading and has_selection)
        self.financial_save_button.setText("Salvando..." if is_loading else "Salvar lancamento")

    def clear_audit_form(self) -> None:
        self.audit_full_summary.setPlainText("Selecione um log para ver os detalhes.")

    def clear_notifications_form(self) -> None:
        self.notifications_full_summary.setPlainText(
            "Selecione uma notificacao para ver os detalhes."
        )

    def _set_active_module(self, module_key: str) -> None:
        previous_module_key = self.active_module_key
        self.active_module_key = module_key
        self.current_rows = []
        self.title_label.setText(self.module_labels.get(module_key, "Dashboard"))
        if hasattr(self, "data_description"):
            self.data_description.setText(self.module_descriptions.get(module_key, ""))
        if hasattr(self, "module_search_input"):
            self.module_search_input.setPlaceholderText(self._module_search_placeholder(module_key))
            if previous_module_key != module_key:
                self.module_search_input.blockSignals(True)
                self.module_search_input.clear()
                self.module_search_input.blockSignals(False)
        if hasattr(self, "session_module_label"):
            self.session_module_label.setText(
                self.module_labels.get(module_key, "Painel Principal")
            )
        self.setWindowTitle(
            f"{self.sidebar_title.text() or 'PRO CORE'} - {self.title_label.text()}"
        )
        self._mark_active_nav(module_key)
        self.dashboard_section_title.setVisible(module_key == "dashboard")
        self.dashboard_greeting_label.setVisible(module_key == "dashboard")
        self.dashboard_last_refresh_label.setVisible(module_key == "dashboard")
        self.dashboard_grid_widget.setVisible(module_key == "dashboard")
        self.dashboard_alerts_frame.setVisible(module_key == "dashboard")
        self.generic_record_splitter.setVisible(module_key in self.record_module_keys)
        self.data_title.setVisible(module_key not in {"dashboard", "equipment"})
        self.data_description.setVisible(module_key not in {"dashboard", "equipment"})
        self.module_search_input.setVisible(module_key in self.searchable_module_keys)
        self.table.setVisible(module_key in self.searchable_module_keys or module_key == "reports")
        self.customer_form_panel.setVisible(module_key == "customers")
        self.equipment_form_panel.setVisible(module_key == "equipment")
        self.inventory_form_panel.setVisible(module_key == "inventory")
        self.service_order_form_panel.setVisible(module_key == "service_orders")
        self.sector_form_panel.setVisible(module_key == "sectors")
        self.user_form_panel.setVisible(module_key == "users")
        self.password_reset_form_panel.setVisible(module_key == "password_resets")
        self.settings_form_panel.setVisible(module_key == "settings")
        self.report_form_panel.setVisible(module_key == "reports")
        self.financial_form_panel.setVisible(module_key == "financial")
        self.audit_form_panel.setVisible(module_key == "audit_logs")
        self.notifications_form_panel.setVisible(module_key == "notifications")
        if module_key == "customers":
            self.clear_customer_form()
        elif module_key == "equipment":
            self.clear_equipment_form()
        elif module_key == "inventory":
            self.clear_inventory_form()
        elif module_key == "service_orders":
            self.clear_service_order_form()
        elif module_key == "sectors":
            self.clear_sector_form()
        elif module_key == "users":
            self.clear_user_form()
        elif module_key == "password_resets":
            self.clear_password_reset_form()
        elif module_key == "settings":
            self.clear_settings_form()
        elif module_key == "reports":
            self.clear_report_form()
        elif module_key == "financial":
            self.clear_financial_form()
        elif module_key == "audit_logs":
            self.clear_audit_form()
        elif module_key == "notifications":
            self.clear_notifications_form()

    def _handle_table_selection(self) -> None:
        if self.active_module_key not in {
            "customers",
            "equipment",
            "inventory",
            "service_orders",
            "sectors",
            "users",
            "password_resets",
            "financial",
            "audit_logs",
            "notifications",
        }:
            return

        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        row_index = selected_items[0].row()
        if row_index >= len(self.current_rows):
            return

        if self.active_module_key == "customers":
            self._populate_customer_form(self.current_rows[row_index])
            return

        if self.active_module_key == "equipment":
            self._populate_equipment_form(self.current_rows[row_index])
            return

        if self.active_module_key == "inventory":
            self._populate_inventory_form(self.current_rows[row_index])
            return

        if self.active_module_key == "service_orders":
            self._populate_service_order_form(self.current_rows[row_index])
            return

        if self.active_module_key == "sectors":
            self._populate_sector_form(self.current_rows[row_index])
            return

        if self.active_module_key == "password_resets":
            self._populate_password_reset_form(self.current_rows[row_index])
            return

        if self.active_module_key == "financial":
            self._populate_financial_form(self.current_rows[row_index])
            return

        if self.active_module_key == "audit_logs":
            self.audit_full_summary.setPlainText(
                self._format_audit_summary(self.current_rows[row_index])
            )
            return

        if self.active_module_key == "notifications":
            self.notifications_full_summary.setPlainText(
                self._format_notification_summary(self.current_rows[row_index])
            )
            return

        self._populate_user_form(self.current_rows[row_index])

    def _populate_customer_form(self, customer: dict[str, Any]) -> None:
        self.selected_customer_id = str(customer["id"])
        self.selected_customer_document_path = None
        self.customer_name_input.setText(str(customer.get("name") or ""))
        self.customer_email_input.setText(str(customer.get("email") or ""))
        self.customer_phone_input.setText(str(customer.get("phone") or ""))
        self.customer_address_input.setText(str(customer.get("address") or ""))
        self.customer_notes_input.setText(str(customer.get("notes") or ""))
        self.customer_document_path_input.clear()
        self.customer_active_checkbox.setChecked(bool(customer.get("is_active", True)))
        self.customer_full_summary.setPlainText(self._format_customer_full_summary(customer))
        self.set_customer_form_status("Editando cliente selecionado.")

    def _request_customer_save(self) -> None:
        name = self.customer_name_input.text().strip()
        email = self.customer_email_input.text().strip().lower()
        phone = self.customer_phone_input.text().strip()
        if not name:
            self.set_customer_form_status("Informe o nome do cliente.", is_error=True)
            return

        if not email:
            self.set_customer_form_status("Informe o email do cliente.", is_error=True)
            return

        if not self._is_complete_phone(phone):
            self.set_customer_form_status(
                "Informe o telefone no formato (DD) 99999-9999.",
                is_error=True,
            )
            return

        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": self._optional_text(self.customer_address_input),
            "notes": self._optional_text(self.customer_notes_input),
            "is_active": self.customer_active_checkbox.isChecked(),
        }

        self.set_customer_form_status("")
        if self.selected_customer_id:
            self.customer_update_requested.emit(self.selected_customer_id, payload)
            return

        self.customer_create_requested.emit(payload)

    def _select_customer_document(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Selecionar anexo",
            "",
            "Arquivos (*.*)",
        )
        if not file_path:
            return

        self.selected_customer_document_path = file_path
        self.customer_document_path_input.setText(file_path)

    def _request_customer_document_upload(self) -> None:
        if not self.selected_customer_id:
            self.set_customer_form_status(
                "Salve ou selecione um cliente antes do anexo.", is_error=True
            )
            return

        file_path = self.selected_customer_document_path
        if not file_path:
            self.set_customer_form_status("Selecione um anexo.", is_error=True)
            return

        if not Path(file_path).exists():
            self.set_customer_form_status("Arquivo selecionado nao existe.", is_error=True)
            return

        self.customer_document_upload_requested.emit(self.selected_customer_id, "other", file_path)

    def _render_equipment_rows(self, title: str, rows: list[dict[str, Any]]) -> None:
        self._set_active_module("equipment")
        self.current_rows = rows
        self.data_title.setText(title)
        self.empty_label.hide()
        self.table.hide()
        self._refresh_equipment_table()
        if not rows:
            self.set_equipment_form_status("Nenhum equipamento cadastrado.")
        else:
            self.set_equipment_form_status("Equipamentos carregados.")

    def _populate_equipment_form(self, equipment: dict[str, Any]) -> None:
        self._select_equipment_by_id(str(equipment["id"]))

    def _refresh_equipment_table(self) -> None:
        term = self.equipment_search_input.text().strip().lower()
        self.equipment_visible_rows = [
            row
            for row in self.current_rows
            if self._row_matches(
                row,
                ("id", "category", "brand", "model", "special_number"),
                term,
            )
        ]
        self._fill_equipment_table(
            self.equipment_table,
            self.equipment_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("category")),
                lambda row: self._format_value(row.get("brand")),
                lambda row: self._format_value(row.get("model")),
                lambda row: self._format_value(row.get("special_number")),
            ],
        )
        if not self.equipment_visible_rows:
            self.selected_equipment_id = None
            self.equipment_full_summary.setPlainText(
                "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
            )
            self._refresh_equipment_boards_table()
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_table,
            self.equipment_visible_rows,
            self.selected_equipment_id,
        ):
            self.equipment_table.selectRow(0)

    def _refresh_equipment_boards_table(self) -> None:
        equipment = self._selected_equipment()
        boards = equipment.get("boards") if equipment else []
        term = self.board_search_input.text().strip().lower()
        self.equipment_board_visible_rows = [
            board
            for board in (boards or [])
            if self._row_matches(board, ("id", "name", "special_number", "model", "revision"), term)
        ]
        self._fill_equipment_table(
            self.equipment_boards_table,
            self.equipment_board_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("name")),
                lambda row: self._format_value(row.get("special_number")),
                lambda row: self._format_value(row.get("model")),
                lambda row: self._format_value(row.get("revision")),
            ],
        )
        if not self.equipment_board_visible_rows:
            self.selected_equipment_board_id = None
            self.selected_equipment_component_id = None
            self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
            self._refresh_equipment_components_table()
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_boards_table,
            self.equipment_board_visible_rows,
            self.selected_equipment_board_id,
        ):
            self.equipment_boards_table.selectRow(0)

    def _refresh_equipment_components_table(self) -> None:
        board = self._selected_equipment_board()
        components = board.get("components") if board else []
        term = self.component_search_input.text().strip().lower()
        self.equipment_component_visible_rows = [
            component
            for component in (components or [])
            if self._row_matches(
                component,
                ("id", "category", "name", "part_number", "location", "notes"),
                term,
            )
        ]
        self._fill_equipment_table(
            self.equipment_components_table,
            self.equipment_component_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("category")),
                lambda row: self._format_value(row.get("name")),
                lambda row: self._format_value(row.get("part_number")),
                lambda row: self._format_value(row.get("location")),
                lambda row: self._format_value(row.get("notes")),
            ],
        )
        if not self.equipment_component_visible_rows:
            self.selected_equipment_component_id = None
            self.component_full_summary.setPlainText(
                "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
            )
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_components_table,
            self.equipment_component_visible_rows,
            self.selected_equipment_component_id,
        ):
            self.equipment_components_table.selectRow(0)

    def _handle_equipment_table_selection(self) -> None:
        selected_items = self.equipment_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_visible_rows):
            return
        equipment = self.equipment_visible_rows[row_index]
        self.selected_equipment_id = str(equipment["id"])
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.equipment_full_summary.setPlainText(self._format_equipment_full_summary(equipment))
        self.equipment_context_label.setText(
            f"_EQUIPAMENTO: {self._equipment_label(equipment).upper()}_"
        )
        self._refresh_equipment_boards_table()
        self._update_equipment_action_state()

    def _handle_equipment_board_table_selection(self) -> None:
        selected_items = self.equipment_boards_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_board_visible_rows):
            return
        board = self.equipment_board_visible_rows[row_index]
        self.selected_equipment_board_id = str(board["id"])
        self.selected_equipment_component_id = None
        self.board_full_summary.setPlainText(self._format_equipment_board_summary(board))
        self.board_context_label.setText(f"_OBJETO: {self._board_label(board).upper()}_")
        self._refresh_equipment_components_table()
        self._update_equipment_action_state()

    def _handle_equipment_component_table_selection(self) -> None:
        selected_items = self.equipment_components_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_component_visible_rows):
            return
        component = self.equipment_component_visible_rows[row_index]
        self.selected_equipment_component_id = str(component["id"])
        self.component_full_summary.setPlainText(
            self._format_equipment_component_summary(component)
        )
        self._update_equipment_action_state()

    def _open_equipment_create_dialog(self) -> None:
        dialog = EquipmentAssetDialog(
            "NOVO EQUIPAMENTO",
            self._equipment_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_create_requested.emit(dialog.payload())

    def _open_equipment_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR EQUIPAMENTO",
            self._equipment_dialog_fields(),
            equipment,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_update_requested.emit(str(equipment["id"]), dialog.payload())

    def _request_equipment_delete(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        if (
            QMessageBox.question(
                self,
                "Remover equipamento",
                "Remover o equipamento selecionado?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self.equipment_delete_requested.emit(str(equipment["id"]))

    def _request_equipment_board_create(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "NOVO OBJETO VINCULADO",
            self._board_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_board_create_requested.emit(str(equipment["id"]), dialog.payload())

    def _open_equipment_board_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment or not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR OBJETO VINCULADO",
            self._board_dialog_fields(),
            board,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_board_update_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            dialog.payload(),
        )

    def _request_equipment_board_delete(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment or not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        if (
            QMessageBox.question(
                self,
                "Remover objeto",
                "Remover o objeto vinculado selecionado?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self.equipment_board_delete_requested.emit(str(equipment["id"]), str(board["id"]))

    def _request_equipment_component_create(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        if not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "NOVO COMPONENTE",
            self._component_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_component_create_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            dialog.payload(),
        )

    def _open_equipment_component_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        if not equipment or not board or not component:
            self.set_equipment_form_status("Selecione um componente.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR COMPONENTE",
            self._component_dialog_fields(),
            component,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_component_update_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            str(component["id"]),
            dialog.payload(),
        )

    def _request_equipment_component_delete(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        if not equipment or not board or not component:
            self.set_equipment_form_status("Selecione um componente.", is_error=True)
            return
        if (
            QMessageBox.question(
                self,
                "Remover componente",
                "Remover o componente selecionado?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self.equipment_component_delete_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            str(component["id"]),
        )

    def _update_equipment_action_state(self) -> None:
        has_equipment = bool(self.selected_equipment_id)
        has_board = bool(self.selected_equipment_board_id)
        has_component = bool(self.selected_equipment_component_id)
        self.equipment_edit_button.setEnabled(has_equipment)
        self.equipment_remove_button.setEnabled(has_equipment)
        self.board_add_button.setEnabled(has_equipment)
        self.board_edit_button.setEnabled(has_board)
        self.board_remove_button.setEnabled(has_board)
        self.component_add_button.setEnabled(has_board)
        self.component_edit_button.setEnabled(has_component)
        self.component_remove_button.setEnabled(has_component)

    def _selected_equipment(self) -> dict[str, Any] | None:
        return self._find_by_id(self.current_rows, self.selected_equipment_id)

    def _selected_equipment_board(self) -> dict[str, Any] | None:
        equipment = self._selected_equipment()
        if not equipment:
            return None
        return self._find_by_id(equipment.get("boards") or [], self.selected_equipment_board_id)

    def _selected_equipment_component(self) -> dict[str, Any] | None:
        board = self._selected_equipment_board()
        if not board:
            return None
        return self._find_by_id(
            board.get("components") or [],
            self.selected_equipment_component_id,
        )

    def _select_equipment_by_id(self, equipment_id: str) -> None:
        self.selected_equipment_id = equipment_id
        self._select_visible_table_row(
            self.equipment_table,
            self.equipment_visible_rows,
            equipment_id,
        )

    def _fill_equipment_table(
        self,
        table: QTableWidget,
        rows: list[dict[str, Any]],
        getters: list,
    ) -> None:
        table.blockSignals(True)
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, getter in enumerate(getters):
                item = QTableWidgetItem(str(getter(row) or ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setData(Qt.ItemDataRole.UserRole, str(row.get("id") or ""))
                table.setItem(row_index, column_index, item)
        table.blockSignals(False)

    def _select_visible_table_row(
        self,
        table: QTableWidget,
        rows: list[dict[str, Any]],
        selected_id: str | None,
    ) -> bool:
        if not selected_id:
            return False
        for row_index, row in enumerate(rows):
            if str(row.get("id")) == selected_id:
                table.selectRow(row_index)
                return True
        return False

    @staticmethod
    def _find_by_id(rows: list[dict[str, Any]], row_id: str | None) -> dict[str, Any] | None:
        if not row_id:
            return None
        for row in rows:
            if str(row.get("id")) == row_id:
                return row
        return None

    @staticmethod
    def _row_matches(row: dict[str, Any], keys: tuple[str, ...], term: str) -> bool:
        if not term:
            return True
        return any(term in str(row.get(key) or "").lower() for key in keys)

    @staticmethod
    def _short_id(value: Any) -> str:
        text = str(value or "")
        return text[:8] if len(text) > 8 else text

    @staticmethod
    def _equipment_label(equipment: dict[str, Any]) -> str:
        return (
            " - ".join(
                part
                for part in [
                    str(equipment.get("category") or ""),
                    str(equipment.get("brand") or ""),
                    str(equipment.get("model") or ""),
                    str(equipment.get("special_number") or ""),
                ]
                if part
            )
            or "Equipamento sem descricao"
        )

    @staticmethod
    def _board_label(board: dict[str, Any]) -> str:
        return str(board.get("name") or board.get("model") or "Objeto vinculado")

    @staticmethod
    def _equipment_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "category",
                "label": "Tipo:",
                "placeholder": "Tipo do equipamento",
                "required": True,
            },
            {"key": "brand", "label": "Marca:", "placeholder": "Marca do equipamento"},
            {"key": "model", "label": "Modelo:", "placeholder": "Modelo do equipamento"},
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, S120-CU320",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 1499,90",
                "money": True,
            },
            {
                "key": "description",
                "label": "Notas:",
                "placeholder": "Observacoes gerais (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _board_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Nome:",
                "placeholder": "Nome do objeto vinculado",
                "required": True,
            },
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, numero de inventario",
            },
            {"key": "model", "label": "Modelo / Tipo:", "placeholder": "Modelo / tipo da placa"},
            {"key": "revision", "label": "Revisao:", "placeholder": "Ex.: A01, B02, Rev.C"},
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 980,00",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Notas:",
                "placeholder": "Observacoes (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _component_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Dados:",
                "placeholder": "Dados do componente",
                "required": True,
            },
            {"key": "category", "label": "Categoria:", "placeholder": "Categoria do componente"},
            {
                "key": "part_number",
                "label": "Modelo / Part Number:",
                "placeholder": "Ex.: BC547B, IRFZ44N",
            },
            {
                "key": "location",
                "label": "Localizacao:",
                "placeholder": "Ex.: Gaveta A3, Bandeja 2",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 12,50",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Observacoes:",
                "placeholder": "Observacoes",
                "multiline": True,
            },
        ]

    def _populate_inventory_form(self, item: dict[str, Any]) -> None:
        self.selected_inventory_item_id = str(item["id"])
        self.inventory_sku_input.setText(str(item.get("sku") or ""))
        self.inventory_name_input.setText(str(item.get("name") or ""))
        self.inventory_category_input.setText(str(item.get("category") or ""))
        self.inventory_quantity_input.setText(str(item.get("quantity") or "0"))
        self.inventory_minimum_quantity_input.setText(str(item.get("minimum_quantity") or "0"))
        self.inventory_unit_cost_input.setText(str(item.get("unit_cost") or "0"))
        self.inventory_full_summary.setPlainText(self._format_inventory_full_summary(item))
        if self._inventory_is_low(item):
            self._set_inventory_stock_status(
                "Estoque critico: quantidade no minimo ou abaixo.", "error"
            )
        else:
            self._set_inventory_stock_status("Estoque em nivel operacional.", "info")
        self.set_inventory_form_status("Editando item selecionado.")

    def _request_inventory_save(self) -> None:
        name = self.inventory_name_input.text().strip()
        if not name:
            self.set_inventory_form_status("Informe o nome do item.", is_error=True)
            return

        quantity = self._decimal_text(self.inventory_quantity_input, "Quantidade")
        minimum_quantity = self._decimal_text(
            self.inventory_minimum_quantity_input,
            "Quantidade minima",
        )
        unit_cost = self._decimal_text(self.inventory_unit_cost_input, "Custo unitario")
        if quantity is None or minimum_quantity is None or unit_cost is None:
            return

        payload = {
            "sku": self._optional_text(self.inventory_sku_input),
            "name": name,
            "category": self._optional_text(self.inventory_category_input),
            "quantity": quantity,
            "minimum_quantity": minimum_quantity,
            "unit_cost": unit_cost,
        }

        self.set_inventory_form_status("")
        if self.selected_inventory_item_id:
            self.inventory_update_requested.emit(self.selected_inventory_item_id, payload)
            return

        self.inventory_create_requested.emit(payload)

    def _populate_service_order_form(self, service_order: dict[str, Any]) -> None:
        self.selected_service_order_id = str(service_order["id"])
        self._select_combo_value(
            self.service_order_customer_combo,
            str(service_order.get("customer_id") or ""),
        )
        self._refresh_service_order_equipment_combo()
        self._select_combo_value(
            self.service_order_equipment_combo,
            str(service_order.get("equipment_id") or ""),
        )
        self._select_combo_value(
            self.service_order_technician_combo,
            str(service_order.get("assigned_technician_id") or ""),
        )
        self._select_combo_value(
            self.service_order_priority_combo,
            str(service_order.get("priority") or "normal"),
        )
        self.service_order_sla_input.setText(str(service_order.get("sla_due_at") or ""))
        self.service_order_problem_input.setText(
            str(service_order.get("problem_description") or "")
        )
        self.service_order_diagnosis_input.setText(
            str(service_order.get("technical_diagnosis") or "")
        )
        self.service_order_rejection_input.setText(str(service_order.get("rejection_reason") or ""))
        self.service_order_budget_description_input.clear()
        self.service_order_budget_quantity_input.setText("1")
        self.service_order_budget_unit_price_input.setText("0")
        self.selected_service_order_document_path = None
        self.service_order_document_path_input.clear()
        self.service_order_current_status.setText(
            f"Status: {self._format_value(service_order.get('status'))}"
        )
        self._update_service_order_workflow(str(service_order.get("status") or ""))
        self.service_order_full_summary.setPlainText(
            self._format_service_order_full_summary(service_order)
        )
        self.service_order_budget_summary.setText(self._format_service_order_budget(service_order))
        self.service_order_documents_summary.setText(
            self._format_service_order_documents(service_order)
        )
        self._set_service_order_flow_buttons_enabled(True)
        self.set_service_order_form_status("Editando ordem de servico selecionada.")

    def _request_service_order_save(self) -> None:
        customer_id = self.service_order_customer_combo.currentData()
        equipment_id = self.service_order_equipment_combo.currentData()
        technician_id = self.service_order_technician_combo.currentData()
        problem_description = self.service_order_problem_input.text().strip()

        if not customer_id:
            self.set_service_order_form_status("Selecione um cliente.", is_error=True)
            return

        if not equipment_id:
            self.set_service_order_form_status("Selecione um equipamento.", is_error=True)
            return

        if not problem_description:
            self.set_service_order_form_status("Informe o problema da OS.", is_error=True)
            return

        if self.selected_service_order_id:
            payload = {
                "assigned_technician_id": str(technician_id) if technician_id else None,
                "priority": str(self.service_order_priority_combo.currentData() or "normal"),
                "sla_due_at": self._optional_text(self.service_order_sla_input),
                "problem_description": problem_description,
                "technical_diagnosis": self._optional_text(self.service_order_diagnosis_input),
                "rejection_reason": self._optional_text(self.service_order_rejection_input),
            }
            self.service_order_update_requested.emit(self.selected_service_order_id, payload)
            return

        payload = {
            "customer_id": str(customer_id),
            "equipment_id": str(equipment_id),
            "assigned_technician_id": str(technician_id) if technician_id else None,
            "priority": str(self.service_order_priority_combo.currentData() or "normal"),
            "sla_due_at": self._optional_text(self.service_order_sla_input),
            "problem_description": problem_description,
        }
        self.service_order_create_requested.emit(payload)

    def _request_service_order_diagnosis(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return

        diagnosis = self.service_order_diagnosis_input.text().strip()
        if not diagnosis:
            self.set_service_order_form_status("Informe o diagnostico tecnico.", is_error=True)
            return

        self.set_service_order_form_status("")
        self.service_order_diagnosis_requested.emit(self.selected_service_order_id, diagnosis)

    def _request_service_order_budget_item(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return

        description = self.service_order_budget_description_input.text().strip()
        if not description:
            self.set_service_order_form_status("Informe a descricao do item.", is_error=True)
            return

        quantity = self._decimal_text_for_service_order(
            self.service_order_budget_quantity_input,
            "Quantidade",
            allow_zero=False,
        )
        unit_price = self._decimal_text_for_service_order(
            self.service_order_budget_unit_price_input,
            "Valor unitario",
            allow_zero=True,
        )
        if quantity is None or unit_price is None:
            return

        payload = {
            "inventory_item_id": None,
            "item_type": str(self.service_order_budget_type_combo.currentData() or "service"),
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
        }
        self.set_service_order_form_status("")
        self.service_order_budget_item_requested.emit(self.selected_service_order_id, payload)

    def _request_service_order_submit_quote(self) -> None:
        if self._require_selected_service_order():
            self.service_order_submit_quote_requested.emit(self.selected_service_order_id)

    def _request_service_order_approve(self) -> None:
        if self._require_selected_service_order():
            self.service_order_approve_requested.emit(self.selected_service_order_id)

    def _request_service_order_reject(self) -> None:
        if not self._require_selected_service_order():
            return

        rejection_reason = self.service_order_rejection_input.text().strip()
        if not rejection_reason:
            self.set_service_order_form_status("Informe o motivo da reprovacao.", is_error=True)
            return

        self.service_order_reject_requested.emit(self.selected_service_order_id, rejection_reason)

    def _request_service_order_start(self) -> None:
        if self._require_selected_service_order():
            self.service_order_start_requested.emit(self.selected_service_order_id)

    def _request_service_order_complete(self) -> None:
        if self._require_selected_service_order():
            self.service_order_complete_requested.emit(self.selected_service_order_id)

    def _select_service_order_document(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Selecionar anexo",
            "",
            "Arquivos (*.*)",
        )
        if not file_path:
            return

        self.selected_service_order_document_path = file_path
        self.service_order_document_path_input.setText(file_path)

    def _request_service_order_document_upload(self) -> None:
        if not self._require_selected_service_order():
            return

        file_path = self.selected_service_order_document_path
        if not file_path:
            self.set_service_order_form_status("Selecione um arquivo.", is_error=True)
            return

        if not Path(file_path).exists():
            self.set_service_order_form_status("Arquivo selecionado nao existe.", is_error=True)
            return

        document_type = str(self.service_order_document_type_combo.currentData() or "other")
        self.set_service_order_form_status("")
        self.service_order_document_upload_requested.emit(
            self.selected_service_order_id,
            document_type,
            file_path,
        )

    def _require_selected_service_order(self) -> bool:
        if self.selected_service_order_id:
            self.set_service_order_form_status("")
            return True

        self.set_service_order_form_status("Selecione uma OS.", is_error=True)
        return False

    def _update_service_order_workflow(self, status: str | None) -> None:
        stage_by_status = {
            "open": 0,
            "assigned": 0,
            "pending_quote": 1,
            "quote_sent": 2,
            "pending_approval": 3,
            "approved": 3,
            "in_progress": 4,
            "completed": 5,
            "rejected": 5,
            "closed": 5,
        }
        current_stage = stage_by_status.get(status or "", 0)
        for index, label in enumerate(self.service_order_workflow_steps):
            if index < current_stage:
                stage = "done"
            elif index == current_stage:
                stage = "active"
            else:
                stage = "future"
            label.setProperty("stage", stage)
            label.style().unpolish(label)
            label.style().polish(label)

    def _populate_sector_form(self, sector: dict[str, Any]) -> None:
        self.selected_sector_id = str(sector["id"])
        self.sector_name_input.setText(str(sector.get("name") or ""))
        self.sector_description_input.setText(str(sector.get("description") or ""))
        is_admin = self.current_user_role == "admin"
        self.sector_new_button.setEnabled(is_admin)
        self.sector_save_button.setEnabled(is_admin)
        self.sector_name_input.setEnabled(is_admin)
        self.sector_description_input.setEnabled(is_admin)
        status_message = (
            "Editando setor selecionado." if is_admin else "Setor disponivel apenas para consulta."
        )
        self.sector_full_summary.setPlainText(self._format_sector_summary(sector))
        self.set_sector_form_status(status_message)

    def _request_sector_save(self) -> None:
        name = self.sector_name_input.text().strip()
        if not name:
            self.set_sector_form_status("Informe o nome do setor.", is_error=True)
            return

        payload = {
            "name": name,
            "description": self._optional_text(self.sector_description_input),
        }

        self.set_sector_form_status("")
        if self.selected_sector_id:
            self.sector_update_requested.emit(self.selected_sector_id, payload)
            return

        self.sector_create_requested.emit(payload)

    def _populate_user_form(self, user: dict[str, Any]) -> None:
        self.selected_user_id = str(user["id"])
        self.user_full_name_input.setText(str(user.get("full_name") or ""))
        self.user_email_input.setText(str(user.get("email") or ""))
        self._select_combo_value(self.user_role_combo, str(user.get("role") or "technician"))
        self._select_combo_value(self.user_sector_combo, str(user.get("sector_id") or ""))
        self.user_initial_password_input.clear()
        self.user_initial_password_input.setEnabled(False)
        self.user_active_checkbox.setChecked(bool(user.get("is_active", True)))
        self.user_reset_password_input.clear()
        self.user_reset_password_input.setEnabled(True)
        self.user_reset_password_button.setEnabled(True)
        self.user_full_summary.setPlainText(self._format_user_summary(user))
        self.set_user_form_status("Editando usuario selecionado.")

    def _request_user_save(self) -> None:
        full_name = self.user_full_name_input.text().strip()
        email = self.user_email_input.text().strip().lower()
        role = self.user_role_combo.currentData()
        sector_id = self.user_sector_combo.currentData()

        if not full_name:
            self.set_user_form_status("Informe o nome do usuario.", is_error=True)
            return

        if not email:
            self.set_user_form_status("Informe o email do usuario.", is_error=True)
            return

        if not role:
            self.set_user_form_status("Selecione o perfil do usuario.", is_error=True)
            return

        payload = {
            "full_name": full_name,
            "email": email,
            "role": str(role),
            "sector_id": str(sector_id) if sector_id else None,
            "is_active": self.user_active_checkbox.isChecked(),
        }

        self.set_user_form_status("")
        if self.selected_user_id:
            self.user_update_requested.emit(self.selected_user_id, payload)
            return

        password = self.user_initial_password_input.text()
        if not password:
            self.set_user_form_status("Informe a senha inicial.", is_error=True)
            return

        create_payload = payload.copy()
        create_payload.pop("is_active")
        create_payload["password"] = password
        self.user_create_requested.emit(create_payload)

    def _request_user_password_reset(self) -> None:
        if not self.selected_user_id:
            self.set_user_form_status("Selecione um usuario para redefinir a senha.", is_error=True)
            return

        new_password = self.user_reset_password_input.text()
        if not new_password:
            self.set_user_form_status("Informe a nova senha.", is_error=True)
            return

        self.set_user_form_status("")
        self.user_password_reset_requested.emit(self.selected_user_id, new_password)

    def _populate_password_reset_form(self, request: dict[str, Any]) -> None:
        self.selected_password_reset_request_id = str(request["id"])
        full_name = self._format_value(request.get("requester_full_name"))
        email = self._format_value(request.get("requester_email"))
        role = self._format_value(request.get("requester_role"))
        created_at = self._format_value(request.get("created_at"))
        self.password_reset_requester_label.setText(
            f"Solicitante: {full_name} | {email} | Perfil: {role} | Criada em: {created_at}"
        )
        self.password_reset_new_password_input.clear()
        self.password_reset_resolve_button.setEnabled(True)
        self.password_reset_full_summary.setPlainText(self._format_password_reset_summary(request))
        self.set_password_reset_form_status("Informe uma nova senha temporaria.")

    def _request_password_reset_resolve(self) -> None:
        if not self.selected_password_reset_request_id:
            self.set_password_reset_form_status(
                "Selecione uma solicitacao.",
                is_error=True,
            )
            return

        new_password = self.password_reset_new_password_input.text()
        if not new_password:
            self.set_password_reset_form_status("Informe a nova senha.", is_error=True)
            return

        self.set_password_reset_form_status("")
        self.password_reset_resolve_requested.emit(
            self.selected_password_reset_request_id,
            new_password,
        )

    def _populate_financial_form(self, record: dict[str, Any]) -> None:
        self.selected_financial_record_id = str(record["id"])
        self._select_combo_value(
            self.financial_type_combo,
            str(record.get("record_type") or "receivable"),
        )
        self.financial_description_input.setText(str(record.get("description") or ""))
        self.financial_amount_input.setText(str(record.get("amount") or ""))
        self.financial_due_date_input.setText(str(record.get("due_date") or ""))
        self.financial_notes_input.setText(str(record.get("notes") or ""))
        self.financial_full_summary.setPlainText(self._format_financial_summary(record))
        self.financial_paid_button.setEnabled(str(record.get("status") or "") == "open")
        self.financial_cancel_button.setEnabled(str(record.get("status") or "") == "open")
        self.set_financial_form_status("Editando lancamento selecionado.")

    def _request_financial_save(self) -> None:
        description = self.financial_description_input.text().strip()
        if not description:
            self.set_financial_form_status("Informe a descricao.", is_error=True)
            return

        amount = self.financial_amount_input.text().strip().replace(",", ".")
        try:
            if float(amount) <= 0:
                raise ValueError
        except ValueError:
            self.set_financial_form_status("Valor deve ser maior que zero.", is_error=True)
            return

        payload = {
            "record_type": str(self.financial_type_combo.currentData() or "receivable"),
            "description": description,
            "amount": amount,
            "due_date": self._optional_text(self.financial_due_date_input),
            "notes": self._optional_text(self.financial_notes_input),
        }
        self.set_financial_form_status("")
        self.financial_create_requested.emit(payload)

    def _request_financial_mark_paid(self) -> None:
        if not self.selected_financial_record_id:
            self.set_financial_form_status("Selecione um lancamento.", is_error=True)
            return
        self.financial_mark_paid_requested.emit(self.selected_financial_record_id)

    def _request_financial_cancel(self) -> None:
        if not self.selected_financial_record_id:
            self.set_financial_form_status("Selecione um lancamento.", is_error=True)
            return
        self.financial_cancel_requested.emit(self.selected_financial_record_id)

    def _populate_settings_form(self, settings: dict[str, Any]) -> None:
        self.settings_company_name_input.setText(str(settings.get("company_name") or ""))
        self.settings_trade_name_input.setText(str(settings.get("trade_name") or ""))
        self.settings_document_input.setText(str(settings.get("document_number") or ""))
        self.settings_email_input.setText(str(settings.get("email") or ""))
        self.settings_phone_input.setText(str(settings.get("phone") or ""))
        self.settings_brand_name_input.setText(str(settings.get("brand_name") or ""))
        self.settings_brand_subtitle_input.setText(str(settings.get("brand_subtitle") or ""))
        self.settings_primary_color_input.setText(str(settings.get("primary_color") or "#0969da"))
        self._select_combo_value(self.settings_theme_combo, str(settings.get("theme") or "light"))
        self.settings_backup_enabled_checkbox.setChecked(bool(settings.get("backup_enabled", True)))
        self.settings_backup_interval_input.setText(
            str(settings.get("backup_interval_hours") or "24")
        )
        self.settings_backup_path_input.setText(
            str(settings.get("backup_storage_path") or "backups")
        )
        last_run = settings.get("backup_last_run_at")
        self.settings_backup_last_run_label.setText(
            f"Ultimo backup: {last_run}" if last_run else "Ultimo backup: nunca"
        )
        self.settings_full_summary.setPlainText(self._format_settings_summary(settings))
        self.apply_branding(settings)
        self.set_settings_form_status("Configuracoes carregadas.")

    def _request_settings_save(self) -> None:
        company_name = self.settings_company_name_input.text().strip()
        if not company_name:
            self.set_settings_form_status("Informe o nome da empresa.", is_error=True)
            return

        interval_text = self.settings_backup_interval_input.text().strip()
        try:
            backup_interval_hours = int(interval_text)
        except ValueError:
            self.set_settings_form_status("Intervalo de backup deve ser inteiro.", is_error=True)
            return

        if backup_interval_hours < 1 or backup_interval_hours > 720:
            self.set_settings_form_status(
                "Intervalo de backup deve ficar entre 1 e 720 horas.",
                is_error=True,
            )
            return

        backup_storage_path = self.settings_backup_path_input.text().strip()
        if not backup_storage_path:
            self.set_settings_form_status("Informe a pasta de backup.", is_error=True)
            return

        primary_color = self.settings_primary_color_input.text().strip() or "#0969da"
        if not self._is_hex_color(primary_color):
            self.set_settings_form_status(
                "Cor principal deve usar o formato #RRGGBB.",
                is_error=True,
            )
            return

        payload = {
            "company_name": company_name,
            "trade_name": self._optional_text(self.settings_trade_name_input),
            "document_number": self._optional_text(self.settings_document_input),
            "email": self._optional_text(self.settings_email_input),
            "phone": self._optional_text(self.settings_phone_input),
            "brand_name": self._optional_text(self.settings_brand_name_input),
            "brand_subtitle": self._optional_text(self.settings_brand_subtitle_input),
            "primary_color": primary_color,
            "theme": str(self.settings_theme_combo.currentData() or "light"),
            "backup_enabled": self.settings_backup_enabled_checkbox.isChecked(),
            "backup_interval_hours": backup_interval_hours,
            "backup_storage_path": backup_storage_path,
        }
        self.set_settings_form_status("")
        self.settings_update_requested.emit(payload)

    def _request_report_view(self) -> None:
        module_key = str(self.report_module_combo.currentData() or "service_orders")
        self.current_report_module_key = module_key
        self.set_report_status("")
        self.report_view_requested.emit(module_key)

    def _request_report_export(self, report_format: str) -> None:
        module_key = str(self.report_module_combo.currentData() or self.current_report_module_key)
        extension = report_format.lower()
        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio",
            f"{module_key}.{extension}",
            f"{extension.upper()} (*.{extension})",
        )
        if not file_path:
            return

        if not file_path.lower().endswith(f".{extension}"):
            file_path = f"{file_path}.{extension}"

        self.current_report_module_key = module_key
        self.set_report_status("")
        self.report_export_requested.emit(module_key, report_format, file_path)

    def _refresh_service_order_equipment_combo(self) -> None:
        if not hasattr(self, "service_order_equipment_combo"):
            return

        current_equipment_id = self.service_order_equipment_combo.currentData()
        self.service_order_equipment_combo.clear()

        for equipment in self.service_order_equipment:
            label = " - ".join(
                part
                for part in [
                    str(equipment.get("category") or ""),
                    str(equipment.get("brand") or ""),
                    str(equipment.get("model") or ""),
                    str(equipment.get("special_number") or ""),
                    str(equipment.get("serial_number") or ""),
                ]
                if part
            )
            self.service_order_equipment_combo.addItem(
                label or "Equipamento sem descricao", str(equipment["id"])
            )

        if current_equipment_id:
            self._select_combo_value(self.service_order_equipment_combo, str(current_equipment_id))

    @staticmethod
    def _format_value(value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, bool):
            return "Sim" if value else "Nao"

        labels = {
            "open": "Aberta",
            "assigned": "Atribuida",
            "pending_quote": "Pendente de orcamento",
            "quote_sent": "Orcamento enviado",
            "pending_approval": "Pendente de aprovacao",
            "approved": "Aprovada",
            "in_progress": "Em execucao",
            "completed": "Concluida",
            "rejected": "Reprovada",
            "closed": "Encerrada",
            "admin": "Administrador",
            "manager": "Gestor/Lider",
            "technician": "Tecnico",
            "customer": "Cliente",
            "pending": "Pendente",
            "resolved": "Resolvida",
            "service": "Servico",
            "part": "Peca",
            "other": "Outro",
            "light": "Claro",
            "dark": "Escuro",
            "low": "Baixa",
            "normal": "Normal",
            "high": "Alta",
            "urgent": "Urgente",
            "receivable": "A receber",
            "payable": "A pagar",
            "paid": "Pago",
            "canceled": "Cancelado",
            "overdue": "Vencido",
            "email": "Email",
            "whatsapp": "WhatsApp",
            "system": "Sistema",
            "sent": "Enviada",
            "failed": "Falhou",
            "service_orders": "Ordens de Servico",
            "customers": "Clientes",
            "equipment": "Equipamentos",
            "inventory": "Estoque",
            "users": "Usuarios",
            "financial": "Financeiro",
            "audit_logs": "Logs/Auditoria",
        }
        if isinstance(value, str) and value in labels:
            return labels[value]

        return str(value)

    def _format_service_order_budget(self, service_order: dict[str, Any]) -> str:
        items = service_order.get("budget_items") or []
        total = self._format_value(service_order.get("quoted_total"))
        if not items:
            return f"Orcamento: nenhum item. Total: {total or '0'}"

        descriptions = []
        for item in items[:4]:
            item_type = self._format_value(item.get("item_type"))
            quantity = self._format_value(item.get("quantity"))
            unit_price = self._format_value(item.get("unit_price"))
            description = self._format_value(item.get("description"))
            descriptions.append(f"{item_type}: {description} ({quantity} x {unit_price})")

        remaining = len(items) - len(descriptions)
        suffix = f" + {remaining} item(ns)" if remaining > 0 else ""
        return f"Orcamento: {'; '.join(descriptions)}{suffix}. Total: {total}"

    def _format_service_order_documents(self, service_order: dict[str, Any]) -> str:
        documents = service_order.get("documents") or []
        if not documents:
            return "Anexos: nenhum arquivo."

        descriptions = []
        for document in documents[:4]:
            document_type = self._format_value(document.get("document_type"))
            file_name = self._format_value(document.get("file_name"))
            descriptions.append(f"{document_type}: {file_name}")

        remaining = len(documents) - len(descriptions)
        suffix = f" + {remaining} arquivo(s)" if remaining > 0 else ""
        return f"Anexos: {'; '.join(descriptions)}{suffix}."

    def _format_service_order_full_summary(self, service_order: dict[str, Any]) -> str:
        customer_name = self._lookup_label(
            self.service_order_customers,
            service_order.get("customer_id"),
            "name",
            "Cliente nao identificado",
        )
        technician_name = self._lookup_label(
            self.service_order_technicians,
            service_order.get("assigned_technician_id"),
            "full_name",
            "Sem tecnico",
        )
        equipment_label = self._lookup_equipment_label(service_order.get("equipment_id"))
        lines = [
            f"Codigo: {self._format_value(service_order.get('code')) or '-'}",
            f"Status: {self._format_value(service_order.get('status'))}",
            f"Prioridade: {self._format_value(service_order.get('priority')) or 'Normal'}",
            f"Prazo SLA: {self._format_value(service_order.get('sla_due_at')) or '-'}",
            f"Cliente: {customer_name}",
            f"Equipamento: {equipment_label}",
            f"Tecnico: {technician_name}",
            f"Problema informado: {self._format_value(service_order.get('problem_description'))}",
            f"Diagnostico: {self._format_value(service_order.get('technical_diagnosis')) or '-'}",
            f"Total orcado: {self._format_value(service_order.get('quoted_total')) or '0'}",
            f"Criada em: {self._format_value(service_order.get('created_at'))}",
        ]
        return "\n".join(lines)

    def _format_customer_full_summary(self, customer: dict[str, Any]) -> str:
        active = "Sim" if customer.get("is_active", True) else "Nao"
        lines = [
            f"Nome: {self._format_value(customer.get('name')) or '-'}",
            f"Email: {self._format_value(customer.get('email')) or '-'}",
            f"Telefone: {self._format_value(customer.get('phone')) or '-'}",
            f"Endereco: {self._format_value(customer.get('address')) or '-'}",
            f"Ativo: {active}",
            f"Observacoes: {self._format_value(customer.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_full_summary(self, equipment: dict[str, Any]) -> str:
        boards = equipment.get("boards") or []
        components_count = sum(len(board.get("components") or []) for board in boards)
        lines = [
            f"ID: {self._format_value(equipment.get('id')) or '-'}",
            f"Tipo: {self._format_value(equipment.get('category')) or '-'}",
            f"Marca: {self._format_value(equipment.get('brand')) or '-'}",
            f"Modelo: {self._format_value(equipment.get('model')) or '-'}",
            f"N especial: {self._format_value(equipment.get('special_number')) or '-'}",
            f"Serie: {self._format_value(equipment.get('serial_number')) or '-'}",
            f"Valor unitario: R$ {self._format_value(equipment.get('unit_price')) or '0'}",
            f"Placas vinculadas: {len(boards)}",
            f"Componentes cadastrados: {components_count}",
            f"Notas: {self._format_value(equipment.get('description')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_board_summary(self, board: dict[str, Any]) -> str:
        components = board.get("components") or []
        lines = [
            f"ID: {self._format_value(board.get('id')) or '-'}",
            f"Nome: {self._format_value(board.get('name')) or '-'}",
            f"N especial: {self._format_value(board.get('special_number')) or '-'}",
            f"Serie: {self._format_value(board.get('serial_number')) or '-'}",
            f"Modelo / Tipo: {self._format_value(board.get('model')) or '-'}",
            f"Revisao: {self._format_value(board.get('revision')) or '-'}",
            f"Valor unitario: R$ {self._format_value(board.get('unit_price')) or '0'}",
            f"Componentes vinculados: {len(components)}",
            f"Notas: {self._format_value(board.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_equipment_component_summary(self, component: dict[str, Any]) -> str:
        lines = [
            f"ID: {self._format_value(component.get('id')) or '-'}",
            f"Dados: {self._format_value(component.get('name')) or '-'}",
            f"Categoria: {self._format_value(component.get('category')) or '-'}",
            f"Modelo / Part Number: {self._format_value(component.get('part_number')) or '-'}",
            f"Localizacao: {self._format_value(component.get('location')) or '-'}",
            f"Quantidade: {self._format_value(component.get('quantity')) or '-'}",
            f"Valor unitario: R$ {self._format_value(component.get('unit_price')) or '0'}",
            f"Observacoes: {self._format_value(component.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_inventory_full_summary(self, item: dict[str, Any]) -> str:
        quantity = self._format_value(item.get("quantity")) or "0"
        minimum = self._format_value(item.get("minimum_quantity")) or "0"
        unit_cost = self._format_value(item.get("unit_cost")) or "0"
        status = "Critico" if self._inventory_is_low(item) else "Operacional"
        lines = [
            f"SKU: {self._format_value(item.get('sku')) or '-'}",
            f"Nome: {self._format_value(item.get('name')) or '-'}",
            f"Categoria: {self._format_value(item.get('category')) or '-'}",
            f"Quantidade: {quantity}",
            f"Minimo para reposicao: {minimum}",
            f"Custo unitario: {unit_cost}",
            f"Status: {status}",
        ]
        return "\n".join(lines)

    def _format_settings_summary(self, settings: dict[str, Any]) -> str:
        backup_enabled = "Ativo" if settings.get("backup_enabled", True) else "Inativo"
        theme = self._format_value(settings.get("theme")) or str(settings.get("theme") or "light")
        lines = [
            f"Empresa: {self._format_value(settings.get('company_name')) or '-'}",
            f"Nome fantasia: {self._format_value(settings.get('trade_name')) or '-'}",
            f"Nome exibido: {self._format_value(settings.get('brand_name')) or '-'}",
            f"Subtitulo: {self._format_value(settings.get('brand_subtitle')) or '-'}",
            f"Cor principal: {self._format_value(settings.get('primary_color')) or '#0969da'}",
            f"Tema: {theme}",
            f"Backup automatico: {backup_enabled}",
            f"Intervalo de backup: {settings.get('backup_interval_hours') or 24} hora(s)",
            f"Destino: {self._format_value(settings.get('backup_storage_path')) or 'backups'}",
            f"Ultimo backup: {self._format_value(settings.get('backup_last_run_at')) or 'nunca'}",
        ]
        return "\n".join(lines)

    def _format_financial_summary(self, record: dict[str, Any]) -> str:
        lines = [
            f"Descricao: {self._format_value(record.get('description')) or '-'}",
            f"Tipo: {self._format_value(record.get('record_type')) or '-'}",
            f"Status: {self._format_value(record.get('status')) or '-'}",
            f"Valor: {self._format_value(record.get('amount')) or '0'}",
            f"Vencimento: {self._format_value(record.get('due_date')) or '-'}",
            f"Pago em: {self._format_value(record.get('paid_at')) or '-'}",
            f"OS vinculada: {self._format_value(record.get('service_order_id')) or '-'}",
            f"Observacoes: {self._format_value(record.get('notes')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_audit_summary(self, record: dict[str, Any]) -> str:
        actor = self._format_value(record.get("actor_user_id")) or record.get("actor_type") or "-"
        lines = [
            f"Acao: {self._format_value(record.get('action')) or '-'}",
            f"Entidade: {self._format_value(record.get('entity_type')) or '-'}",
            f"ID: {self._format_value(record.get('entity_id')) or '-'}",
            f"Resumo: {self._format_value(record.get('summary')) or '-'}",
            f"Ator: {actor}",
            f"Criado em: {self._format_value(record.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_notification_summary(self, record: dict[str, Any]) -> str:
        lines = [
            f"Canal: {self._format_value(record.get('channel')) or '-'}",
            f"Status: {self._format_value(record.get('status')) or '-'}",
            f"Destinatario: {self._format_value(record.get('recipient')) or '-'}",
            f"Assunto: {self._format_value(record.get('subject')) or '-'}",
            f"Mensagem: {self._format_value(record.get('message')) or '-'}",
            f"OS vinculada: {self._format_value(record.get('service_order_id')) or '-'}",
            f"Criado em: {self._format_value(record.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_sector_summary(self, sector: dict[str, Any]) -> str:
        lines = [
            f"Nome: {self._format_value(sector.get('name')) or '-'}",
            f"Descricao: {self._format_value(sector.get('description')) or '-'}",
            f"Criado em: {self._format_value(sector.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_user_summary(self, user: dict[str, Any]) -> str:
        sector_name = self._lookup_label(
            self.user_sectors,
            user.get("sector_id"),
            "name",
            "Sem setor",
        )
        active = "Ativo" if user.get("is_active", True) else "Inativo"
        must_change = "Sim" if user.get("must_change_password", False) else "Nao"
        lines = [
            f"Nome: {self._format_value(user.get('full_name')) or '-'}",
            f"Email: {self._format_value(user.get('email')) or '-'}",
            f"Perfil: {self._format_value(user.get('role')) or '-'}",
            f"Setor: {sector_name}",
            f"Status: {active}",
            f"Exige troca de senha: {must_change}",
        ]
        return "\n".join(lines)

    def _format_password_reset_summary(self, request: dict[str, Any]) -> str:
        lines = [
            f"Solicitante: {self._format_value(request.get('requester_full_name')) or '-'}",
            f"Email: {self._format_value(request.get('requester_email')) or '-'}",
            f"Perfil: {self._format_value(request.get('requester_role')) or '-'}",
            f"Status: {self._format_value(request.get('status')) or '-'}",
            f"Criada em: {self._format_value(request.get('created_at')) or '-'}",
        ]
        return "\n".join(lines)

    def _format_report_summary(self, report: dict[str, Any]) -> str:
        columns = report.get("columns") or []
        rows = report.get("rows") or []
        column_labels = [
            str(column.get("label") or column.get("key") or "") for column in columns if column
        ]
        lines = [
            f"Titulo: {self._format_value(report.get('title')) or 'Relatorio'}",
            f"Modulo: {self._format_value(report.get('module')) or '-'}",
            f"Registros: {report.get('total_records', len(rows))}",
            f"Colunas: {', '.join(column_labels) if column_labels else '-'}",
            "Formatos disponiveis: CSV, XLSX e PDF",
        ]
        return "\n".join(lines)

    def _inventory_is_low(self, item: dict[str, Any]) -> bool:
        quantity = self._safe_float(item.get("quantity"))
        minimum = self._safe_float(item.get("minimum_quantity"))
        return minimum > 0 and quantity <= minimum

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def _lookup_label(
        self,
        items: list[dict[str, Any]],
        item_id: Any,
        key: str,
        fallback: str,
    ) -> str:
        for item in items:
            if str(item.get("id")) == str(item_id):
                return str(item.get(key) or fallback)
        return fallback

    def _lookup_equipment_label(self, equipment_id: Any) -> str:
        for equipment in self.service_order_equipment:
            if str(equipment.get("id")) != str(equipment_id):
                continue
            parts = [
                str(equipment.get("category") or ""),
                str(equipment.get("brand") or ""),
                str(equipment.get("model") or ""),
                str(equipment.get("special_number") or ""),
                str(equipment.get("serial_number") or ""),
            ]
            return " - ".join(part for part in parts if part) or "Equipamento sem descricao"
        return "Equipamento nao identificado"

    @staticmethod
    def _optional_text(input_widget: QLineEdit) -> str | None:
        value = input_widget.text().strip()
        return value or None

    @staticmethod
    def _is_complete_phone(value: str) -> bool:
        digits = "".join(character for character in value if character.isdigit())
        return "_" not in value and len(digits) == 11

    @staticmethod
    def _is_hex_color(value: str) -> bool:
        if len(value) != 7 or not value.startswith("#"):
            return False
        return all(character in "0123456789abcdefABCDEF" for character in value[1:])

    @staticmethod
    def _select_combo_value(combo: QComboBox, value: str) -> None:
        for index in range(combo.count()):
            if str(combo.itemData(index)) == value:
                combo.setCurrentIndex(index)
                return

    def _decimal_text(self, input_widget: QLineEdit, label: str) -> str | None:
        value = input_widget.text().strip().replace(",", ".")
        if not value:
            value = "0"

        try:
            numeric_value = float(value)
        except ValueError:
            self.set_inventory_form_status(f"{label} deve ser numerico.", is_error=True)
            return None

        if numeric_value < 0:
            self.set_inventory_form_status(f"{label} nao pode ser negativo.", is_error=True)
            return None

        return value

    def _decimal_text_for_service_order(
        self,
        input_widget: QLineEdit,
        label: str,
        allow_zero: bool,
    ) -> str | None:
        value = input_widget.text().strip().replace(",", ".")
        if not value:
            value = "0"

        try:
            numeric_value = float(value)
        except ValueError:
            self.set_service_order_form_status(f"{label} deve ser numerico.", is_error=True)
            return None

        if numeric_value < 0 or (numeric_value == 0 and not allow_zero):
            self.set_service_order_form_status(f"{label} deve ser maior que zero.", is_error=True)
            return None

        return value
