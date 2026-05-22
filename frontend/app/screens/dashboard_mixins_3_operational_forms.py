from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.grid import add_widget, create_grid
from frontend.app.core.inventory_catalog import STOCK_GROUP_OPTIONS
from frontend.app.widgets import create_summary_text
from frontend.app.widgets.sla_date_time_edit import SlaDateTimeEdit


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardOperationalFormsMixin:
    @staticmethod
    def _configure_multiline_editor(widget: QTextEdit, placeholder: str) -> None:
        widget.setPlaceholderText(placeholder)
        widget.setMinimumHeight(92)
        widget.setMaximumHeight(128)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _build_inventory_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("ADICIONAR ITEM - ASSISTENTE")
        title.setObjectName("sectionTitle")

        self.inventory_step_title = QLabel("ETAPA 1/3 - CATEGORIA")
        self.inventory_step_title.setObjectName("formGroupTitle")

        self.inventory_group_tabs = QTabWidget()
        self.inventory_group_tabs.setObjectName("settingsTabs")
        self.inventory_stock_group_keys: list[str] = []
        for stock_group_key, stock_group_label in STOCK_GROUP_OPTIONS:
            placeholder = QWidget()
            placeholder.setObjectName("settingsTab")
            self.inventory_group_tabs.addTab(placeholder, stock_group_label)
            self.inventory_stock_group_keys.append(stock_group_key)
        self.inventory_group_tabs.currentChanged.connect(self._handle_inventory_stock_group_changed)

        self.inventory_category_input = QComboBox()
        self.inventory_category_input.currentIndexChanged.connect(
            self._handle_inventory_category_changed
        )

        step_1_layout = QFormLayout()
        step_1_layout.setSpacing(10)
        step_1_layout.addRow("Submodulo", self.inventory_group_tabs)
        step_1_layout.addRow("Categoria", self.inventory_category_input)

        step_1_panel = QFrame()
        step_1_panel.setObjectName("formSubPanel")
        step_1_panel_layout = QVBoxLayout(step_1_panel)
        step_1_panel_layout.setContentsMargins(12, 12, 12, 12)
        step_1_panel_layout.setSpacing(8)
        step_1_panel_layout.addLayout(step_1_layout)

        self.inventory_step_1_panel = step_1_panel

        self.inventory_sku_input = QLineEdit()
        self.inventory_sku_input.setPlaceholderText("ID gerado automaticamente")
        self.inventory_sku_input.setReadOnly(True)

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

        self.inventory_quantity_input = QLineEdit()
        self.inventory_quantity_input.setPlaceholderText("Quantidade")

        self.inventory_minimum_quantity_input = QLineEdit()
        self.inventory_minimum_quantity_input.setPlaceholderText("Quantidade minima")

        self.inventory_location_input = QLineEdit()
        self.inventory_location_input.setPlaceholderText("Digite ou selecione localizacao")

        self.inventory_unit_cost_input = QLineEdit()
        self.inventory_unit_cost_input.setPlaceholderText("Custo unitario")

        self.inventory_dynamic_specs_title = QLabel("ESPECIFICACOES TECNICAS POR CATEGORIA")
        self.inventory_dynamic_specs_title.setObjectName("formGroupTitle")
        self.inventory_dynamic_specs_layout = QFormLayout()
        self.inventory_dynamic_specs_layout.setSpacing(10)
        self.inventory_dynamic_fields: list[tuple[str, QLineEdit]] = []

        self._rebuild_inventory_dynamic_fields("Transformadores")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
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
        inventory_fields_panel_layout = QVBoxLayout(inventory_fields_panel)
        inventory_fields_panel_layout.setContentsMargins(12, 12, 12, 12)
        inventory_fields_panel_layout.setSpacing(8)
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
        self.inventory_notes_input.setMinimumHeight(88)
        self.inventory_notes_input.setMaximumHeight(132)

        self.inventory_document_path_input = QLineEdit()
        self.inventory_document_path_input.setPlaceholderText("Nenhum arquivo")
        self.inventory_document_path_input.setReadOnly(True)

        self.inventory_documents_summary = create_summary_text(70, 120)
        self.inventory_documents_summary.setPlainText("Nenhum anexo vinculado ao item.")

        self.inventory_documents_buttons_frame = QFrame()
        self.inventory_documents_buttons_frame.setObjectName("formSubPanel")
        self.inventory_documents_buttons_layout = QVBoxLayout(
            self.inventory_documents_buttons_frame
        )
        self.inventory_documents_buttons_layout.setContentsMargins(8, 8, 8, 8)
        self.inventory_documents_buttons_layout.setSpacing(6)
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
        step_3_layout = QFormLayout(step_3_panel)
        step_3_layout.setContentsMargins(12, 12, 12, 12)
        step_3_layout.setSpacing(10)
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

    def _build_service_order_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("ORDENS DE SERVIÇO")
        title.setObjectName("sectionTitle")

        subtitle = QLabel("CONTROLAR ENTRADA, ANDAMENTO E CUSTOS POR ATENDIMENTO.")
        subtitle.setObjectName("mutedText")
        subtitle.setWordWrap(True)

        self.service_order_workflow_hint = QLabel(
            "ENTRADA LOGÍSTICA -> DIAGNÓSTICO TÉCNICO -> ORÇAMENTO -> LOGÍSTICA E FECHAMENTO"
        )
        self.service_order_workflow_hint.setObjectName("mutedText")

        workflow_panel = QFrame()
        workflow_panel.setObjectName("workflowPanel")
        workflow_layout = QHBoxLayout(workflow_panel)
        workflow_layout.setContentsMargins(10, 10, 10, 10)
        workflow_layout.setSpacing(8)
        self.service_order_workflow_steps: list[QLabel] = []
        for label in [
            "Triagem",
            "Diagnóstico",
            "Orçamento",
            "Aprovação",
            "Execução",
            "Conclusão",
        ]:
            step_label = QLabel(label)
            step_label.setObjectName("workflowStep")
            step_label.setProperty("stage", "future")
            step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.service_order_workflow_steps.append(step_label)
            workflow_layout.addWidget(step_label)

        self.service_order_next_step_label = QLabel("Selecione uma OS para ver o proximo passo.")
        self.service_order_next_step_label.setObjectName("statusBanner")
        self.service_order_next_step_label.setProperty("level", "warning")
        self.service_order_next_step_label.setWordWrap(True)

        self.service_order_customer_combo = QComboBox()
        self.service_order_customer_combo.currentIndexChanged.connect(
            self._refresh_service_order_equipment_combo
        )

        self.service_order_custom_id_input = QLineEdit()
        self.service_order_custom_id_input.setPlaceholderText("ID personalizado")

        self.service_order_equipment_combo = QComboBox()
        self.service_order_equipment_type_combo = QComboBox()
        self.service_order_equipment_type_combo.currentIndexChanged.connect(
            self._refresh_service_order_equipment_combo
        )
        self.service_order_technician_combo = QComboBox()

        self.service_order_service_type_combo = QComboBox()
        self.service_order_service_type_combo.addItem("Reparo", "repair")
        self.service_order_service_type_combo.addItem("Manutenção preventiva", "preventive")
        self.service_order_service_type_combo.addItem("Instalação", "installation")
        self.service_order_service_type_combo.addItem("Diagnóstico", "diagnostic")
        self.service_order_service_type_combo.addItem("Outro", "other")

        self.service_order_special_number_input = QLineEdit()
        self.service_order_special_number_input.setPlaceholderText("Nº especial")

        self.service_order_serial_number_input = QLineEdit()
        self.service_order_serial_number_input.setPlaceholderText("Número de série")

        self.service_order_status_combo = QComboBox()
        self.service_order_status_combo.addItem("Aberta", "open")
        self.service_order_status_combo.addItem("Aguardando técnico", "pending_tech")
        self.service_order_status_combo.addItem("Em diagnóstico técnico", "diagnosis")
        self.service_order_status_combo.addItem("Orçamento enviado", "quote_sent")
        self.service_order_status_combo.addItem(
            "Aguardando aprovação do cliente", "pending_approval"
        )
        self.service_order_status_combo.addItem("Aprovado para execução", "approved")
        self.service_order_status_combo.addItem("Em execução", "in_progress")
        self.service_order_status_combo.addItem("Pronto para expedição", "ready_dispatch")
        self.service_order_status_combo.addItem("Finalizado", "completed")
        self.service_order_status_combo.currentIndexChanged.connect(
            self._handle_service_order_status_changed
        )

        self.service_order_customer_approval_combo = QComboBox()
        self.service_order_customer_approval_combo.addItem("Pendente", "pending")
        self.service_order_customer_approval_combo.addItem("Aprovado", "approved")
        self.service_order_customer_approval_combo.addItem("Reprovado", "rejected")
        self.service_order_customer_approval_combo.addItem("Não se aplica", "na")

        self.service_order_entry_date_input = QLineEdit()
        self.service_order_entry_date_input.setPlaceholderText("AAAA-MM-DD")

        self.service_order_budget_sent_at_input = QLineEdit()
        self.service_order_budget_sent_at_input.setPlaceholderText("AAAA-MM-DD")
        self.service_order_budget_sent_at_input.setReadOnly(True)

        self.service_order_priority_combo = QComboBox()
        self.service_order_priority_combo.addItem("Baixa", "low")
        self.service_order_priority_combo.addItem("Normal", "normal")
        self.service_order_priority_combo.addItem("Alta", "high")
        self.service_order_priority_combo.addItem("Urgente", "urgent")

        self.service_order_sla_input = SlaDateTimeEdit()

        self.service_order_problem_input = QLineEdit()
        self.service_order_problem_input.setPlaceholderText("Defeito Informado")

        self.service_order_diagnosis_input = QLineEdit()
        self.service_order_diagnosis_input.setPlaceholderText("Defeito Encontrado")

        self.service_order_inspection_visual_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_inspection_visual_input,
            "Inspeção Visual",
        )

        self.service_order_proposed_solution_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_proposed_solution_input,
            "Solução Proposta",
        )

        self.service_order_proposed_actions_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_proposed_actions_input,
            "Execuções Necessárias",
        )

        self.service_order_intake_checklist_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_intake_checklist_input,
            "Checklist de entrada",
        )

        self.service_order_linked_objects_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_linked_objects_input,
            "Objetos vinculados",
        )

        self.service_order_parts_used_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_parts_used_input,
            "Componentes utilizados",
        )

        self.service_order_workflow_history_input = QTextEdit()
        self._configure_multiline_editor(
            self.service_order_workflow_history_input,
            "Histórico de Workflow",
        )
        self.service_order_workflow_history_input.setReadOnly(True)

        self.service_order_notes_input = QTextEdit()
        self._configure_multiline_editor(self.service_order_notes_input, "Notas")

        self.service_order_rejection_input = QLineEdit()
        self.service_order_rejection_input.setPlaceholderText("Motivo de reprovação/observação")

        self.service_order_budget_type_combo = QComboBox()
        self.service_order_budget_type_combo.addItem("Serviço", "service")
        self.service_order_budget_type_combo.addItem("Peça", "part")
        self.service_order_budget_type_combo.addItem("Outro", "other")

        self.service_order_budget_description_input = QLineEdit()
        self.service_order_budget_description_input.setPlaceholderText("Descrição do item")

        self.service_order_budget_quantity_input = QLineEdit()
        self.service_order_budget_quantity_input.setPlaceholderText("Quantidade")
        self.service_order_budget_quantity_input.setText("1")

        self.service_order_budget_unit_price_input = QLineEdit()
        self.service_order_budget_unit_price_input.setPlaceholderText("Valor unitário")
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

        record_fields_title = QLabel("ENTRADA LOGÍSTICA")
        record_fields_title.setObjectName("formGroupTitle")
        record_form_layout = QFormLayout()
        record_form_layout.setSpacing(10)
        record_form_layout.addRow("ID Personalizado", self.service_order_custom_id_input)
        record_form_layout.addRow("Empresa", self.service_order_customer_combo)
        record_form_layout.addRow("Status", self.service_order_status_combo)
        record_form_layout.addRow("Prioridade", self.service_order_priority_combo)
        record_form_layout.addRow("Equipamento", self.service_order_equipment_combo)
        record_form_layout.addRow("Tipo de Equipamento", self.service_order_equipment_type_combo)
        record_form_layout.addRow("Tipo de Serviço", self.service_order_service_type_combo)
        record_form_layout.addRow("Nº Especial", self.service_order_special_number_input)
        record_form_layout.addRow("Número de Série", self.service_order_serial_number_input)
        record_form_layout.addRow("Data de Entrada", self.service_order_entry_date_input)
        record_form_layout.addRow("Checklist de Entrada", self.service_order_intake_checklist_input)

        record_fields = QFrame()
        record_fields.setObjectName("formSubPanel")
        record_fields_layout = QVBoxLayout(record_fields)
        record_fields_layout.setContentsMargins(12, 12, 12, 12)
        record_fields_layout.setSpacing(8)
        record_fields_layout.addWidget(record_fields_title)
        record_fields_layout.addLayout(record_form_layout)

        technical_fields_title = QLabel("DIAGNÓSTICO TÉCNICO")
        technical_fields_title.setObjectName("formGroupTitle")
        technical_form_layout = QFormLayout()
        technical_form_layout.setSpacing(10)
        technical_form_layout.addRow("Técnico Responsável", self.service_order_technician_combo)
        technical_form_layout.addRow("Defeito Informado", self.service_order_problem_input)
        technical_form_layout.addRow("Defeito Encontrado", self.service_order_diagnosis_input)
        technical_form_layout.addRow("Inspeção Visual", self.service_order_inspection_visual_input)
        technical_form_layout.addRow("Solução Proposta", self.service_order_proposed_solution_input)
        technical_form_layout.addRow(
            "Execuções Necessárias", self.service_order_proposed_actions_input
        )

        technical_fields = QFrame()
        technical_fields.setObjectName("formSubPanel")
        technical_fields_layout = QVBoxLayout(technical_fields)
        technical_fields_layout.setContentsMargins(12, 12, 12, 12)
        technical_fields_layout.setSpacing(8)
        technical_fields_layout.addWidget(technical_fields_title)
        technical_fields_layout.addLayout(technical_form_layout)

        budget_fields_title = QLabel("ORÇAMENTO")
        budget_fields_title.setObjectName("formGroupTitle")
        budget_form_layout = QFormLayout()
        budget_form_layout.setSpacing(10)
        budget_form_layout.addRow("Entrega Prevista", self.service_order_sla_input)
        budget_form_layout.addRow(
            "Data de Envio do Orçamento", self.service_order_budget_sent_at_input
        )
        budget_form_layout.addRow(
            "Aprovação do Cliente", self.service_order_customer_approval_combo
        )
        budget_form_layout.addRow("Tipo do item", self.service_order_budget_type_combo)
        budget_form_layout.addRow("Item", self.service_order_budget_description_input)
        budget_form_layout.addRow("Quantidade", self.service_order_budget_quantity_input)
        budget_form_layout.addRow("Valor unitário", self.service_order_budget_unit_price_input)

        budget_fields = QFrame()
        budget_fields.setObjectName("formSubPanel")
        budget_fields_layout = QVBoxLayout(budget_fields)
        budget_fields_layout.setContentsMargins(12, 12, 12, 12)
        budget_fields_layout.setSpacing(8)
        budget_fields_layout.addWidget(budget_fields_title)
        budget_fields_layout.addLayout(budget_form_layout)

        logistics_fields_title = QLabel("LOGÍSTICA E FECHAMENTO")
        logistics_fields_title.setObjectName("formGroupTitle")
        logistics_form_layout = QFormLayout()
        logistics_form_layout.setSpacing(10)
        logistics_form_layout.addRow("Objetos Vinculados", self.service_order_linked_objects_input)
        logistics_form_layout.addRow("Componentes Utilizados", self.service_order_parts_used_input)

        logistics_fields = QFrame()
        logistics_fields.setObjectName("formSubPanel")
        logistics_fields_layout = QVBoxLayout(logistics_fields)
        logistics_fields_layout.setContentsMargins(12, 12, 12, 12)
        logistics_fields_layout.setSpacing(8)
        logistics_fields_layout.addWidget(logistics_fields_title)
        logistics_fields_layout.addLayout(logistics_form_layout)

        general_fields_title = QLabel("GERAL")
        general_fields_title.setObjectName("formGroupTitle")
        general_form_layout = QFormLayout()
        general_form_layout.setSpacing(10)
        general_form_layout.addRow("Tipo do anexo", self.service_order_document_type_combo)
        general_form_layout.addRow("Anexos / Evidências", self.service_order_document_path_input)
        general_form_layout.addRow(
            "Histórico de Workflow", self.service_order_workflow_history_input
        )
        general_form_layout.addRow("Notas", self.service_order_notes_input)
        general_form_layout.addRow("Observação de Reprovação", self.service_order_rejection_input)

        general_fields = QFrame()
        general_fields.setObjectName("formSubPanel")
        general_fields_layout = QVBoxLayout(general_fields)
        general_fields_layout.setContentsMargins(12, 12, 12, 12)
        general_fields_layout.setSpacing(8)
        general_fields_layout.addWidget(general_fields_title)
        general_fields_layout.addLayout(general_form_layout)

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, record_fields, 0)
        add_widget(fields_layout, technical_fields, 1)
        add_widget(fields_layout, budget_fields, 2)
        add_widget(fields_layout, logistics_fields, 3)
        add_widget(fields_layout, general_fields, 4)

        self.service_order_form_status = QLabel("")
        self.service_order_form_status.setObjectName("mutedText")

        self.service_order_current_status = QLabel("Status: -")
        self.service_order_current_status.setObjectName("mutedText")

        self.service_order_budget_summary = QLabel("Orçamento: nenhum item.")
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

        self.service_order_delete_button = QPushButton("Excluir")
        self.service_order_delete_button.setObjectName("dangerButton")
        self.service_order_delete_button.setEnabled(False)
        self.service_order_delete_button.clicked.connect(self._request_service_order_delete)

        self.service_order_save_button = QPushButton("Salvar OS")
        self.service_order_save_button.clicked.connect(self._request_service_order_save)

        self.service_order_diagnosis_button = QPushButton("Registrar diagnóstico")
        self.service_order_diagnosis_button.setObjectName("secondaryButton")
        self.service_order_diagnosis_button.clicked.connect(self._request_service_order_diagnosis)

        self.service_order_add_budget_button = QPushButton("Adicionar item")
        self.service_order_add_budget_button.setObjectName("secondaryButton")
        self.service_order_add_budget_button.clicked.connect(
            self._request_service_order_budget_item
        )

        self.service_order_submit_quote_button = QPushButton("Enviar orçamento")
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
        actions.addWidget(self.service_order_delete_button)
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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.service_order_workflow_hint)
        layout.addWidget(workflow_panel)
        layout.addWidget(self.service_order_next_step_label)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        content_layout.addLayout(fields_layout)
        content_layout.addWidget(self.service_order_current_status)
        content_layout.addWidget(details_title)
        content_layout.addWidget(self.service_order_full_summary)
        content_layout.addWidget(self.service_order_budget_summary)
        content_layout.addWidget(self.service_order_documents_summary)
        content_layout.addWidget(self.service_order_form_status)
        content_layout.addLayout(actions)
        content_layout.addLayout(flow_actions)
        content_layout.addLayout(document_actions)
        content_layout.addStretch()

        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_scroll.setWidget(content_widget)

        layout.addWidget(content_scroll, 1)

        return panel
