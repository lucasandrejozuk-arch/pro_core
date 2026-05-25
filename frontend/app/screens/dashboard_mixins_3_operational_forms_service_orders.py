from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.screens.dashboard_mixins_3_operational_forms_service_order_sections import (
    DashboardServiceOrderFormSectionsMixin,
)
from frontend.app.widgets import create_summary_text
from frontend.app.widgets.sla_date_time_edit import SlaDateTimeEdit


class DashboardServiceOrderFormBuilderMixin(DashboardServiceOrderFormSectionsMixin):
    @staticmethod
    def _configure_multiline_editor(widget: QTextEdit, placeholder: str) -> None:
        widget.setPlaceholderText(placeholder)
        widget.setAcceptRichText(False)
        widget.setTabChangesFocus(True)
        widget.setMinimumHeight(84)
        widget.setMaximumHeight(112)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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
        self.service_order_workflow_hint.setWordWrap(True)

        workflow_panel = self._build_service_order_workflow_panel()

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

        for field in (
            self.service_order_customer_combo,
            self.service_order_custom_id_input,
            self.service_order_equipment_combo,
            self.service_order_equipment_type_combo,
            self.service_order_technician_combo,
            self.service_order_service_type_combo,
            self.service_order_special_number_input,
            self.service_order_serial_number_input,
            self.service_order_status_combo,
            self.service_order_customer_approval_combo,
            self.service_order_entry_date_input,
            self.service_order_budget_sent_at_input,
            self.service_order_priority_combo,
            self.service_order_sla_input,
            self.service_order_problem_input,
            self.service_order_diagnosis_input,
            self.service_order_rejection_input,
            self.service_order_budget_type_combo,
            self.service_order_budget_description_input,
            self.service_order_budget_quantity_input,
            self.service_order_budget_unit_price_input,
            self.service_order_document_type_combo,
            self.service_order_document_path_input,
        ):
            field.setMinimumHeight(36)

        fields_layout = self._build_service_order_fields_grid()

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

        self.service_order_full_summary = create_summary_text(110, 176)

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

        actions, flow_actions, document_actions = self._build_service_order_action_rows()

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
