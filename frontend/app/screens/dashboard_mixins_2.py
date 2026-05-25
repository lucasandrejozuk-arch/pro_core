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
        self.data_title.setText(title or self.module_labels.get(module_key, "Registros"))
        self.data_description.setText(self.module_descriptions.get(module_key, ""))
        self.module_search_input.setPlaceholderText(self._module_search_placeholder(module_key))
        self._reset_pagination_for_module(module_key)
        self._populate_current_table(self._filtered_rows())
        if module_key == "sectors":
            self._refresh_sector_operational_status()
        elif module_key == "users":
            self._refresh_user_operational_status()
        elif module_key == "resource_access":
            self._refresh_resource_access_operational_status()
        elif module_key == "password_resets":
            self._refresh_password_reset_operational_status()
        elif module_key == "audit_logs":
            self._refresh_audit_operational_status()

    def _populate_current_table(self, rows: list[dict[str, Any]]) -> None:
        columns = self.current_columns
        filtered_rows = list(rows)
        if self.active_module_key == "service_orders":
            visible_rows = self._current_page_rows(filtered_rows)
            self._update_pagination_controls(len(filtered_rows))
        else:
            visible_rows = filtered_rows
        self.current_rows = visible_rows
        if hasattr(self, "record_count_label"):
            total = len(self.all_rows)
            shown = len(visible_rows)
            if shown == total:
                self.record_count_label.setText(f"{total} registro(s)")
            else:
                if self.active_module_key == "service_orders":
                    self.record_count_label.setText(
                        f"{shown} registro(s) na pagina | "
                        f"{len(filtered_rows)} filtrado(s) de {total}"
                    )
                else:
                    self.record_count_label.setText(f"{shown} de {total} registro(s)")
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for label, _key in columns])
        self.table.setRowCount(len(visible_rows))
        self._resize_table_to_content(self.table, len(visible_rows), minimum=190, maximum=16777215)

        if not visible_rows:
            message = "Nenhum registro encontrado."
            if self.module_search_input.text().strip():
                message = "Nenhum registro encontrado para a busca."
            self.empty_label.setText(message)
            self.empty_label.show()
            self._refresh_module_guidance()
            return

        self.empty_label.hide()
        for row_index, row in enumerate(visible_rows):
            for column_index, (_label, key) in enumerate(columns):
                value = self._format_value(row.get(key))
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_index, column_index, item)
            self.table.setRowHeight(row_index, 34)

        if self.active_module_key in self.searchable_module_keys:
            self.table.selectRow(0)

    @staticmethod
    def _resize_table_to_content(table, row_count: int, minimum: int, maximum: int) -> None:
        header_height = table.horizontalHeader().height() if table.horizontalHeader() else 34
        row_height = table.verticalHeader().defaultSectionSize()
        target_height = header_height + max(row_count, 1) * row_height + 12
        table.setMinimumHeight(minimum)
        if maximum >= 10000:
            table.setMaximumHeight(maximum)
            return
        table.setMaximumHeight(max(minimum, min(target_height, maximum)))

    def _apply_current_filter(self) -> None:
        if self.active_module_key not in self.searchable_module_keys:
            return
        if self.active_module_key == "service_orders":
            self.current_page = 1
        self._populate_current_table(self._filtered_rows())

    def _reset_pagination_for_module(self, module_key: str) -> None:
        self.current_page = 1
        self.total_pages = 1
        if hasattr(self, "pagination_bar"):
            self.pagination_bar.setVisible(module_key == "service_orders")
        if hasattr(self, "pagination_size_combo"):
            index = self.pagination_size_combo.findData(self.page_size)
            if index >= 0:
                self.pagination_size_combo.blockSignals(True)
                self.pagination_size_combo.setCurrentIndex(index)
                self.pagination_size_combo.blockSignals(False)

    def _current_page_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self.page_size <= 0:
            return list(rows)
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return rows[start:end]

    def _update_pagination_controls(self, filtered_count: int) -> None:
        if self.page_size <= 0:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (filtered_count + self.page_size - 1) // self.page_size)
        self.current_page = max(1, min(self.current_page, self.total_pages))
        if hasattr(self, "pagination_label"):
            self.pagination_label.setText(f"Pagina {self.current_page} de {self.total_pages}")
        if hasattr(self, "pagination_prev_button"):
            self.pagination_prev_button.setEnabled(self.current_page > 1)
        if hasattr(self, "pagination_next_button"):
            self.pagination_next_button.setEnabled(self.current_page < self.total_pages)

    def _set_page_size(self, *_args: Any) -> None:
        if not hasattr(self, "pagination_size_combo"):
            return
        self.page_size = int(self.pagination_size_combo.currentData() or 10)
        self.current_page = 1
        if self.active_module_key == "service_orders":
            self._populate_current_table(self._filtered_rows())

    def _go_previous_page(self) -> None:
        if self.active_module_key != "service_orders":
            return
        if self.current_page <= 1:
            return
        self.current_page -= 1
        self._populate_current_table(self._filtered_rows())

    def _go_next_page(self) -> None:
        if self.active_module_key != "service_orders":
            return
        if self.current_page >= self.total_pages:
            return
        self.current_page += 1
        self._populate_current_table(self._filtered_rows())

    def _filtered_rows(self) -> list[dict[str, Any]]:
        rows = list(self.all_rows)
        if self.active_module_key == "inventory" and hasattr(
            self, "_inventory_row_matches_stock_group"
        ):
            rows = [row for row in rows if self._inventory_row_matches_stock_group(row)]
        search_text = self.module_search_input.text().strip().lower()
        if not search_text:
            return rows
        return [row for row in rows if self._row_matches_search(row, search_text)]

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
        previous_settings = dict(getattr(self, "current_settings", {}) or {})
        if self.active_module_key != "settings":
            self._set_active_module("settings")
        self.current_rows = []
        self.all_rows = []
        self.current_columns = []
        self.data_title.setText("Configuracoes")
        self.data_description.setText(self.module_descriptions["settings"])
        self.empty_label.hide()
        self.table.hide()
        merged_settings = dict(previous_settings)
        merged_settings.update(settings)
        self._populate_settings_form(merged_settings)

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
            self.dashboard_alerts_layout.addWidget(empty_message)
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
