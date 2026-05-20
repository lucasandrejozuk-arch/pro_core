# ruff: noqa: F401, F821, E501
from __future__ import annotations

import math
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QResizeEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.display import DisplayProfile, detect_display_profile
from frontend.app.core.grid import GRID_COLUMNS, add_layout, add_widget, create_grid, span_for_items
from frontend.app.core.icons import build_icon
from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
)
from frontend.app.themes.styles import COLOR_PALETTE_OPTIONS, DEFAULT_COLOR_PALETTE
from frontend.app.widgets import DashboardKpiCard, create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin2:
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
            empty_message = QLabel("Nenhum aviso no momento")
            empty_message.setObjectName("emptyAlertText")
            empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dashboard_alerts_layout.addStretch()
            self.dashboard_alerts_layout.addWidget(empty_message)
            self.dashboard_alerts_layout.addStretch()
            return

        for alert in alerts:
            row = QFrame()
            row.setObjectName("dashboardAlertRow")
            row.setProperty("level", str(alert.get("level") or "info"))
            message = QLabel(str(alert.get("message") or "Alerta operacional."))
            message.setWordWrap(True)
            layout = QHBoxLayout(row)
            layout.setContentsMargins(8, 4, 8, 4)
            layout.addWidget(message)
            self.dashboard_alerts_layout.addWidget(row)
        self.dashboard_alerts_layout.addStretch()

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _render_bar_chart(self, layout: QVBoxLayout, values: dict[str, float]) -> None:
        self._clear_layout(layout)
        if not values:
            empty = QLabel("Sem dados para grafico.")
            empty.setObjectName("mutedText")
            layout.addWidget(empty)
            return
        maximum = max(max(values.values()), 1)
        for label, value in values.items():
            row = QHBoxLayout()
            name = QLabel(label)
            name.setObjectName("mutedText")
            name.setMinimumWidth(120)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(round((value / maximum) * 100))
            bar.setFormat(f"{self._format_number(value)}")
            row.addWidget(name)
            row.addWidget(bar, 1)
            layout.addLayout(row)

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

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, identity_panel, 0, 0, 6)
        add_widget(fields_layout, contact_panel, 0, 6, 6)

        self.customer_form_status = QLabel("")
        self.customer_form_status.setObjectName("mutedText")

        self.customer_new_button = QPushButton("Novo")
        self.customer_new_button.setObjectName("secondaryButton")
        self.customer_new_button.clicked.connect(self.clear_customer_form)

        self.customer_delete_button = QPushButton("Excluir")
        self.customer_delete_button.setObjectName("dangerButton")
        self.customer_delete_button.setEnabled(False)
        self.customer_delete_button.clicked.connect(self._request_customer_delete)

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
        actions.addWidget(self.customer_delete_button)
        actions.addWidget(self.customer_save_button)

        document_actions = QHBoxLayout()
        document_actions.addWidget(self.customer_document_path_input, 1)
        document_actions.addWidget(self.customer_select_document_button)
        document_actions.addWidget(self.customer_upload_document_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
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
        self.equipment_import_button = QPushButton("Importar CSV")
        self.equipment_import_button.setObjectName("secondaryButton")
        self.equipment_import_button.clicked.connect(self._request_equipment_import)
        self.equipment_export_csv_button = QPushButton("Exportar CSV")
        self.equipment_export_csv_button.setObjectName("secondaryButton")
        self.equipment_export_csv_button.clicked.connect(
            lambda: self._request_equipment_export("csv")
        )
        self.equipment_export_pdf_button = QPushButton("Exportar PDF")
        self.equipment_export_pdf_button.setObjectName("secondaryButton")
        self.equipment_export_pdf_button.clicked.connect(
            lambda: self._request_equipment_export("pdf")
        )
        self.equipment_defect_cases_button = QPushButton("Casos de Defeito")
        self.equipment_defect_cases_button.setObjectName("secondaryButton")
        self.equipment_defect_cases_button.clicked.connect(
            self._request_equipment_defect_cases_open
        )

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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
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
                    self.equipment_import_button,
                    self.equipment_export_csv_button,
                    self.equipment_export_pdf_button,
                    self.equipment_defect_cases_button,
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

        grid_layout = create_grid(spacing=10)
        add_layout(grid_layout, table_layout, 0, 0, 7)
        add_layout(grid_layout, details_layout, 0, 7, 5)

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
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda position, source_table=table: self._open_equipment_table_context_menu(
                source_table,
                position,
            )
        )
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setMinimumHeight(minimum_height)
        table.viewport().installEventFilter(self)

    def _build_tools_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("CALCULADORAS ELETRICAS")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tools_tabs = QTabWidget()
        self.tools_tabs.setObjectName("toolsTabs")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.tools_tabs, 1)
        return panel

    def render_tools(self, tools: list[dict[str, Any]]) -> None:
        self._set_active_module("tools")
        self.current_tools = list(tools)
        self.tools_tabs.clear()
        tool_ids = {str(tool.get("id") or "") for tool in tools}
        if not tool_ids:
            self.tools_tabs.addTab(
                self._build_tool_message("Nenhuma ferramenta disponivel."),
                "Aviso",
            )
            return
        tools_by_specialty = self._group_tools_by_specialty(tool_ids)
        for specialty_name, specialty_tools in tools_by_specialty.items():
            tab_widget = self._build_specialty_tab(specialty_name, specialty_tools)
            self.tools_tabs.addTab(tab_widget, specialty_name)

    def _group_tools_by_specialty(
        self, tool_ids: set[str]
    ) -> dict[str, list[tuple[str, str, Any, list[tuple[str, str]]]]]:
        specialty_map = {
            "eletrica": [
                ("ohm", "Lei de Ohm", self._calculate_ohm_tool, []),
                (
                    "power",
                    "Potencia",
                    self._calculate_power_tool,
                    [
                        ("Tensao (V)", "voltage"),
                        ("Corrente (A)", "current"),
                        ("Resistencia (ohm)", "resistance"),
                    ],
                ),
                (
                    "led",
                    "LED",
                    self._calculate_led_tool,
                    [
                        ("Fonte (V)", "supply"),
                        ("LED Vf (V)", "forward"),
                        ("Corrente (mA)", "current_ma"),
                    ],
                ),
                (
                    "divider",
                    "Divisor",
                    self._calculate_divider_tool,
                    [("Vin (V)", "vin"), ("R1 (ohm)", "r1"), ("R2 (ohm)", "r2")],
                ),
                (
                    "battery",
                    "Bateria",
                    self._calculate_battery_tool,
                    [
                        ("Capacidade (mAh)", "capacity"),
                        ("Consumo (mA)", "load"),
                        ("Eficiencia (%)", "efficiency"),
                    ],
                ),
                (
                    "resistor_color",
                    "Codigo de Cor",
                    self._calculate_resistor_color_tool,
                    [
                        ("Digito 1", "digit_1"),
                        ("Digito 2", "digit_2"),
                        ("Multiplicador", "multiplier"),
                    ],
                ),
                (
                    "resistor_assoc",
                    "Assoc. Resistores",
                    self._calculate_resistor_assoc_tool,
                    [("Resistores", "values")],
                ),
                ("awg", "AWG/mm2", self._calculate_awg_tool, [("AWG", "awg")]),
            ],
            "operacional": [
                (
                    "sla",
                    "SLA",
                    self._calculate_sla_tool,
                    [("Horas contratadas", "hours"), ("Horas consumidas", "used")],
                ),
                (
                    "stock_reorder",
                    "Reposicao Estoque",
                    self._calculate_stock_reorder_tool,
                    [("Estoque atual", "current"), ("Minimo", "minimum"), ("Lote", "batch")],
                ),
            ],
        }
        available_specialties = {}
        for specialty, tools_list in specialty_map.items():
            available_tools = [
                (tool_id, title, calc, fields)
                for tool_id, title, calc, fields in tools_list
                if tool_id in tool_ids
            ]
            if available_tools or specialty == "eletrica":
                available_specialties[specialty] = available_tools
        if not available_specialties:
            available_specialties["geral"] = []
        return available_specialties

    def _build_specialty_tab(
        self,
        specialty_name: str,
        specialty_tools: list[tuple[str, str, Any, list[tuple[str, str]]]],
    ) -> QWidget:
        panel = QFrame()
        panel.setObjectName("formSubPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        if not specialty_tools:
            label = QLabel(f"Nenhuma ferramenta de {specialty_name.lower()} disponivel.")
            label.setObjectName("mutedText")
            layout.addWidget(label)
            layout.addStretch()
            return panel

        specialty_tabs = QTabWidget()
        specialty_tabs.setObjectName("specialtyTabs")

        history_text = create_summary_text(48, 64)
        history_text.setPlainText(f"Ultimos calculos de {specialty_name.lower()} aparecerao aqui.")

        for tool_id, tool_title, calculator, fields in specialty_tools:
            if tool_id == "ohm" and fields == []:
                tool_widget = self._build_ohm_tool()
            else:
                tool_widget = self._build_generic_tool(
                    tool_title, fields, calculator, specialty_name
                )
            tool_widget.parent_specialty_text = history_text
            specialty_tabs.addTab(tool_widget, tool_title)

        layout.addWidget(specialty_tabs, 1)

        history_section = QFrame()
        history_section.setObjectName("formSubPanel")
        history_layout = QVBoxLayout(history_section)
        history_layout.setContentsMargins(4, 4, 4, 4)
        history_layout.setSpacing(2)

        history_label = QLabel(f"HISTORICO - {specialty_name.upper()}")
        history_label.setObjectName("formGroupTitle")

        history_layout.addWidget(history_label)
        history_layout.addWidget(history_text)

        layout.addWidget(history_section, 0)

        return panel

    def _build_tool_message(self, message: str) -> QWidget:
        widget = QWidget()
        label = QLabel(message)
        label.setObjectName("mutedText")
        layout = QVBoxLayout(widget)
        layout.addWidget(label)
        layout.addStretch()
        return widget
