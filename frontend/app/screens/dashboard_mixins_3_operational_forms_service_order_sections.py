from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from frontend.app.core.grid import add_widget, create_grid


class DashboardServiceOrderFormSectionsMixin:
    @staticmethod
    def _build_service_order_section_panel(title: str, form_layout: QFormLayout) -> QFrame:
        form_layout.setHorizontalSpacing(14)
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        title_label = QLabel(title)
        title_label.setObjectName("formGroupTitle")
        section = QFrame()
        section.setObjectName("formSubPanel")
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(12, 12, 12, 12)
        section_layout.setSpacing(8)
        section_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        section_layout.addWidget(title_label)
        section_layout.addLayout(form_layout)
        return section

    def _build_service_order_fields_grid(self):
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

        logistics_form_layout = QFormLayout()
        logistics_form_layout.setSpacing(10)
        logistics_form_layout.addRow("Objetos Vinculados", self.service_order_linked_objects_input)
        logistics_form_layout.addRow("Componentes Utilizados", self.service_order_parts_used_input)

        general_form_layout = QFormLayout()
        general_form_layout.setSpacing(10)
        general_form_layout.addRow("Tipo do anexo", self.service_order_document_type_combo)
        general_form_layout.addRow("Anexos / Evidências", self.service_order_document_path_input)
        general_form_layout.addRow(
            "Histórico de Workflow", self.service_order_workflow_history_input
        )
        general_form_layout.addRow("Notas", self.service_order_notes_input)
        general_form_layout.addRow("Observação de Reprovação", self.service_order_rejection_input)

        fields_layout = create_grid(spacing=8)
        add_widget(
            fields_layout,
            self._build_service_order_section_panel("ENTRADA LOGÍSTICA", record_form_layout),
            0,
            0,
            6,
        )
        add_widget(
            fields_layout,
            self._build_service_order_section_panel("DIAGNÓSTICO TÉCNICO", technical_form_layout),
            0,
            6,
            6,
        )
        add_widget(
            fields_layout,
            self._build_service_order_section_panel("ORÇAMENTO", budget_form_layout),
            1,
            0,
            6,
        )
        add_widget(
            fields_layout,
            self._build_service_order_section_panel(
                "LOGÍSTICA E FECHAMENTO", logistics_form_layout
            ),
            1,
            6,
            6,
        )
        add_widget(
            fields_layout,
            self._build_service_order_section_panel("GERAL", general_form_layout),
            2,
        )
        return fields_layout

    def _build_service_order_action_rows(self) -> tuple[QHBoxLayout, QHBoxLayout, QHBoxLayout]:
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
        return actions, flow_actions, document_actions

    def _build_service_order_workflow_panel(self) -> QFrame:
        workflow_panel = QFrame()
        workflow_panel.setObjectName("workflowPanel")
        workflow_layout = QHBoxLayout(workflow_panel)
        workflow_layout.setContentsMargins(10, 10, 10, 10)
        workflow_layout.setSpacing(8)
        self.service_order_workflow_steps = []
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
        return workflow_panel
