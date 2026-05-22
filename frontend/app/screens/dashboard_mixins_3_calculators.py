from __future__ import annotations

import math

from PySide6.QtWidgets import QLineEdit


class DashboardToolCalculatorMixin:
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
        bands = int(self._required_float(inputs["bands"].text(), "faixas"))
        digit_1 = int(self._required_float(inputs["digit_1"].text(), "digito 1"))
        digit_2 = int(self._required_float(inputs["digit_2"].text(), "digito 2"))
        multiplier = self._required_float(inputs["multiplier"].text(), "multiplicador")
        tolerance_input = inputs.get("tolerance")
        tolerance = self._optional_float(tolerance_input.text()) if tolerance_input else None
        if bands not in {4, 5}:
            raise ValueError("Faixas deve ser 4 ou 5.")
        if digit_1 < 0 or digit_1 > 9 or digit_2 < 0 or digit_2 > 9:
            raise ValueError("Digitos devem ficar entre 0 e 9.")
        if bands == 4:
            resistance = ((digit_1 * 10) + digit_2) * multiplier
        else:
            digit_3 = int(self._required_float(inputs["digit_3"].text(), "digito 3"))
            if digit_3 < 0 or digit_3 > 9:
                raise ValueError("Digito 3 deve ficar entre 0 e 9.")
            resistance = ((digit_1 * 100) + (digit_2 * 10) + digit_3) * multiplier

        tolerance_text = (
            f" | Tolerancia: {self._format_number(tolerance)}%"
            if tolerance is not None and tolerance > 0
            else ""
        )
        return f"Resistencia: {self._format_number(resistance)} ohm{tolerance_text}"

    def _calculate_resistor_assoc_tool(self, inputs: dict[str, QLineEdit]) -> str:
        association_type = inputs["association_type"].text().strip().lower()
        if association_type not in {"serie", "paralelo"}:
            raise ValueError("Tipo deve ser 'serie' ou 'paralelo'.")

        expected_count = int(self._required_float(inputs["count"].text(), "quantidade"))
        if expected_count < 2:
            raise ValueError("Quantidade deve ser pelo menos 2.")

        values = [
            self._required_float(token, "resistor")
            for token in inputs["values"].text().replace(";", ",").split(",")
            if token.strip()
        ]
        if not values or any(value <= 0 for value in values):
            raise ValueError("Informe resistores positivos separados por virgula.")
        if len(values) != expected_count:
            raise ValueError("Quantidade informada deve corresponder ao total de resistores.")

        if association_type == "serie":
            result = sum(values)
            return f"Equivalente (serie): {self._format_number(result)} ohm"

        result = 1 / sum(1 / value for value in values)
        return f"Equivalente (paralelo): {self._format_number(result)} ohm"

    def _calculate_awg_tool(self, inputs: dict[str, QLineEdit]) -> str:
        scale = inputs["scale"].text().strip().lower()
        value = self._required_float(inputs["value"].text(), "valor")

        if scale == "awg":
            awg = value
            if awg < -5 or awg > 50:
                raise ValueError("AWG fora da faixa -5 a 50.")
            diameter = 0.127 * (92 ** ((36 - awg) / 39))
            area = (math.pi / 4) * (diameter**2)
            return (
                f"Area: {self._format_number(area)} mm2 | "
                f"Diametro: {self._format_number(diameter)} mm"
            )

        if scale == "mm2":
            area = value
            if area <= 0:
                raise ValueError("Area em mm2 deve ser maior que zero.")
            diameter = math.sqrt((4 * area) / math.pi)
            awg = 36 - (39 * (math.log(diameter / 0.127) / math.log(92)))
            return (
                f"AWG aproximado: {self._format_number(awg)} | "
                f"Diametro: {self._format_number(diameter)} mm"
            )

        raise ValueError("Escala deve ser 'awg' ou 'mm2'.")

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
