from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from frontend.app.widgets import create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardToolTabsMixin:
    def _build_tools_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("FERRAMENTAS")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Calculadoras tecnicas e apoio operacional em fluxo rapido.")
        subtitle.setObjectName("mutedText")
        subtitle.setWordWrap(True)

        self.tools_status_label = QLabel("Carregando ferramentas disponiveis para o perfil.")
        self.tools_status_label.setObjectName("statusBanner")
        self.tools_status_label.setProperty("level", "warning")
        self.tools_status_label.setWordWrap(True)

        self.tools_availability_label = QLabel("0 ferramentas liberadas")
        self.tools_availability_label.setObjectName("moduleCountBadge")
        self.tools_specialties_label = QLabel("Especialidades: -")
        self.tools_specialties_label.setObjectName("moduleActionHint")
        self.tools_specialties_label.setWordWrap(True)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        header_text = QVBoxLayout()
        header_text.setContentsMargins(0, 0, 0, 0)
        header_text.setSpacing(2)
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_row.addLayout(header_text, 1)
        header_row.addWidget(self.tools_availability_label, 0, Qt.AlignmentFlag.AlignTop)

        self.tools_tabs = QTabWidget()
        self.tools_tabs.setObjectName("toolsTabs")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addLayout(header_row)
        layout.addWidget(self.tools_status_label)
        layout.addWidget(self.tools_specialties_label)
        layout.addWidget(self.tools_tabs, 1)
        return panel

    def render_tools(self, tools: list[dict[str, Any]]) -> None:
        self._set_active_module("tools")
        self.current_tools = list(tools)
        self.tools_tabs.clear()
        tool_ids = {str(tool.get("id") or "") for tool in tools}
        if not tool_ids:
            self._set_tools_operational_status([], {})
            self.tools_tabs.addTab(
                self._build_tool_message("Nenhuma ferramenta disponivel."),
                "Aviso",
            )
            return
        tools_by_specialty = self._group_tools_by_specialty(tool_ids)
        self._set_tools_operational_status(tools, tools_by_specialty)
        for specialty_name, specialty_tools in tools_by_specialty.items():
            tab_widget = self._build_specialty_tab(specialty_name, specialty_tools)
            self.tools_tabs.addTab(tab_widget, self._specialty_label(specialty_name))

    def _set_tools_operational_status(
        self,
        tools: list[dict[str, Any]],
        tools_by_specialty: dict[str, list[tuple[str, str, Any, list[tuple[str, str]]]]],
    ) -> None:
        available_count = len(tools)
        active_specialties = [
            self._specialty_label(name)
            for name, specialty_tools in tools_by_specialty.items()
            if specialty_tools
        ]
        if not available_count:
            message = "Nenhuma ferramenta foi liberada para o perfil atual."
            level = "warning"
            specialties_text = "Especialidades: nenhuma"
        else:
            specialty_count = len(active_specialties)
            message = (
                f"{available_count} ferramenta(s) disponivel(is) em "
                f"{specialty_count} especialidade(s). Use os calculos como apoio rapido "
                "ao diagnostico, orçamento e reposicao."
            )
            level = "info"
            specialties_text = f"Especialidades: {', '.join(active_specialties)}"

        self.tools_status_label.setText(message)
        self.tools_status_label.setProperty("level", level)
        self.tools_status_label.style().unpolish(self.tools_status_label)
        self.tools_status_label.style().polish(self.tools_status_label)
        self.tools_availability_label.setText(f"{available_count} ferramentas liberadas")
        self.tools_specialties_label.setText(specialties_text)

    def _group_tools_by_specialty(
        self, tool_ids: set[str]
    ) -> dict[str, list[tuple[str, str, Any, list[tuple[str, str]]]]]:
        specialty_map = {
            "eletrica": [
                ("ohm", "Lei de Ohm", self._calculate_ohm_tool, []),
                (
                    "power",
                    "Potencia",
                    self._calculate_power_tool,
                    [
                        ("Tensao (V)", "voltage"),
                        ("Corrente (A)", "current"),
                        ("Resistencia (ohm)", "resistance"),
                    ],
                ),
                (
                    "led",
                    "LED",
                    self._calculate_led_tool,
                    [
                        ("Fonte (V)", "supply"),
                        ("LED Vf (V)", "forward"),
                        ("Corrente (mA)", "current_ma"),
                    ],
                ),
                (
                    "divider",
                    "Divisor",
                    self._calculate_divider_tool,
                    [("Vin (V)", "vin"), ("R1 (ohm)", "r1"), ("R2 (ohm)", "r2")],
                ),
                (
                    "battery",
                    "Bateria",
                    self._calculate_battery_tool,
                    [
                        ("Capacidade (mAh)", "capacity"),
                        ("Consumo (mA)", "load"),
                        ("Eficiencia (%)", "efficiency"),
                    ],
                ),
                (
                    "resistor_color",
                    "Codigo de Cor",
                    self._calculate_resistor_color_tool,
                    [
                        ("Digito 1", "digit_1"),
                        ("Digito 2", "digit_2"),
                        ("Multiplicador", "multiplier"),
                    ],
                ),
                (
                    "resistor_assoc",
                    "Assoc. Resistores",
                    self._calculate_resistor_assoc_tool,
                    [("Resistores", "values")],
                ),
                ("awg", "AWG/mm2", self._calculate_awg_tool, [("AWG", "awg")]),
            ],
            "operacional": [
                (
                    "sla",
                    "SLA",
                    self._calculate_sla_tool,
                    [("Horas contratadas", "hours"), ("Horas consumidas", "used")],
                ),
                (
                    "stock_reorder",
                    "Reposicao Estoque",
                    self._calculate_stock_reorder_tool,
                    [("Estoque atual", "current"), ("Minimo", "minimum"), ("Lote", "batch")],
                ),
            ],
        }
        available_specialties = {}
        for specialty, tools_list in specialty_map.items():
            available_tools = [
                (tool_id, title, calc, fields)
                for tool_id, title, calc, fields in tools_list
                if tool_id in tool_ids
            ]
            if available_tools or specialty == "eletrica":
                available_specialties[specialty] = available_tools
        if not available_specialties:
            available_specialties["geral"] = []
        return available_specialties

    @staticmethod
    def _specialty_label(specialty_name: str) -> str:
        labels = {
            "eletrica": "Eletrica",
            "operacional": "Operacional",
            "geral": "Geral",
        }
        return labels.get(specialty_name, specialty_name.title())

    def _build_specialty_tab(
        self,
        specialty_name: str,
        specialty_tools: list[tuple[str, str, Any, list[tuple[str, str]]]],
    ) -> QWidget:
        panel = QFrame()
        panel.setObjectName("formSubPanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        if not specialty_tools:
            label = QLabel(f"Nenhuma ferramenta de {specialty_name.lower()} disponivel.")
            label.setObjectName("mutedText")
            layout.addWidget(label)
            layout.addStretch()
            return panel

        context = QLabel(
            f"{self._specialty_label(specialty_name)}: {len(specialty_tools)} "
            "ferramenta(s) liberada(s)."
        )
        context.setObjectName("moduleActionHint")

        specialty_tabs = QTabWidget()
        specialty_tabs.setObjectName("specialtyTabs")

        history_text = create_summary_text(48, 64)
        history_text.setPlainText(f"Ultimos calculos de {specialty_name.lower()} aparecerao aqui.")

        for tool_id, tool_title, calculator, fields in specialty_tools:
            if tool_id == "ohm" and fields == []:
                tool_widget = self._build_ohm_tool()
            else:
                tool_widget = self._build_generic_tool(
                    tool_title, fields, calculator, specialty_name
                )
            tool_widget.parent_specialty_text = history_text
            specialty_tabs.addTab(tool_widget, tool_title)

        history_section = QFrame()
        history_section.setObjectName("formSubPanel")
        history_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        history_layout = QVBoxLayout(history_section)
        history_layout.setContentsMargins(8, 8, 8, 8)
        history_layout.setSpacing(6)

        history_label = QLabel(f"HISTORICO - {specialty_name.upper()}")
        history_label.setObjectName("formGroupTitle")

        history_layout.addWidget(history_label)
        history_layout.addWidget(history_text)

        workspace = QHBoxLayout()
        workspace.setContentsMargins(0, 0, 0, 0)
        workspace.setSpacing(10)
        workspace.addWidget(specialty_tabs, 3)
        workspace.addWidget(history_section, 1)

        layout.addWidget(context)
        layout.addLayout(workspace, 1)

        return panel

    def _build_tool_message(self, message: str) -> QWidget:
        widget = QWidget()
        label = QLabel(message)
        label.setObjectName("mutedText")
        layout = QVBoxLayout(widget)
        layout.addWidget(label)
        layout.addStretch()
        return widget
