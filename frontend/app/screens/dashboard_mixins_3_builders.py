from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from frontend.app.widgets import create_summary_text


class DashboardToolBuilderMixin:
    def _build_ohm_tool(self) -> QWidget:
        widget = QWidget()
        form_panel = QFrame()
        form_panel.setObjectName("toolPanel")
        form_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(form_panel)

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
        self.ohm_result = create_summary_text(58, 86)
        self.ohm_result.setPlainText("")
        result_title = QLabel("Resultado")
        result_title.setObjectName("formGroupTitle")

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
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addLayout(form)
        result_layout = QVBoxLayout()
        result_layout.setSpacing(6)
        result_layout.setContentsMargins(8, 8, 8, 8)
        result_layout.addWidget(result_title)
        result_layout.addWidget(self.ohm_result)
        result_panel = QFrame()
        result_panel.setObjectName("toolResultPanel")
        result_panel.setLayout(result_layout)
        result_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        input_layout.addWidget(result_panel)
        input_layout.addStretch(1)
        input_layout.addWidget(calculate_button, 0, Qt.AlignmentFlag.AlignLeft)
        panel_layout.addLayout(input_layout)

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
        panel.setObjectName("toolPanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        inputs: dict[str, QLineEdit] = {}
        form = QFormLayout()
        form.setSpacing(8)
        for label, key in fields:
            input_widget = QLineEdit()
            input_widget.setPlaceholderText(label)
            inputs[key] = input_widget
            form.addRow(f"{label}:", input_widget)
        result = create_summary_text(58, 92)
        result_title = QLabel("Resultado")
        result_title.setObjectName("formGroupTitle")

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
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addLayout(form)
        result_layout = QVBoxLayout()
        result_layout.setSpacing(6)
        result_layout.setContentsMargins(8, 8, 8, 8)
        result_layout.addWidget(result_title)
        result_layout.addWidget(result)
        result_panel = QFrame()
        result_panel.setObjectName("toolResultPanel")
        result_panel.setLayout(result_layout)
        result_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        input_layout.addWidget(result_panel)
        input_layout.addStretch(1)
        input_layout.addWidget(calculate_button, 0, Qt.AlignmentFlag.AlignLeft)
        panel_layout.addLayout(input_layout)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(panel)
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
