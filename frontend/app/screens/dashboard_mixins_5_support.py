from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)

from frontend.app.screens.dashboard_mixins_5_equipment_fields import (
    DashboardEquipmentFieldsMixin,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardEquipmentSupportMixin(DashboardEquipmentFieldsMixin):
    def _remember_equipment_resume_selection(self) -> None:
        settings = QSettings("PRO CORE", "PRO CORE")
        settings.setValue("guided/equipment_id", self.selected_equipment_id or "")
        settings.setValue("guided/equipment_board_id", self.selected_equipment_board_id or "")
        settings.setValue(
            "guided/equipment_component_id",
            self.selected_equipment_component_id or "",
        )

    def _restore_equipment_resume_selection(self) -> None:
        settings = QSettings("PRO CORE", "PRO CORE")
        self.selected_equipment_id = str(settings.value("guided/equipment_id", "") or "") or None
        self.selected_equipment_board_id = (
            str(settings.value("guided/equipment_board_id", "") or "") or None
        )
        self.selected_equipment_component_id = (
            str(settings.value("guided/equipment_component_id", "") or "") or None
        )

    def _update_equipment_action_state(self) -> None:
        has_equipment = bool(self.selected_equipment_id)
        has_board = bool(self.selected_equipment_board_id)
        has_component = bool(self.selected_equipment_component_id)
        self.equipment_edit_button.setEnabled(has_equipment)
        self.equipment_remove_button.setEnabled(has_equipment)
        self.equipment_defect_cases_button.setEnabled(has_equipment)
        self.board_add_button.setEnabled(has_equipment)
        self.board_edit_button.setEnabled(has_board)
        self.board_remove_button.setEnabled(has_board)
        self.component_add_button.setEnabled(has_board)
        self.component_edit_button.setEnabled(has_component)
        self.component_remove_button.setEnabled(has_component)
        self._refresh_equipment_operational_status()

    def _refresh_equipment_operational_status(self) -> None:
        if not hasattr(self, "equipment_operational_status"):
            return

        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        search_text = self.equipment_search_input.text().strip()

        if not self.current_rows:
            self._set_equipment_operational_status(
                "Nenhum equipamento cadastrado. Cadastre um equipamento ou importe CSV.",
                "warning",
            )
            self._set_equipment_hierarchy_status(
                "Hierarquia: nenhum equipamento disponivel.",
                "warning",
            )
            return

        if not self.equipment_visible_rows:
            suffix = f' para a busca "{search_text}"' if search_text else ""
            self._set_equipment_operational_status(
                f"Nenhum equipamento encontrado{suffix}. Ajuste a busca ou cadastre novo item.",
                "warning",
            )
            self._set_equipment_hierarchy_status(
                "Hierarquia: selecione um equipamento para carregar objetos e componentes.",
                "warning",
            )
            return

        if equipment is None:
            self._set_equipment_operational_status(
                f"{len(self.equipment_visible_rows)} equipamento(s) visivel(is). "
                "Selecione um equipamento para gerenciar a hierarquia.",
                "warning",
            )
            self._set_equipment_hierarchy_status(
                "Hierarquia: nenhum equipamento selecionado.",
                "warning",
            )
            return

        boards = equipment.get("boards") or []
        components_count = sum(len(board_item.get("components") or []) for board_item in boards)
        self._set_equipment_operational_status(
            f"Equipamento selecionado: {self._equipment_label(equipment)}. "
            f"{len(boards)} objeto(s) vinculado(s), {components_count} componente(s).",
            "info",
        )

        if board is None:
            self._set_equipment_hierarchy_status(
                "Hierarquia: adicione ou selecione um objeto vinculado para gerenciar componentes.",
                "warning",
            )
            return

        board_components = board.get("components") or []
        if component is None:
            self._set_equipment_hierarchy_status(
                f"Objeto selecionado: {self._board_label(board)}. "
                f"{len(board_components)} componente(s) vinculado(s).",
                "info",
            )
            return

        self._set_equipment_hierarchy_status(
            f"Componente selecionado: {self._format_value(component.get('name')) or '-'} "
            f"em {self._board_label(board)}.",
            "info",
        )

    def _set_equipment_operational_status(self, message: str, level: str) -> None:
        self.equipment_operational_status.setText(message)
        self.equipment_operational_status.setProperty("level", level)
        self.equipment_operational_status.setVisible(bool(message))
        self.equipment_operational_status.style().unpolish(self.equipment_operational_status)
        self.equipment_operational_status.style().polish(self.equipment_operational_status)

    def _set_equipment_hierarchy_status(self, message: str, level: str) -> None:
        self.equipment_hierarchy_status.setText(message)
        self.equipment_hierarchy_status.setProperty("level", level)
        self.equipment_hierarchy_status.setVisible(bool(message))
        self.equipment_hierarchy_status.style().unpolish(self.equipment_hierarchy_status)
        self.equipment_hierarchy_status.style().polish(self.equipment_hierarchy_status)

    def _selected_equipment(self) -> dict[str, Any] | None:
        return self._find_by_id(self.current_rows, self.selected_equipment_id)

    def _selected_equipment_board(self) -> dict[str, Any] | None:
        equipment = self._selected_equipment()
        if not equipment:
            return None
        return self._find_by_id(equipment.get("boards") or [], self.selected_equipment_board_id)

    def _selected_equipment_component(self) -> dict[str, Any] | None:
        board = self._selected_equipment_board()
        if not board:
            return None
        return self._find_by_id(
            board.get("components") or [],
            self.selected_equipment_component_id,
        )

    def _select_equipment_by_id(self, equipment_id: str) -> None:
        self.selected_equipment_id = equipment_id
        self._select_visible_table_row(
            self.equipment_table,
            self.equipment_visible_rows,
            equipment_id,
        )

    def _fill_equipment_table(
        self,
        table: QTableWidget,
        rows: list[dict[str, Any]],
        getters: list,
    ) -> None:
        table.blockSignals(True)
        table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, getter in enumerate(getters):
                item = QTableWidgetItem(str(getter(row) or ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setData(Qt.ItemDataRole.UserRole, str(row.get("id") or ""))
                table.setItem(row_index, column_index, item)
            table.setRowHeight(row_index, 34)
        self._resize_table_to_content(
            table,
            len(rows),
            minimum=table.minimumHeight(),
            maximum=self._equipment_table_maximum_height(table),
        )
        self._set_equipment_list_count(table, len(rows))
        table.blockSignals(False)

    def _set_equipment_list_count(self, table: QTableWidget, count: int) -> None:
        if table is self.equipment_table:
            badge = self.equipment_count_badge
        elif table is self.equipment_boards_table:
            badge = self.board_count_badge
        else:
            badge = self.component_count_badge
        label = "item" if count == 1 else "itens"
        badge.setText(f"{count} {label}")

    def _clear_equipment_selection_from_table(self, table: QTableWidget) -> None:
        if table is self.equipment_table:
            self._clear_equipment_selection()
        elif table is self.equipment_boards_table:
            self._clear_equipment_board_selection()
        elif table is self.equipment_components_table:
            self._clear_equipment_component_selection()

    def _clear_equipment_selection(self) -> None:
        self._clear_table_selection(self.equipment_table)
        self._clear_table_selection(self.equipment_boards_table)
        self._clear_table_selection(self.equipment_components_table)
        self.selected_equipment_id = None
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.current_selected_record = None
        self.current_selected_summary = "Nenhum item selecionado."
        self.equipment_board_visible_rows = []
        self.equipment_component_visible_rows = []
        self.equipment_boards_table.setRowCount(0)
        self.equipment_components_table.setRowCount(0)
        self.equipment_full_summary.setPlainText(
            "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
        )
        self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
        self.component_full_summary.setPlainText(
            "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
        )
        self.equipment_context_label.setText("Nenhum equipamento selecionado")
        self.board_context_label.setText("Nenhum objeto vinculado selecionado")
        self._set_equipment_list_count(self.equipment_boards_table, 0)
        self._set_equipment_list_count(self.equipment_components_table, 0)
        self._update_record_summary_panel()
        self._remember_equipment_resume_selection()
        self._update_equipment_action_state()

    def _clear_equipment_board_selection(self) -> None:
        self._clear_table_selection(self.equipment_boards_table)
        self._clear_table_selection(self.equipment_components_table)
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.current_selected_record = self._selected_equipment()
        self.current_selected_summary = (
            self._format_equipment_full_summary(self.current_selected_record)
            if self.current_selected_record
            else "Nenhum item selecionado."
        )
        self.equipment_component_visible_rows = []
        self.equipment_components_table.setRowCount(0)
        self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
        self.component_full_summary.setPlainText(
            "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
        )
        self.board_context_label.setText("Nenhum objeto vinculado selecionado")
        self._set_equipment_list_count(self.equipment_components_table, 0)
        self._update_record_summary_panel()
        self._remember_equipment_resume_selection()
        self._update_equipment_action_state()

    def _clear_equipment_component_selection(self) -> None:
        self._clear_table_selection(self.equipment_components_table)
        self.selected_equipment_component_id = None
        self.current_selected_record = self._selected_equipment_board()
        self.current_selected_summary = (
            self._format_equipment_board_summary(self.current_selected_record)
            if self.current_selected_record
            else "Nenhum item selecionado."
        )
        self.component_full_summary.setPlainText(
            "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
        )
        self._update_record_summary_panel()
        self._remember_equipment_resume_selection()
        self._update_equipment_action_state()

    @staticmethod
    def _clear_table_selection(table: QTableWidget) -> None:
        table.blockSignals(True)
        table.clearSelection()
        table.blockSignals(False)

    def _equipment_table_maximum_height(self, table: QTableWidget) -> int:
        if table is self.equipment_table:
            return 178
        return 150

    def _select_visible_table_row(
        self,
        table: QTableWidget,
        rows: list[dict[str, Any]],
        selected_id: str | None,
    ) -> bool:
        if not selected_id:
            return False
        for row_index, row in enumerate(rows):
            if str(row.get("id")) == selected_id:
                table.selectRow(row_index)
                return True
        return False

    @staticmethod
    def _find_by_id(rows: list[dict[str, Any]], row_id: str | None) -> dict[str, Any] | None:
        if not row_id:
            return None
        for row in rows:
            if str(row.get("id")) == row_id:
                return row
        return None

    @staticmethod
    def _row_matches(row: dict[str, Any], keys: tuple[str, ...], term: str) -> bool:
        if not term:
            return True
        return any(term in str(row.get(key) or "").lower() for key in keys)

    @staticmethod
    def _short_id(value: Any) -> str:
        text = str(value or "")
        return text[:8] if len(text) > 8 else text

    @staticmethod
    def _equipment_label(equipment: dict[str, Any]) -> str:
        return (
            " - ".join(
                part
                for part in [
                    str(equipment.get("category") or ""),
                    str(equipment.get("brand") or ""),
                    str(equipment.get("model") or ""),
                    str(equipment.get("special_number") or ""),
                ]
                if part
            )
            or "Equipamento sem descricao"
        )

    @staticmethod
    def _board_label(board: dict[str, Any]) -> str:
        return str(board.get("name") or board.get("model") or "Objeto vinculado")
