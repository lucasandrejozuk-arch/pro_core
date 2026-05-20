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


class DashboardMixin3:
    def _build_ohm_tool(self) -> QWidget:
        widget = QWidget()
        form_panel = QFrame()
        form_panel.setObjectName("formSubPanel")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(form_panel)
        layout.addStretch()

        self.ohm_target_combo = QComboBox()
        self.ohm_target_combo.addItem("Tensao", "voltage")
        self.ohm_target_combo.addItem("Corrente", "current")
        self.ohm_target_combo.addItem("Resistencia", "resistance")
        self.ohm_voltage_input = QLineEdit()
        self.ohm_voltage_input.setPlaceholderText("Tensao (V)")
        self.ohm_current_input = QLineEdit()
        self.ohm_current_input.setPlaceholderText("Corrente (A)")
        self.ohm_resistance_input = QLineEdit()
        self.ohm_resistance_input.setPlaceholderText("Resistencia (ohm)")
        self.ohm_result = create_summary_text(56, 72)
        self.ohm_result.setPlainText("")

        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Calcular:", self.ohm_target_combo)
        form.addRow("Tensao (V):", self.ohm_voltage_input)
        form.addRow("Corrente (A):", self.ohm_current_input)
        form.addRow("Resistencia (ohm):", self.ohm_resistance_input)

        def calculate_ohm_with_history() -> None:
            self._calculate_ohm_tool()
            if widget.parent_specialty_text:
                text = self.ohm_result.toPlainText()
                widget.parent_specialty_text.setPlainText(
                    self._push_calculation_to_history(
                        widget.parent_specialty_text, f"Lei de Ohm: {text}"
                    )
                )

        calculate_button = QPushButton("Calcular")
        calculate_button.clicked.connect(calculate_ohm_with_history)

        panel_layout = QVBoxLayout(form_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(8)
        panel_layout.addLayout(form)
        panel_layout.addWidget(calculate_button, 0, Qt.AlignmentFlag.AlignLeft)
        panel_layout.addWidget(self.ohm_result)

        self.ohm_target_combo.currentIndexChanged.connect(self._update_ohm_fields)
        self._update_ohm_fields()

        widget.parent_specialty_text = None
        return widget

    def _build_generic_tool(
        self,
        title: str,
        fields: list[tuple[str, str]],
        calculator: Callable[[dict[str, QLineEdit]], str],
        specialty_name: str = "geral",
    ) -> QWidget:
        widget = QWidget()
        panel = QFrame()
        panel.setObjectName("formSubPanel")
        inputs: dict[str, QLineEdit] = {}
        form = QFormLayout()
        form.setSpacing(8)
        for label, key in fields:
            input_widget = QLineEdit()
            input_widget.setPlaceholderText(label)
            inputs[key] = input_widget
            form.addRow(f"{label}:", input_widget)
        result = create_summary_text(56, 72)

        def run_calculation() -> None:
            try:
                text = calculator(inputs)
            except ValueError as exc:
                text = str(exc)
            result.setPlainText(text)
            widget.parent_specialty_text.setPlainText(
                self._push_calculation_to_history(widget.parent_specialty_text, f"{title}: {text}")
            )

        calculate_button = QPushButton("Calcular")
        calculate_button.clicked.connect(run_calculation)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(8)
        panel_layout.addLayout(form)
        panel_layout.addWidget(calculate_button, 0, Qt.AlignmentFlag.AlignLeft)
        panel_layout.addWidget(result)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(panel)
        layout.addStretch()
        widget.parent_specialty_text = None
        return widget

    def _update_ohm_fields(self) -> None:
        target = str(self.ohm_target_combo.currentData() or "voltage")
        mapping = {
            "voltage": self.ohm_voltage_input,
            "current": self.ohm_current_input,
            "resistance": self.ohm_resistance_input,
        }
        placeholders = {
            "voltage": "Tensao (V)",
            "current": "Corrente (A)",
            "resistance": "Resistencia (ohm)",
        }
        for key, input_widget in mapping.items():
            blocked = key == target
            input_widget.setReadOnly(blocked)
            input_widget.clear()
            input_widget.setPlaceholderText(
                "Bloqueado: sera calculado" if blocked else placeholders[key]
            )

    def _calculate_ohm_tool(self) -> None:
        target = str(self.ohm_target_combo.currentData() or "voltage")
        voltage = self._optional_float(self.ohm_voltage_input.text())
        current = self._optional_float(self.ohm_current_input.text())
        resistance = self._optional_float(self.ohm_resistance_input.text())
        if target == "voltage":
            if current is None or resistance is None:
                text = "Informe corrente e resistencia."
            else:
                text = f"Tensao: {self._format_number(current * resistance)} V"
        elif target == "current":
            if voltage is None or resistance in {None, 0}:
                text = "Informe tensao e resistencia maior que zero."
            else:
                text = f"Corrente: {self._format_number(voltage / resistance)} A"
        elif voltage is None or current in {None, 0}:
            text = "Informe tensao e corrente maior que zero."
        else:
            text = f"Resistencia: {self._format_number(voltage / current)} ohm"
        self.ohm_result.setPlainText(text)

    def _calculate_power_tool(self, inputs: dict[str, QLineEdit]) -> str:
        voltage = self._optional_float(inputs["voltage"].text())
        current = self._optional_float(inputs["current"].text())
        resistance = self._optional_float(inputs["resistance"].text())
        if voltage is not None and current is not None:
            return f"Potencia: {self._format_number(voltage * current)} W"
        if current is not None and resistance is not None:
            return f"Potencia: {self._format_number((current**2) * resistance)} W"
        if voltage is not None and resistance not in {None, 0}:
            return f"Potencia: {self._format_number((voltage**2) / resistance)} W"
        raise ValueError("Informe V/I, I/R ou V/R.")

    def _calculate_led_tool(self, inputs: dict[str, QLineEdit]) -> str:
        supply = self._required_float(inputs["supply"].text(), "fonte")
        forward = self._required_float(inputs["forward"].text(), "Vf")
        current_ma = self._required_float(inputs["current_ma"].text(), "corrente")
        if supply <= forward or current_ma <= 0:
            raise ValueError("Fonte deve ser maior que Vf e corrente deve ser positiva.")
        current = current_ma / 1000
        resistor = (supply - forward) / current
        power = current * current * resistor
        return (
            f"Resistor: {self._format_number(resistor)} ohm | "
            f"Potencia: {self._format_number(power)} W"
        )

    def _calculate_divider_tool(self, inputs: dict[str, QLineEdit]) -> str:
        vin = self._required_float(inputs["vin"].text(), "Vin")
        r1 = self._required_float(inputs["r1"].text(), "R1")
        r2 = self._required_float(inputs["r2"].text(), "R2")
        if r1 <= 0 or r2 <= 0:
            raise ValueError("R1 e R2 devem ser maiores que zero.")
        return f"Vout: {self._format_number(vin * (r2 / (r1 + r2)))} V"

    def _calculate_battery_tool(self, inputs: dict[str, QLineEdit]) -> str:
        capacity = self._required_float(inputs["capacity"].text(), "capacidade")
        load = self._required_float(inputs["load"].text(), "consumo")
        efficiency = self._optional_float(inputs["efficiency"].text()) or 100.0
        if capacity <= 0 or load <= 0 or efficiency <= 0:
            raise ValueError("Valores devem ser positivos.")
        autonomy = (capacity / load) * (efficiency / 100)
        return f"Autonomia estimada: {self._format_number(autonomy)} h"

    def _calculate_resistor_color_tool(self, inputs: dict[str, QLineEdit]) -> str:
        digit_1 = int(self._required_float(inputs["digit_1"].text(), "digito 1"))
        digit_2 = int(self._required_float(inputs["digit_2"].text(), "digito 2"))
        multiplier = self._required_float(inputs["multiplier"].text(), "multiplicador")
        if digit_1 < 0 or digit_1 > 9 or digit_2 < 0 or digit_2 > 9:
            raise ValueError("Digitos devem ficar entre 0 e 9.")
        return f"Resistencia: {self._format_number(((digit_1 * 10) + digit_2) * multiplier)} ohm"

    def _calculate_resistor_assoc_tool(self, inputs: dict[str, QLineEdit]) -> str:
        values = [
            self._required_float(token, "resistor")
            for token in inputs["values"].text().replace(";", ",").split(",")
            if token.strip()
        ]
        if not values or any(value <= 0 for value in values):
            raise ValueError("Informe resistores positivos separados por virgula.")
        series = sum(values)
        parallel = 1 / sum(1 / value for value in values)
        return (
            f"Serie: {self._format_number(series)} ohm | "
            f"Paralelo: {self._format_number(parallel)} ohm"
        )

    def _calculate_awg_tool(self, inputs: dict[str, QLineEdit]) -> str:
        awg = self._required_float(inputs["awg"].text(), "AWG")
        if awg < -5 or awg > 50:
            raise ValueError("AWG fora da faixa -5 a 50.")
        diameter = 0.127 * (92 ** ((36 - awg) / 39))
        area = (math.pi / 4) * (diameter**2)
        return (
            f"Area: {self._format_number(area)} mm2 | "
            f"Diametro: {self._format_number(diameter)} mm"
        )

    def _calculate_markup_tool(self, inputs: dict[str, QLineEdit]) -> str:
        cost = self._required_float(inputs["cost"].text(), "custo")
        margin = self._required_float(inputs["margin"].text(), "margem")
        if cost < 0 or margin >= 100:
            raise ValueError("Custo deve ser positivo e margem menor que 100%.")
        return f"Preco de venda: R$ {self._format_number(cost / (1 - (margin / 100)))}"

    def _calculate_installment_tool(self, inputs: dict[str, QLineEdit]) -> str:
        amount = self._required_float(inputs["amount"].text(), "valor")
        installments = int(self._required_float(inputs["installments"].text(), "parcelas"))
        if installments <= 0:
            raise ValueError("Parcelas deve ser maior que zero.")
        return f"Parcela: R$ {self._format_number(amount / installments)}"

    def _calculate_sla_tool(self, inputs: dict[str, QLineEdit]) -> str:
        hours = self._required_float(inputs["hours"].text(), "horas contratadas")
        used = self._required_float(inputs["used"].text(), "horas consumidas")
        return f"Saldo de SLA: {self._format_number(hours - used)} h"

    def _calculate_stock_reorder_tool(self, inputs: dict[str, QLineEdit]) -> str:
        current = self._required_float(inputs["current"].text(), "estoque atual")
        minimum = self._required_float(inputs["minimum"].text(), "minimo")
        batch = self._optional_float(inputs["batch"].text()) or 1
        needed = max(0, minimum - current)
        lots = math.ceil(needed / batch) if batch > 0 else 0
        return f"Necessidade: {self._format_number(needed)} unidade(s) | Lotes: {lots}"

    def _push_tools_history(self, text: str) -> None:
        current_lines = [
            line
            for line in self.tools_history_text.toPlainText().splitlines()
            if line.strip() and "ultimos calculos" not in line.lower()
        ]
        current_lines.append(text)
        self.tools_history_text.setPlainText("\n".join(current_lines[-10:]))

    def _push_calculation_to_history(self, history_widget, text: str) -> str:
        current_lines = [
            line
            for line in history_widget.toPlainText().splitlines()
            if line.strip() and "ultimos calculos" not in line.lower()
        ]
        current_lines.append(text)
        result = "\n".join(current_lines[-10:])
        return result

    @staticmethod
    def _optional_float(value: str) -> float | None:
        text = value.strip().replace(",", ".")
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _required_float(self, value: str, label: str) -> float:
        parsed = self._optional_float(value)
        if parsed is None:
            raise ValueError(f"Informe {label}.")
        return parsed

    @staticmethod
    def _format_number(value: float) -> str:
        if abs(value - round(value)) < 0.000001:
            return str(int(round(value)))
        return f"{value:.4f}".rstrip("0").rstrip(".")

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

        self.inventory_delete_button = QPushButton("Excluir")
        self.inventory_delete_button.setObjectName("dangerButton")
        self.inventory_delete_button.setEnabled(False)
        self.inventory_delete_button.clicked.connect(self._request_inventory_delete)

        self.inventory_save_button = QPushButton("Salvar item")
        self.inventory_save_button.clicked.connect(self._request_inventory_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.inventory_new_button)
        actions.addWidget(self.inventory_delete_button)
        actions.addWidget(self.inventory_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
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

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, record_fields, 0, 0, 6)
        add_widget(fields_layout, technical_fields, 0, 6, 6)

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

        self.service_order_delete_button = QPushButton("Excluir")
        self.service_order_delete_button.setObjectName("dangerButton")
        self.service_order_delete_button.setEnabled(False)
        self.service_order_delete_button.clicked.connect(self._request_service_order_delete)

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

        self.sector_delete_button = QPushButton("Excluir")
        self.sector_delete_button.setObjectName("dangerButton")
        self.sector_delete_button.setEnabled(False)
        self.sector_delete_button.clicked.connect(self._request_sector_delete)

        self.sector_save_button = QPushButton("Salvar setor")
        self.sector_save_button.clicked.connect(self._request_sector_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.sector_new_button)
        actions.addWidget(self.sector_delete_button)
        actions.addWidget(self.sector_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
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

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, identity_panel, 0, 0, 7)
        add_widget(fields_layout, security_panel, 0, 7, 5)

        user_details_title = QLabel("DADOS COMPLETOS")
        user_details_title.setObjectName("formGroupTitle")
        self.user_full_summary = create_summary_text()

        self.user_form_status = QLabel("")
        self.user_form_status.setObjectName("mutedText")

        self.user_new_button = QPushButton("Novo")
        self.user_new_button.setObjectName("secondaryButton")
        self.user_new_button.clicked.connect(self.clear_user_form)

        self.user_delete_button = QPushButton("Excluir")
        self.user_delete_button.setObjectName("dangerButton")
        self.user_delete_button.setEnabled(False)
        self.user_delete_button.clicked.connect(self._request_user_delete)

        self.user_reset_password_button = QPushButton("Redefinir senha")
        self.user_reset_password_button.setObjectName("secondaryButton")
        self.user_reset_password_button.clicked.connect(self._request_user_password_reset)

        self.user_save_button = QPushButton("Salvar usuario")
        self.user_save_button.clicked.connect(self._request_user_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.user_new_button)
        actions.addWidget(self.user_delete_button)
        actions.addWidget(self.user_reset_password_button)
        actions.addWidget(self.user_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(password_reset_panel)
        layout.addWidget(password_reset_details_title)
        layout.addWidget(self.password_reset_full_summary)
        layout.addWidget(self.password_reset_form_status)
        layout.addLayout(actions)

        return panel
