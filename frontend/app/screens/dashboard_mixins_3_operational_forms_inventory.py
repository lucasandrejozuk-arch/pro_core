from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.inventory_catalog import STOCK_GROUP_OPTIONS
from frontend.app.widgets import create_summary_text


class DashboardInventoryFormBuilderMixin:
    def _build_inventory_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("ADICIONAR ITEM - ASSISTENTE")
        title.setObjectName("sectionTitle")

        self.inventory_step_title = QLabel("ETAPA 1/3 - CATEGORIA")
        self.inventory_step_title.setObjectName("formGroupTitle")

        self.inventory_group_tabs = QTabWidget()
        self.inventory_group_tabs.setObjectName("settingsTabs")
        self.inventory_group_tabs.setDocumentMode(True)
        self.inventory_group_tabs.setUsesScrollButtons(True)
        self.inventory_group_tabs.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.inventory_stock_group_keys: list[str] = []
        for stock_group_key, stock_group_label in STOCK_GROUP_OPTIONS:
            placeholder = QWidget()
            placeholder.setObjectName("settingsTab")
            self.inventory_group_tabs.addTab(placeholder, stock_group_label)
            self.inventory_stock_group_keys.append(stock_group_key)
        self.inventory_group_tabs.currentChanged.connect(self._handle_inventory_stock_group_changed)
        self.inventory_group_tabs.setMaximumHeight(
            self.inventory_group_tabs.tabBar().sizeHint().height() + 8
        )

        self.inventory_category_input = QComboBox()
        self.inventory_category_input.setMinimumHeight(36)
        self.inventory_category_input.currentIndexChanged.connect(
            self._handle_inventory_category_changed
        )

        step_1_layout = QVBoxLayout()
        step_1_layout.setContentsMargins(0, 0, 0, 0)
        step_1_layout.setSpacing(10)
        step_1_tabs_label = QLabel("SUBMODULO")
        step_1_tabs_label.setObjectName("formGroupTitle")
        step_1_layout.addWidget(step_1_tabs_label)
        step_1_layout.addWidget(self.inventory_group_tabs)
        step_1_form = QFormLayout()
        step_1_form.setSpacing(10)
        step_1_form.setHorizontalSpacing(14)
        step_1_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        step_1_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        step_1_form.addRow("Categoria", self.inventory_category_input)
        step_1_layout.addLayout(step_1_form)

        step_1_panel = QFrame()
        step_1_panel.setObjectName("formSubPanel")
        step_1_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        step_1_panel_layout = QVBoxLayout(step_1_panel)
        step_1_panel_layout.setContentsMargins(12, 12, 12, 12)
        step_1_panel_layout.setSpacing(8)
        step_1_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        step_1_panel_layout.addLayout(step_1_layout)

        self.inventory_step_1_panel = step_1_panel

        self.inventory_sku_input = QLineEdit()
        self.inventory_sku_input.setPlaceholderText("ID gerado automaticamente")
        self.inventory_sku_input.setReadOnly(True)
        self.inventory_sku_input.setMinimumHeight(36)

        self.inventory_generate_id_button = QPushButton("Gerar ID")
        self.inventory_generate_id_button.setObjectName("secondaryButton")
        self.inventory_generate_id_button.clicked.connect(self._generate_inventory_sku)

        sku_row = QHBoxLayout()
        sku_row.setContentsMargins(0, 0, 0, 0)
        sku_row.setSpacing(8)
        sku_row.addWidget(self.inventory_sku_input, 1)
        sku_row.addWidget(self.inventory_generate_id_button)

        self.inventory_name_input = QLineEdit()
        self.inventory_name_input.setPlaceholderText("Nome descritivo do item")
        self.inventory_name_input.setClearButtonEnabled(True)
        self.inventory_name_input.setMinimumHeight(36)

        self.inventory_quantity_input = QLineEdit()
        self.inventory_quantity_input.setPlaceholderText("Quantidade")
        self.inventory_quantity_input.setMinimumHeight(36)

        self.inventory_minimum_quantity_input = QLineEdit()
        self.inventory_minimum_quantity_input.setPlaceholderText("Quantidade minima")
        self.inventory_minimum_quantity_input.setMinimumHeight(36)

        self.inventory_location_input = QLineEdit()
        self.inventory_location_input.setPlaceholderText("Digite ou selecione localizacao")
        self.inventory_location_input.setClearButtonEnabled(True)
        self.inventory_location_input.setMinimumHeight(36)

        self.inventory_unit_cost_input = QLineEdit()
        self.inventory_unit_cost_input.setPlaceholderText("Custo unitario")
        self.inventory_unit_cost_input.setMinimumHeight(36)

        self.inventory_dynamic_specs_title = QLabel("ESPECIFICACOES TECNICAS POR CATEGORIA")
        self.inventory_dynamic_specs_title.setObjectName("formGroupTitle")
        self.inventory_dynamic_specs_layout = QFormLayout()
        self.inventory_dynamic_specs_layout.setSpacing(10)
        self.inventory_dynamic_fields: list[tuple[str, QLineEdit]] = []

        self._rebuild_inventory_dynamic_fields("Transformadores")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setHorizontalSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form_layout.addRow("ID", sku_row)
        form_layout.addRow("Nome", self.inventory_name_input)
        form_layout.addRow("Quantidade", self.inventory_quantity_input)
        form_layout.addRow("Minimo", self.inventory_minimum_quantity_input)
        form_layout.addRow("Localizacao", self.inventory_location_input)
        form_layout.addRow("Custo", self.inventory_unit_cost_input)
        form_layout.addRow(self.inventory_dynamic_specs_title)
        form_layout.addRow(self.inventory_dynamic_specs_layout)

        inventory_fields_title = QLabel("ETAPA 2/3 - DADOS TECNICOS")
        inventory_fields_title.setObjectName("formGroupTitle")
        inventory_fields_panel = QFrame()
        inventory_fields_panel.setObjectName("formSubPanel")
        inventory_fields_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )
        inventory_fields_panel_layout = QVBoxLayout(inventory_fields_panel)
        inventory_fields_panel_layout.setContentsMargins(12, 12, 12, 12)
        inventory_fields_panel_layout.setSpacing(8)
        inventory_fields_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        inventory_fields_panel_layout.addWidget(inventory_fields_title)
        inventory_fields_panel_layout.addLayout(form_layout)

        self.inventory_step_2_panel = inventory_fields_panel

        self.inventory_stock_status = QLabel("Status: novo item.")
        self.inventory_stock_status.setObjectName("statusBanner")
        self.inventory_stock_status.setProperty("level", "info")
        self.inventory_stock_status.setWordWrap(True)

        self.inventory_reorder_status = QLabel(
            "Reposicao: informe quantidade, minimo e custo para calcular necessidade."
        )
        self.inventory_reorder_status.setObjectName("statusBanner")
        self.inventory_reorder_status.setProperty("level", "warning")
        self.inventory_reorder_status.setWordWrap(True)

        inventory_details_title = QLabel("DADOS COMPLETOS")
        inventory_details_title.setObjectName("formGroupTitle")
        self.inventory_full_summary = create_summary_text()

        self.inventory_notes_input = QTextEdit()
        self.inventory_notes_input.setPlaceholderText("Observacoes extras (opcional)")
        self.inventory_notes_input.setAcceptRichText(False)
        self.inventory_notes_input.setTabChangesFocus(True)
        self.inventory_notes_input.setMinimumHeight(88)
        self.inventory_notes_input.setMaximumHeight(132)

        self.inventory_document_path_input = QLineEdit()
        self.inventory_document_path_input.setPlaceholderText("Nenhum arquivo")
        self.inventory_document_path_input.setReadOnly(True)
        self.inventory_document_path_input.setMinimumHeight(36)

        self.inventory_documents_summary = create_summary_text(70, 120)
        self.inventory_documents_summary.setPlainText("Nenhum anexo vinculado ao item.")

        self.inventory_documents_buttons_frame = QFrame()
        self.inventory_documents_buttons_frame.setObjectName("formSubPanel")
        self.inventory_documents_buttons_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )
        self.inventory_documents_buttons_layout = QVBoxLayout(
            self.inventory_documents_buttons_frame
        )
        self.inventory_documents_buttons_layout.setContentsMargins(8, 8, 8, 8)
        self.inventory_documents_buttons_layout.setSpacing(6)
        self.inventory_documents_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.inventory_documents_buttons_layout.addWidget(
            QLabel("Selecione um item para habilitar downloads por anexo.")
        )

        self.inventory_attach_document_button = QPushButton("Anexar PDF")
        self.inventory_attach_document_button.setObjectName("secondaryButton")
        self.inventory_attach_document_button.clicked.connect(self._select_inventory_document)

        self.inventory_remove_document_button = QPushButton("Remover PDF")
        self.inventory_remove_document_button.setObjectName("secondaryButton")
        self.inventory_remove_document_button.clicked.connect(self._remove_inventory_document)

        document_actions = QHBoxLayout()
        document_actions.setContentsMargins(0, 0, 0, 0)
        document_actions.setSpacing(8)
        document_actions.addWidget(self.inventory_attach_document_button)
        document_actions.addWidget(self.inventory_remove_document_button)
        document_actions.addStretch()

        step_3_panel = QFrame()
        step_3_panel.setObjectName("formSubPanel")
        step_3_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        step_3_layout = QFormLayout(step_3_panel)
        step_3_layout.setContentsMargins(12, 12, 12, 12)
        step_3_layout.setSpacing(10)
        step_3_layout.setHorizontalSpacing(14)
        step_3_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        step_3_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        step_3_title = QLabel("ETAPA 3/3 - CONFIGURACOES FINAIS")
        step_3_title.setObjectName("formGroupTitle")
        step_3_layout.addRow(step_3_title)
        step_3_layout.addRow("Observacoes", self.inventory_notes_input)
        step_3_layout.addRow("Datasheet (PDF)", self.inventory_document_path_input)
        step_3_layout.addRow("", document_actions)
        step_3_layout.addRow("Arquivos vinculados", self.inventory_documents_summary)
        step_3_layout.addRow("Downloads", self.inventory_documents_buttons_frame)
        step_3_layout.addRow(inventory_details_title)
        step_3_layout.addRow(self.inventory_full_summary)

        self.inventory_step_3_panel = step_3_panel

        self.inventory_form_status = QLabel("")
        self.inventory_form_status.setObjectName("mutedText")

        self.inventory_new_button = QPushButton("Novo")
        self.inventory_new_button.setObjectName("secondaryButton")
        self.inventory_new_button.clicked.connect(self.clear_inventory_form)

        self.inventory_delete_button = QPushButton("Excluir")
        self.inventory_delete_button.setObjectName("dangerButton")
        self.inventory_delete_button.setEnabled(False)
        self.inventory_delete_button.clicked.connect(self._request_inventory_delete)

        self.inventory_back_button = QPushButton("Voltar")
        self.inventory_back_button.setObjectName("secondaryButton")
        self.inventory_back_button.clicked.connect(self._go_inventory_previous_step)

        self.inventory_next_button = QPushButton("Avancar")
        self.inventory_next_button.setObjectName("secondaryButton")
        self.inventory_next_button.clicked.connect(self._go_inventory_next_step)

        self.inventory_save_button = QPushButton("Salvar")
        self.inventory_save_button.clicked.connect(self._request_inventory_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.inventory_back_button)
        actions.addWidget(self.inventory_next_button)
        actions.addWidget(self.inventory_new_button)
        actions.addWidget(self.inventory_delete_button)
        actions.addWidget(self.inventory_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.inventory_step_title)
        layout.addWidget(self.inventory_step_1_panel)
        layout.addWidget(self.inventory_step_2_panel)
        layout.addWidget(self.inventory_step_3_panel)
        layout.addWidget(self.inventory_stock_status)
        layout.addWidget(self.inventory_reorder_status)
        layout.addWidget(self.inventory_form_status)
        layout.addLayout(actions)

        self._initialize_inventory_wizard()

        return panel
