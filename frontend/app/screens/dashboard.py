from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DashboardWindow(QWidget):
    logout_requested = Signal()
    module_selected = Signal(str)
    refresh_requested = Signal()
    customer_create_requested = Signal(dict)
    customer_update_requested = Signal(str, dict)
    equipment_create_requested = Signal(dict)
    equipment_update_requested = Signal(str, dict)
    inventory_create_requested = Signal(dict)
    inventory_update_requested = Signal(str, dict)
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
    settings_update_requested = Signal(dict)
    backup_run_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.active_module_key = "service_orders"
        self.current_rows: list[dict[str, Any]] = []
        self.selected_customer_id: str | None = None
        self.selected_equipment_id: str | None = None
        self.selected_inventory_item_id: str | None = None
        self.selected_service_order_id: str | None = None
        self.selected_user_id: str | None = None
        self.selected_service_order_document_path: str | None = None
        self.equipment_customers: list[dict[str, Any]] = []
        self.service_order_customers: list[dict[str, Any]] = []
        self.service_order_equipment: list[dict[str, Any]] = []
        self.service_order_technicians: list[dict[str, Any]] = []

        self.setWindowTitle("PRO CORE - Dashboard")
        self.setMinimumSize(1120, 720)
        self.setObjectName("dashboardWindow")

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(236)

        sidebar_title = QLabel("PRO CORE")
        sidebar_title.setObjectName("sidebarTitle")

        sidebar_text = QLabel("Assistencia tecnica")
        sidebar_text.setObjectName("sidebarText")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 24, 20, 24)
        sidebar_layout.setSpacing(12)
        sidebar_layout.addWidget(sidebar_title)
        sidebar_layout.addWidget(sidebar_text)
        sidebar_layout.addSpacing(28)

        self.module_buttons: dict[str, QPushButton] = {}
        modules = {
            "service_orders": "Ordens de Servico",
            "customers": "Clientes",
            "equipment": "Equipamentos",
            "inventory": "Estoque",
            "users": "Usuarios",
            "settings": "Configuracoes",
        }

        for module_key, label in modules.items():
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.clicked.connect(lambda checked=False, key=module_key: self.module_selected.emit(key))
            self.module_buttons[module_key] = button
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        self.logout_button = QPushButton("Sair")
        self.logout_button.setObjectName("secondaryButton")
        self.logout_button.clicked.connect(self.logout_requested.emit)
        sidebar_layout.addWidget(self.logout_button)

        content = QFrame()
        content.setObjectName("contentPanel")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 28, 28, 28)
        content_layout.setSpacing(20)

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

        header_layout = QHBoxLayout()
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        section_title = QLabel("Modulos do MVP")
        section_title.setObjectName("sectionTitle")

        grid = QGridLayout()
        grid.setSpacing(14)
        modules = [
            ("Ordens de Servico", "Criacao, diagnostico, orcamento e execucao."),
            ("Clientes", "Cadastro e consulta de clientes da empresa."),
            ("Equipamentos", "Equipamentos vinculados aos clientes."),
            ("Estoque", "Itens, pecas, quantidades e custo base."),
            ("Configuracoes", "Preferencias e parametros operacionais."),
            ("Area Administrativa", "Usuarios, setores e governanca do sistema."),
        ]

        for index, (title, description) in enumerate(modules):
            grid.addWidget(self._build_module_card(title, description), index // 2, index % 2)

        self.data_title = QLabel("Dados")
        self.data_title.setObjectName("sectionTitle")

        self.empty_label = QLabel("Selecione um modulo para carregar dados.")
        self.empty_label.setObjectName("mutedText")

        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self._handle_table_selection)

        self.customer_form_panel = self._build_customer_form()
        self.customer_form_panel.hide()
        self.equipment_form_panel = self._build_equipment_form()
        self.equipment_form_panel.hide()
        self.inventory_form_panel = self._build_inventory_form()
        self.inventory_form_panel.hide()
        self.service_order_form_panel = self._build_service_order_form()
        self.service_order_form_panel.hide()
        self.user_form_panel = self._build_user_form()
        self.user_form_panel.hide()
        self.settings_form_panel = self._build_settings_form()
        self.settings_form_panel.hide()

        content_layout.addLayout(header_layout)
        content_layout.addWidget(section_title)
        content_layout.addLayout(grid)
        content_layout.addWidget(self.data_title)
        content_layout.addWidget(self.empty_label)
        content_layout.addWidget(self.table)
        content_layout.addWidget(self.customer_form_panel)
        content_layout.addWidget(self.equipment_form_panel)
        content_layout.addWidget(self.inventory_form_panel)
        content_layout.addWidget(self.service_order_form_panel)
        content_layout.addWidget(self.user_form_panel)
        content_layout.addWidget(self.settings_form_panel)
        content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(content)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addWidget(scroll_area)

    def set_user(self, user: dict[str, Any]) -> None:
        role_key = str(user.get("role", ""))
        role = role_key.replace("_", " ").title()
        full_name = user.get("full_name", "Usuario")
        email = user.get("email", "")
        self.user_label.setText(f"{full_name} | {email} | Perfil: {role}")
        if "users" in self.module_buttons:
            self.module_buttons["users"].setVisible(role_key in {"admin", "manager"})
        if "settings" in self.module_buttons:
            self.module_buttons["settings"].setVisible(role_key == "admin")

    def render_loading(self, title: str, module_key: str) -> None:
        self._set_active_module(module_key)
        self.data_title.setText(title)
        self.empty_label.setText("Carregando dados...")
        self.empty_label.show()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def render_error(self, title: str, message: str, module_key: str) -> None:
        self._set_active_module(module_key)
        self.data_title.setText(title)
        self.empty_label.setText(message)
        self.empty_label.show()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def render_rows(
        self,
        title: str,
        rows: list[dict[str, Any]],
        columns: list[tuple[str, str]],
        module_key: str,
    ) -> None:
        self._set_active_module(module_key)
        self.current_rows = rows
        self.data_title.setText(title)
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for label, _key in columns])
        self.table.setRowCount(len(rows))

        if not rows:
            self.empty_label.setText("Nenhum registro encontrado.")
            self.empty_label.show()
            return

        self.empty_label.hide()
        for row_index, row in enumerate(rows):
            for column_index, (_label, key) in enumerate(columns):
                value = self._format_value(row.get(key))
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)

        if module_key == "customers":
            self.table.selectRow(0)
        elif module_key == "equipment":
            self.table.selectRow(0)
        elif module_key == "inventory":
            self.table.selectRow(0)
        elif module_key == "service_orders":
            self.table.selectRow(0)
        elif module_key == "users":
            self.table.selectRow(0)

    def render_settings(self, settings: dict[str, Any]) -> None:
        self._set_active_module("settings")
        self.current_rows = []
        self.data_title.setText("Configuracoes")
        self.empty_label.hide()
        self.table.hide()
        self._populate_settings_form(settings)

    @staticmethod
    def _build_module_card(title: str, description: str) -> QFrame:
        card = QFrame()
        card.setObjectName("moduleCard")
        card.setMinimumHeight(112)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        description_label = QLabel(description)
        description_label.setObjectName("cardMeta")
        description_label.setWordWrap(True)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return card

    def _build_customer_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("Cadastro de cliente")
        title.setObjectName("sectionTitle")

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Nome")

        self.customer_document_input = QLineEdit()
        self.customer_document_input.setPlaceholderText("Documento")

        self.customer_email_input = QLineEdit()
        self.customer_email_input.setPlaceholderText("Email")

        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText("Telefone")

        self.customer_address_input = QLineEdit()
        self.customer_address_input.setPlaceholderText("Endereco")

        self.customer_notes_input = QLineEdit()
        self.customer_notes_input.setPlaceholderText("Observacoes")

        self.customer_active_checkbox = QCheckBox("Cliente ativo")
        self.customer_active_checkbox.setChecked(True)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Nome", self.customer_name_input)
        form_layout.addRow("Documento", self.customer_document_input)
        form_layout.addRow("Email", self.customer_email_input)
        form_layout.addRow("Telefone", self.customer_phone_input)
        form_layout.addRow("Endereco", self.customer_address_input)
        form_layout.addRow("Observacoes", self.customer_notes_input)
        form_layout.addRow("", self.customer_active_checkbox)

        self.customer_form_status = QLabel("")
        self.customer_form_status.setObjectName("mutedText")

        self.customer_new_button = QPushButton("Novo")
        self.customer_new_button.setObjectName("secondaryButton")
        self.customer_new_button.clicked.connect(self.clear_customer_form)

        self.customer_save_button = QPushButton("Salvar cliente")
        self.customer_save_button.clicked.connect(self._request_customer_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.customer_new_button)
        actions.addWidget(self.customer_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.customer_form_status)
        layout.addLayout(actions)

        return panel

    def _build_equipment_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("Cadastro de equipamento")
        title.setObjectName("sectionTitle")

        self.equipment_customer_combo = QComboBox()

        self.equipment_category_input = QLineEdit()
        self.equipment_category_input.setPlaceholderText("Categoria")

        self.equipment_brand_input = QLineEdit()
        self.equipment_brand_input.setPlaceholderText("Marca")

        self.equipment_model_input = QLineEdit()
        self.equipment_model_input.setPlaceholderText("Modelo")

        self.equipment_serial_input = QLineEdit()
        self.equipment_serial_input.setPlaceholderText("Numero de serie")

        self.equipment_description_input = QLineEdit()
        self.equipment_description_input.setPlaceholderText("Descricao")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Cliente", self.equipment_customer_combo)
        form_layout.addRow("Categoria", self.equipment_category_input)
        form_layout.addRow("Marca", self.equipment_brand_input)
        form_layout.addRow("Modelo", self.equipment_model_input)
        form_layout.addRow("Serie", self.equipment_serial_input)
        form_layout.addRow("Descricao", self.equipment_description_input)

        self.equipment_form_status = QLabel("")
        self.equipment_form_status.setObjectName("mutedText")

        self.equipment_new_button = QPushButton("Novo")
        self.equipment_new_button.setObjectName("secondaryButton")
        self.equipment_new_button.clicked.connect(self.clear_equipment_form)

        self.equipment_save_button = QPushButton("Salvar equipamento")
        self.equipment_save_button.clicked.connect(self._request_equipment_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.equipment_new_button)
        actions.addWidget(self.equipment_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addWidget(self.equipment_form_status)
        layout.addLayout(actions)

        return panel

    def _build_inventory_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("Cadastro de item de estoque")
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
        layout.addLayout(form_layout)
        layout.addWidget(self.inventory_form_status)
        layout.addLayout(actions)

        return panel

    def _build_service_order_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("Cadastro de ordem de servico")
        title.setObjectName("sectionTitle")

        self.service_order_customer_combo = QComboBox()
        self.service_order_customer_combo.currentIndexChanged.connect(
            self._refresh_service_order_equipment_combo
        )

        self.service_order_equipment_combo = QComboBox()
        self.service_order_technician_combo = QComboBox()

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

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Cliente", self.service_order_customer_combo)
        form_layout.addRow("Equipamento", self.service_order_equipment_combo)
        form_layout.addRow("Tecnico", self.service_order_technician_combo)
        form_layout.addRow("Problema", self.service_order_problem_input)
        form_layout.addRow("Diagnostico", self.service_order_diagnosis_input)
        form_layout.addRow("Observacao", self.service_order_rejection_input)
        form_layout.addRow("Tipo do item", self.service_order_budget_type_combo)
        form_layout.addRow("Item", self.service_order_budget_description_input)
        form_layout.addRow("Quantidade", self.service_order_budget_quantity_input)
        form_layout.addRow("Valor unitario", self.service_order_budget_unit_price_input)
        form_layout.addRow("Tipo do anexo", self.service_order_document_type_combo)
        form_layout.addRow("Arquivo", self.service_order_document_path_input)

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
        self.service_order_add_budget_button.clicked.connect(self._request_service_order_budget_item)

        self.service_order_submit_quote_button = QPushButton("Enviar orcamento")
        self.service_order_submit_quote_button.setObjectName("secondaryButton")
        self.service_order_submit_quote_button.clicked.connect(self._request_service_order_submit_quote)

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
        self.service_order_select_document_button.clicked.connect(self._select_service_order_document)

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
        layout.addLayout(form_layout)
        layout.addWidget(self.service_order_current_status)
        layout.addWidget(self.service_order_budget_summary)
        layout.addWidget(self.service_order_documents_summary)
        layout.addWidget(self.service_order_form_status)
        layout.addLayout(actions)
        layout.addLayout(flow_actions)
        layout.addLayout(document_actions)

        return panel

    def _build_user_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("Gestao de usuarios")
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

        self.user_initial_password_input = QLineEdit()
        self.user_initial_password_input.setPlaceholderText("Senha inicial")
        self.user_initial_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.user_active_checkbox = QCheckBox("Usuario ativo")
        self.user_active_checkbox.setChecked(True)

        self.user_reset_password_input = QLineEdit()
        self.user_reset_password_input.setPlaceholderText("Nova senha")
        self.user_reset_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Nome", self.user_full_name_input)
        form_layout.addRow("Email", self.user_email_input)
        form_layout.addRow("Perfil", self.user_role_combo)
        form_layout.addRow("Senha inicial", self.user_initial_password_input)
        form_layout.addRow("", self.user_active_checkbox)
        form_layout.addRow("Redefinir senha", self.user_reset_password_input)

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
        layout.addLayout(form_layout)
        layout.addWidget(self.user_form_status)
        layout.addLayout(actions)

        return panel

    def _build_settings_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("Configuracoes do sistema")
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

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Empresa", self.settings_company_name_input)
        form_layout.addRow("Nome fantasia", self.settings_trade_name_input)
        form_layout.addRow("Documento", self.settings_document_input)
        form_layout.addRow("Email", self.settings_email_input)
        form_layout.addRow("Telefone", self.settings_phone_input)
        form_layout.addRow("Tema", self.settings_theme_combo)
        form_layout.addRow("", self.settings_backup_enabled_checkbox)
        form_layout.addRow("Intervalo", self.settings_backup_interval_input)
        form_layout.addRow("Destino", self.settings_backup_path_input)

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
        layout.addLayout(form_layout)
        layout.addWidget(self.settings_backup_last_run_label)
        layout.addWidget(self.settings_form_status)
        layout.addLayout(actions)

        return panel

    def clear_customer_form(self) -> None:
        self.selected_customer_id = None
        self.customer_name_input.clear()
        self.customer_document_input.clear()
        self.customer_email_input.clear()
        self.customer_phone_input.clear()
        self.customer_address_input.clear()
        self.customer_notes_input.clear()
        self.customer_active_checkbox.setChecked(True)
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

    def set_equipment_customers(self, customers: list[dict[str, Any]]) -> None:
        current_customer_id = self.equipment_customer_combo.currentData()
        self.equipment_customers = customers
        self.equipment_customer_combo.clear()

        for customer in customers:
            self.equipment_customer_combo.addItem(
                str(customer.get("name") or "Cliente sem nome"),
                str(customer["id"]),
            )

        if current_customer_id:
            self._select_equipment_customer(str(current_customer_id))

        if not customers:
            self.set_equipment_form_status("Cadastre um cliente antes do equipamento.", is_error=True)

    def clear_equipment_form(self) -> None:
        self.selected_equipment_id = None
        if self.equipment_customer_combo.count() > 0:
            self.equipment_customer_combo.setCurrentIndex(0)
        self.equipment_category_input.clear()
        self.equipment_brand_input.clear()
        self.equipment_model_input.clear()
        self.equipment_serial_input.clear()
        self.equipment_description_input.clear()
        self.equipment_form_status.setText("Novo equipamento.")
        self.table.clearSelection()

    def set_equipment_form_status(self, message: str, is_error: bool = False) -> None:
        self.equipment_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.equipment_form_status.setText(message)
        self.equipment_form_status.style().unpolish(self.equipment_form_status)
        self.equipment_form_status.style().polish(self.equipment_form_status)

    def set_equipment_form_loading(self, is_loading: bool) -> None:
        self.equipment_save_button.setEnabled(not is_loading)
        self.equipment_new_button.setEnabled(not is_loading)
        self.equipment_save_button.setText("Salvando..." if is_loading else "Salvar equipamento")

    def clear_inventory_form(self) -> None:
        self.selected_inventory_item_id = None
        self.inventory_sku_input.clear()
        self.inventory_name_input.clear()
        self.inventory_category_input.clear()
        self.inventory_quantity_input.setText("0")
        self.inventory_minimum_quantity_input.setText("0")
        self.inventory_unit_cost_input.setText("0")
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
            self._select_combo_value(self.service_order_technician_combo, str(current_technician_id))

        self._refresh_service_order_equipment_combo()

        if not customers:
            self.set_service_order_form_status("Cadastre um cliente antes da OS.", is_error=True)
        elif not equipment:
            self.set_service_order_form_status("Cadastre um equipamento antes da OS.", is_error=True)

    def clear_service_order_form(self) -> None:
        self.selected_service_order_id = None
        if self.service_order_customer_combo.count() > 0:
            self.service_order_customer_combo.setCurrentIndex(0)
        if self.service_order_technician_combo.count() > 0:
            self.service_order_technician_combo.setCurrentIndex(0)
        self._refresh_service_order_equipment_combo()
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
        self._set_service_order_flow_buttons_enabled(not is_loading and bool(self.selected_service_order_id))

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

    def clear_user_form(self) -> None:
        self.selected_user_id = None
        self.user_full_name_input.clear()
        self.user_email_input.clear()
        if self.user_role_combo.count() > 0:
            self.user_role_combo.setCurrentIndex(2)
        self.user_initial_password_input.clear()
        self.user_initial_password_input.setEnabled(True)
        self.user_active_checkbox.setChecked(True)
        self.user_reset_password_input.clear()
        self.user_reset_password_input.setEnabled(False)
        self.user_reset_password_button.setEnabled(False)
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
        self.user_reset_password_button.setEnabled(
            not is_loading and bool(self.selected_user_id)
        )
        self.user_save_button.setText("Salvando..." if is_loading else "Salvar usuario")

    def set_user_password_reset_loading(self, is_loading: bool) -> None:
        self.user_reset_password_button.setEnabled(
            not is_loading and bool(self.selected_user_id)
        )
        self.user_save_button.setEnabled(not is_loading)
        self.user_new_button.setEnabled(not is_loading)
        self.user_reset_password_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )

    def clear_settings_form(self) -> None:
        self.settings_company_name_input.clear()
        self.settings_trade_name_input.clear()
        self.settings_document_input.clear()
        self.settings_email_input.clear()
        self.settings_phone_input.clear()
        if self.settings_theme_combo.count() > 0:
            self.settings_theme_combo.setCurrentIndex(0)
        self.settings_backup_enabled_checkbox.setChecked(True)
        self.settings_backup_interval_input.setText("24")
        self.settings_backup_path_input.setText("backups")
        self.settings_backup_last_run_label.setText("Ultimo backup: nunca")
        self.settings_form_status.setText("")

    def set_settings_form_status(self, message: str, is_error: bool = False) -> None:
        self.settings_form_status.setObjectName("errorText" if is_error else "mutedText")
        self.settings_form_status.setText(message)
        self.settings_form_status.style().unpolish(self.settings_form_status)
        self.settings_form_status.style().polish(self.settings_form_status)

    def set_settings_form_loading(self, is_loading: bool) -> None:
        self.settings_save_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setEnabled(not is_loading)
        self.settings_save_button.setText(
            "Salvando..." if is_loading else "Salvar configuracoes"
        )

    def set_backup_run_loading(self, is_loading: bool) -> None:
        self.settings_save_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setEnabled(not is_loading)
        self.settings_run_backup_button.setText(
            "Executando..." if is_loading else "Executar backup agora"
        )

    def _set_active_module(self, module_key: str) -> None:
        self.active_module_key = module_key
        self.current_rows = []
        self.table.show()
        self.customer_form_panel.setVisible(module_key == "customers")
        self.equipment_form_panel.setVisible(module_key == "equipment")
        self.inventory_form_panel.setVisible(module_key == "inventory")
        self.service_order_form_panel.setVisible(module_key == "service_orders")
        self.user_form_panel.setVisible(module_key == "users")
        self.settings_form_panel.setVisible(module_key == "settings")
        if module_key == "customers":
            self.clear_customer_form()
        elif module_key == "equipment":
            self.clear_equipment_form()
        elif module_key == "inventory":
            self.clear_inventory_form()
        elif module_key == "service_orders":
            self.clear_service_order_form()
        elif module_key == "users":
            self.clear_user_form()
        elif module_key == "settings":
            self.clear_settings_form()

    def _handle_table_selection(self) -> None:
        if self.active_module_key not in {
            "customers",
            "equipment",
            "inventory",
            "service_orders",
            "users",
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

        self._populate_user_form(self.current_rows[row_index])

    def _populate_customer_form(self, customer: dict[str, Any]) -> None:
        self.selected_customer_id = str(customer["id"])
        self.customer_name_input.setText(str(customer.get("name") or ""))
        self.customer_document_input.setText(str(customer.get("document_number") or ""))
        self.customer_email_input.setText(str(customer.get("email") or ""))
        self.customer_phone_input.setText(str(customer.get("phone") or ""))
        self.customer_address_input.setText(str(customer.get("address") or ""))
        self.customer_notes_input.setText(str(customer.get("notes") or ""))
        self.customer_active_checkbox.setChecked(bool(customer.get("is_active", True)))
        self.set_customer_form_status("Editando cliente selecionado.")

    def _request_customer_save(self) -> None:
        name = self.customer_name_input.text().strip()
        if not name:
            self.set_customer_form_status("Informe o nome do cliente.", is_error=True)
            return

        payload = {
            "name": name,
            "document_number": self._optional_text(self.customer_document_input),
            "email": self._optional_text(self.customer_email_input),
            "phone": self._optional_text(self.customer_phone_input),
            "address": self._optional_text(self.customer_address_input),
            "notes": self._optional_text(self.customer_notes_input),
            "is_active": self.customer_active_checkbox.isChecked(),
        }

        self.set_customer_form_status("")
        if self.selected_customer_id:
            self.customer_update_requested.emit(self.selected_customer_id, payload)
            return

        self.customer_create_requested.emit(payload)

    def _populate_equipment_form(self, equipment: dict[str, Any]) -> None:
        self.selected_equipment_id = str(equipment["id"])
        self._select_equipment_customer(str(equipment.get("customer_id") or ""))
        self.equipment_category_input.setText(str(equipment.get("category") or ""))
        self.equipment_brand_input.setText(str(equipment.get("brand") or ""))
        self.equipment_model_input.setText(str(equipment.get("model") or ""))
        self.equipment_serial_input.setText(str(equipment.get("serial_number") or ""))
        self.equipment_description_input.setText(str(equipment.get("description") or ""))
        self.set_equipment_form_status("Editando equipamento selecionado.")

    def _request_equipment_save(self) -> None:
        customer_id = self.equipment_customer_combo.currentData()
        category = self.equipment_category_input.text().strip()

        if not customer_id:
            self.set_equipment_form_status("Selecione um cliente.", is_error=True)
            return

        if not category:
            self.set_equipment_form_status("Informe a categoria do equipamento.", is_error=True)
            return

        payload = {
            "customer_id": str(customer_id),
            "category": category,
            "brand": self._optional_text(self.equipment_brand_input),
            "model": self._optional_text(self.equipment_model_input),
            "serial_number": self._optional_text(self.equipment_serial_input),
            "description": self._optional_text(self.equipment_description_input),
        }

        self.set_equipment_form_status("")
        if self.selected_equipment_id:
            self.equipment_update_requested.emit(self.selected_equipment_id, payload)
            return

        self.equipment_create_requested.emit(payload)

    def _select_equipment_customer(self, customer_id: str) -> None:
        if not customer_id:
            return

        for index in range(self.equipment_customer_combo.count()):
            if self.equipment_customer_combo.itemData(index) == customer_id:
                self.equipment_customer_combo.setCurrentIndex(index)
                return

    def _populate_inventory_form(self, item: dict[str, Any]) -> None:
        self.selected_inventory_item_id = str(item["id"])
        self.inventory_sku_input.setText(str(item.get("sku") or ""))
        self.inventory_name_input.setText(str(item.get("name") or ""))
        self.inventory_category_input.setText(str(item.get("category") or ""))
        self.inventory_quantity_input.setText(str(item.get("quantity") or "0"))
        self.inventory_minimum_quantity_input.setText(str(item.get("minimum_quantity") or "0"))
        self.inventory_unit_cost_input.setText(str(item.get("unit_cost") or "0"))
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
        self.service_order_problem_input.setText(str(service_order.get("problem_description") or ""))
        self.service_order_diagnosis_input.setText(str(service_order.get("technical_diagnosis") or ""))
        self.service_order_rejection_input.setText(str(service_order.get("rejection_reason") or ""))
        self.service_order_budget_description_input.clear()
        self.service_order_budget_quantity_input.setText("1")
        self.service_order_budget_unit_price_input.setText("0")
        self.selected_service_order_document_path = None
        self.service_order_document_path_input.clear()
        self.service_order_current_status.setText(
            f"Status: {self._format_value(service_order.get('status'))}"
        )
        self.service_order_budget_summary.setText(self._format_service_order_budget(service_order))
        self.service_order_documents_summary.setText(self._format_service_order_documents(service_order))
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

    def _populate_user_form(self, user: dict[str, Any]) -> None:
        self.selected_user_id = str(user["id"])
        self.user_full_name_input.setText(str(user.get("full_name") or ""))
        self.user_email_input.setText(str(user.get("email") or ""))
        self._select_combo_value(self.user_role_combo, str(user.get("role") or "technician"))
        self.user_initial_password_input.clear()
        self.user_initial_password_input.setEnabled(False)
        self.user_active_checkbox.setChecked(bool(user.get("is_active", True)))
        self.user_reset_password_input.clear()
        self.user_reset_password_input.setEnabled(True)
        self.user_reset_password_button.setEnabled(True)
        self.set_user_form_status("Editando usuario selecionado.")

    def _request_user_save(self) -> None:
        full_name = self.user_full_name_input.text().strip()
        email = self.user_email_input.text().strip().lower()
        role = self.user_role_combo.currentData()

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
            "sector_id": None,
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

    def _populate_settings_form(self, settings: dict[str, Any]) -> None:
        self.settings_company_name_input.setText(str(settings.get("company_name") or ""))
        self.settings_trade_name_input.setText(str(settings.get("trade_name") or ""))
        self.settings_document_input.setText(str(settings.get("document_number") or ""))
        self.settings_email_input.setText(str(settings.get("email") or ""))
        self.settings_phone_input.setText(str(settings.get("phone") or ""))
        self._select_combo_value(self.settings_theme_combo, str(settings.get("theme") or "light"))
        self.settings_backup_enabled_checkbox.setChecked(bool(settings.get("backup_enabled", True)))
        self.settings_backup_interval_input.setText(
            str(settings.get("backup_interval_hours") or "24")
        )
        self.settings_backup_path_input.setText(str(settings.get("backup_storage_path") or "backups"))
        last_run = settings.get("backup_last_run_at")
        self.settings_backup_last_run_label.setText(
            f"Ultimo backup: {last_run}" if last_run else "Ultimo backup: nunca"
        )
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

        payload = {
            "company_name": company_name,
            "trade_name": self._optional_text(self.settings_trade_name_input),
            "document_number": self._optional_text(self.settings_document_input),
            "email": self._optional_text(self.settings_email_input),
            "phone": self._optional_text(self.settings_phone_input),
            "theme": str(self.settings_theme_combo.currentData() or "light"),
            "backup_enabled": self.settings_backup_enabled_checkbox.isChecked(),
            "backup_interval_hours": backup_interval_hours,
            "backup_storage_path": backup_storage_path,
        }
        self.set_settings_form_status("")
        self.settings_update_requested.emit(payload)

    def _refresh_service_order_equipment_combo(self) -> None:
        if not hasattr(self, "service_order_equipment_combo"):
            return

        current_equipment_id = self.service_order_equipment_combo.currentData()
        customer_id = self.service_order_customer_combo.currentData()
        self.service_order_equipment_combo.clear()

        if not customer_id:
            return

        for equipment in self.service_order_equipment:
            if str(equipment.get("customer_id")) != str(customer_id):
                continue

            label = " - ".join(
                part
                for part in [
                    str(equipment.get("category") or ""),
                    str(equipment.get("brand") or ""),
                    str(equipment.get("model") or ""),
                    str(equipment.get("serial_number") or ""),
                ]
                if part
            )
            self.service_order_equipment_combo.addItem(label or "Equipamento sem descricao", str(equipment["id"]))

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
            "service": "Servico",
            "part": "Peca",
            "other": "Outro",
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

    @staticmethod
    def _optional_text(input_widget: QLineEdit) -> str | None:
        value = input_widget.text().strip()
        return value or None

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
