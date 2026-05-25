from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
)

from frontend.app.core.icons import build_icon
from frontend.app.widgets import create_summary_text


class DashboardEquipmentFormMixin:
    def _build_equipment_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EQUIPAMENTOS")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Gestao hierarquica de ativos, objetos e componentes")
        subtitle.setObjectName("mutedText")

        self.equipment_operational_status = QLabel(
            "Selecione um equipamento para gerenciar objetos, componentes e casos de defeito."
        )
        self.equipment_operational_status.setObjectName("statusBanner")
        self.equipment_operational_status.setProperty("level", "warning")
        self.equipment_operational_status.setWordWrap(True)
        self.equipment_operational_status.hide()

        self.equipment_hierarchy_status = QLabel("Hierarquia: nenhum equipamento selecionado.")
        self.equipment_hierarchy_status.setObjectName("statusBanner")
        self.equipment_hierarchy_status.setProperty("level", "warning")
        self.equipment_hierarchy_status.setWordWrap(True)
        self.equipment_hierarchy_status.hide()

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
        self.equipment_count_badge = QLabel("0")
        self.equipment_count_badge.setObjectName("listCountBadge")
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
        self.board_count_badge = QLabel("0")
        self.board_count_badge.setObjectName("listCountBadge")
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
        self.component_count_badge = QLabel("0")
        self.component_count_badge.setObjectName("listCountBadge")

        self.equipment_form_status = QLabel("")
        self.equipment_form_status.setObjectName("mutedText")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.equipment_operational_status)
        layout.addWidget(self.equipment_hierarchy_status)
        layout.addWidget(
            self._build_equipment_section(
                "EQUIPAMENTOS",
                self.equipment_search_input,
                self.equipment_table,
                self.equipment_full_summary,
                self.equipment_count_badge,
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
                self.board_count_badge,
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
                self.component_count_badge,
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
        count_badge: QLabel,
        buttons: list[QPushButton],
    ) -> QFrame:
        section = QFrame()
        section.setObjectName("equipmentSection")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

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
        actions.addWidget(count_badge)

        table_column = QVBoxLayout()
        table_column.setContentsMargins(0, 0, 0, 0)
        table_column.setSpacing(6)
        table_column.addWidget(search_input)
        table_column.addWidget(table)
        table_column.addLayout(actions)
        table_column.addStretch(1)

        details_header = QHBoxLayout()
        details_header.setContentsMargins(0, 0, 0, 0)
        details_header.setSpacing(6)
        details_header.addWidget(details_title)
        details_header.addStretch()
        details_header.addWidget(copy_button)

        details_column = QVBoxLayout()
        details_column.setContentsMargins(8, 8, 8, 8)
        details_column.setSpacing(6)
        details_column.addLayout(details_header)
        details_column.addWidget(summary)
        details_column.addStretch(1)

        details_panel = QFrame()
        details_panel.setObjectName("equipmentDetailsPanel")
        details_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        details_panel.setLayout(details_column)
        summary.setMinimumHeight(max(150, table.minimumHeight()))
        summary.setMaximumHeight(16777215)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(10)
        content.addLayout(table_column, 7)
        content.addWidget(details_panel, 5)

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
