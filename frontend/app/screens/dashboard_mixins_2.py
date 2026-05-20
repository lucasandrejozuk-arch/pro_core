from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin2:
    def render_loading(self, title: str, module_key: str) -> None:
        self._set_active_module(module_key)
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText(title)
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.empty_label.setText("Carregando dados...")
        self.empty_label.show()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def render_error(self, title: str, message: str, module_key: str) -> None:
        self._set_active_module(module_key)
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText(title)
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.empty_label.setText(message)
        self.empty_label.show()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def render_dashboard(self, summary: dict[str, Any] | None = None) -> None:
        self._set_active_module("dashboard")
        self.current_rows = []
        self.all_rows = []
        self.current_columns = []
        self.title_label.setText("Painel Principal")
        self.dashboard_section_title.setText("VISAO GERAL")
        self.empty_label.hide()
        self.table.hide()
        self._apply_dashboard_summary(summary or {})

    def render_rows(
        self,
        title: str,
        rows: list[dict[str, Any]],
        columns: list[tuple[str, str]],
        module_key: str,
    ) -> None:
        if module_key == "equipment":
            self._render_equipment_rows(title, rows)
            return

        self._set_active_module(module_key)
        self.all_rows = list(rows)
        self.current_columns = list(columns)
        self.data_title.setText(title)
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.module_search_input.setPlaceholderText(self._module_search_placeholder(module_key))
        self._populate_current_table(self._filtered_rows())

    def _populate_current_table(self, rows: list[dict[str, Any]]) -> None:
        columns = self.current_columns
        self.current_rows = rows
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for label, _key in columns])
        self.table.setRowCount(len(rows))

        if not rows:
            message = "Nenhum registro encontrado."
            if self.module_search_input.text().strip():
                message = "Nenhum registro encontrado para a busca."
            self.empty_label.setText(message)
            self.empty_label.show()
            return

        self.empty_label.hide()
        for row_index, row in enumerate(rows):
            for column_index, (_label, key) in enumerate(columns):
                value = self._format_value(row.get(key))
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)
            self.table.setRowHeight(row_index, 34)

        if self.active_module_key in self.searchable_module_keys:
            self.table.selectRow(0)

    def _apply_current_filter(self) -> None:
        if self.active_module_key not in self.searchable_module_keys:
            return
        self._populate_current_table(self._filtered_rows())

    def _filtered_rows(self) -> list[dict[str, Any]]:
        search_text = self.module_search_input.text().strip().lower()
        if not search_text:
            return list(self.all_rows)
        return [row for row in self.all_rows if self._row_matches_search(row, search_text)]

    def _row_matches_search(self, value: Any, search_text: str) -> bool:
        if isinstance(value, dict):
            return any(self._row_matches_search(child, search_text) for child in value.values())
        if isinstance(value, list):
            return any(self._row_matches_search(child, search_text) for child in value)
        return search_text in self._format_value(value).lower()

    def _module_search_placeholder(self, module_key: str) -> str:
        label = self.module_labels.get(module_key, "registros")
        return f"BUSCAR {label.upper()}..."

    def render_settings(self, settings: dict[str, Any]) -> None:
        self._set_active_module("settings")
        self.current_rows = []
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText("Configuracoes")
        self.data_description.setText(self.module_descriptions["settings"])
        self.empty_label.hide()
        self.table.hide()
        self._populate_settings_form(settings)

    @staticmethod
    def _build_module_card(title: str, description: str) -> QFrame:
        card = QFrame()
        card.setObjectName("moduleCard")
        card.setMinimumHeight(88)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        description_label = QLabel(description)
        description_label.setObjectName("cardMeta")
        description_label.setWordWrap(True)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return card

    def _apply_dashboard_summary(self, summary: dict[str, Any]) -> None:
        greeting = str(summary.get("greeting") or "Painel operacional do PRO CORE.")
        self.dashboard_greeting_label.setText(greeting)
        self.dashboard_last_refresh_label.setText(str(summary.get("last_refresh") or ""))

        cards = summary.get("cards") or {}
        for key, card in self.dashboard_cards.items():
            card.set_value(cards.get(key, 0))

        self._clear_layout(self.dashboard_alerts_layout)
        alerts = summary.get("alerts") or []
        if not alerts:
            empty_message = QLabel("Nenhum aviso no momento")
            empty_message.setObjectName("emptyAlertText")
            empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dashboard_alerts_layout.addStretch()
            self.dashboard_alerts_layout.addWidget(empty_message)
            self.dashboard_alerts_layout.addStretch()
            return

        for alert in alerts:
            row = QFrame()
            row.setObjectName("dashboardAlertRow")
            row.setProperty("level", str(alert.get("level") or "info"))
            message = QLabel(str(alert.get("message") or "Alerta operacional."))
            message.setWordWrap(True)
            layout = QHBoxLayout(row)
            layout.setContentsMargins(8, 4, 8, 4)
            layout.addWidget(message)
            self.dashboard_alerts_layout.addWidget(row)
        self.dashboard_alerts_layout.addStretch()

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _render_bar_chart(self, layout: QVBoxLayout, values: dict[str, float]) -> None:
        self._clear_layout(layout)
        if not values:
            empty = QLabel("Sem dados para grafico.")
            empty.setObjectName("mutedText")
            layout.addWidget(empty)
            return
        maximum = max(max(values.values()), 1)
        for label, value in values.items():
            row = QHBoxLayout()
            name = QLabel(label)
            name.setObjectName("mutedText")
            name.setMinimumWidth(120)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(round((value / maximum) * 100))
            bar.setFormat(f"{self._format_number(value)}")
            row.addWidget(name)
            row.addWidget(bar, 1)
            layout.addLayout(row)

    def _install_input_guards(self) -> None:
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QComboBox, QAbstractSpinBox)):
                widget.installEventFilter(self)

    def _mark_active_nav(self, module_key: str) -> None:
        for key, button in self.module_buttons.items():
            is_active = key == module_key
            button.setChecked(is_active)
            button.setProperty("active", "true" if is_active else "false")
            button.style().unpolish(button)
            button.style().polish(button)
