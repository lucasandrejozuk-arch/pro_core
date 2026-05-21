from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
)

from frontend.app.core.grid import add_widget, create_grid
from frontend.app.core.icons import build_icon
from frontend.app.widgets import create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardRecordFormsMixin:
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
            150,
        )
        self.equipment_table.itemSelectionChanged.connect(self._handle_equipment_table_selection)
        self.equipment_full_summary = create_summary_text(110, 180)
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
            136,
        )
        self.equipment_boards_table.itemSelectionChanged.connect(
            self._handle_equipment_board_table_selection
        )
        self.board_full_summary = create_summary_text(110, 180)
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
            136,
        )
        self.equipment_components_table.itemSelectionChanged.connect(
            self._handle_equipment_component_table_selection
        )
        self.component_full_summary = create_summary_text(110, 180)
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
        copy_button = self._build_copy_summary_button(summary)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        for button in buttons:
            actions.addWidget(button)
        actions.addStretch()

        table_column = QVBoxLayout()
        table_column.setContentsMargins(0, 0, 0, 0)
        table_column.setSpacing(6)
        table_column.addWidget(search_input)
        table_column.addWidget(table)
        table_column.addLayout(actions)

        details_header = QHBoxLayout()
        details_header.setContentsMargins(0, 0, 0, 0)
        details_header.setSpacing(6)
        details_header.addWidget(details_title)
        details_header.addStretch()
        details_header.addWidget(copy_button)

        details_column = QVBoxLayout()
        details_column.setContentsMargins(0, 0, 0, 0)
        details_column.setSpacing(6)
        details_column.addLayout(details_header)
        details_column.addWidget(summary)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(10)
        content.addLayout(table_column, 7)
        content.addLayout(details_column, 5)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(title_label)
        layout.addLayout(content)
        return section

    def _build_copy_summary_button(self, summary: QTextEdit) -> QPushButton:
        button = QPushButton("")
        button.setObjectName("summaryCopyButton")
        button.setToolTip("Copiar dados completos")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(build_icon("copy", self.record_editor_icon_color, 18))
        button.setIconSize(QSize(18, 18))
        button.setFixedSize(30, 28)
        button.clicked.connect(
            lambda checked=False, source=summary: self._copy_summary_text(source)
        )
        if not hasattr(self, "summary_copy_buttons"):
            self.summary_copy_buttons = []
        self.summary_copy_buttons.append(button)
        return button

    def _copy_summary_text(self, summary: QTextEdit) -> None:
        QApplication.clipboard().setText(summary.toPlainText().strip())
        if hasattr(self, "equipment_form_status"):
            self.set_equipment_form_status("Dados completos copiados.")

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
