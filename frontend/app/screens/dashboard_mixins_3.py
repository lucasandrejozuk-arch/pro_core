from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from frontend.app.widgets import create_summary_text


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
