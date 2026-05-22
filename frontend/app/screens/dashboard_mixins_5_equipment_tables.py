from __future__ import annotations

from typing import Any


class DashboardEquipmentTablesMixin:
    def _render_equipment_rows(self, title: str, rows: list[dict[str, Any]]) -> None:
        self._set_active_module("equipment")
        self.current_rows = rows
        self.data_title.setText(title)
        self.empty_label.hide()
        self.table.hide()
        self._refresh_equipment_table()
        if not rows:
            self.set_equipment_form_status("Nenhum equipamento cadastrado.")
        else:
            self.set_equipment_form_status("Equipamentos carregados.")
        self._refresh_equipment_operational_status()

    def _populate_equipment_form(self, equipment: dict[str, Any]) -> None:
        self._select_equipment_by_id(str(equipment["id"]))

    def _refresh_equipment_table(self) -> None:
        term = self.equipment_search_input.text().strip().lower()
        self.equipment_visible_rows = [
            row
            for row in self.current_rows
            if self._row_matches(
                row,
                ("id", "category", "brand", "model", "special_number"),
                term,
            )
        ]
        self._fill_equipment_table(
            self.equipment_table,
            self.equipment_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("category")),
                lambda row: self._format_value(row.get("brand")),
                lambda row: self._format_value(row.get("model")),
                lambda row: self._format_value(row.get("special_number")),
            ],
        )
        if not self.equipment_visible_rows:
            self.selected_equipment_id = None
            self.equipment_full_summary.setPlainText(
                "SELECIONE UM EQUIPAMENTO PARA VER OS DADOS COMPLETOS."
            )
            self._refresh_equipment_boards_table()
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_table,
            self.equipment_visible_rows,
            self.selected_equipment_id,
        ):
            self.equipment_table.selectRow(0)

    def _refresh_equipment_boards_table(self) -> None:
        equipment = self._selected_equipment()
        boards = equipment.get("boards") if equipment else []
        term = self.board_search_input.text().strip().lower()
        self.equipment_board_visible_rows = [
            board
            for board in (boards or [])
            if self._row_matches(board, ("id", "name", "special_number", "model", "revision"), term)
        ]
        self._fill_equipment_table(
            self.equipment_boards_table,
            self.equipment_board_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("name")),
                lambda row: self._format_value(row.get("special_number")),
                lambda row: self._format_value(row.get("model")),
                lambda row: self._format_value(row.get("revision")),
            ],
        )
        if not self.equipment_board_visible_rows:
            self.selected_equipment_board_id = None
            self.selected_equipment_component_id = None
            self.board_full_summary.setPlainText("SELECIONE UM OBJETO PARA VER OS DADOS COMPLETOS.")
            self._refresh_equipment_components_table()
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_boards_table,
            self.equipment_board_visible_rows,
            self.selected_equipment_board_id,
        ):
            self.equipment_boards_table.selectRow(0)

    def _refresh_equipment_components_table(self) -> None:
        board = self._selected_equipment_board()
        components = board.get("components") if board else []
        term = self.component_search_input.text().strip().lower()
        self.equipment_component_visible_rows = [
            component
            for component in (components or [])
            if self._row_matches(
                component,
                ("id", "category", "name", "part_number", "location", "notes"),
                term,
            )
        ]
        self._fill_equipment_table(
            self.equipment_components_table,
            self.equipment_component_visible_rows,
            [
                lambda row: self._short_id(row.get("id")),
                lambda row: self._format_value(row.get("category")),
                lambda row: self._format_value(row.get("name")),
                lambda row: self._format_value(row.get("part_number")),
                lambda row: self._format_value(row.get("location")),
                lambda row: self._format_value(row.get("notes")),
            ],
        )
        if not self.equipment_component_visible_rows:
            self.selected_equipment_component_id = None
            self.component_full_summary.setPlainText(
                "SELECIONE UM COMPONENTE PARA VER OS DADOS COMPLETOS."
            )
            self._update_equipment_action_state()
            return

        if not self._select_visible_table_row(
            self.equipment_components_table,
            self.equipment_component_visible_rows,
            self.selected_equipment_component_id,
        ):
            self.equipment_components_table.selectRow(0)

    def _handle_equipment_table_selection(self) -> None:
        selected_items = self.equipment_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_visible_rows):
            return
        equipment = self.equipment_visible_rows[row_index]
        self.current_selected_record = dict(equipment)
        self.current_selected_summary = self._format_equipment_full_summary(equipment)
        self.selected_equipment_id = str(equipment["id"])
        self.selected_equipment_board_id = None
        self.selected_equipment_component_id = None
        self.equipment_full_summary.setPlainText(self._format_equipment_full_summary(equipment))
        self.equipment_context_label.setText(f"Equipamento: {self._equipment_label(equipment)}")
        self._refresh_equipment_boards_table()
        self._update_equipment_action_state()

    def _handle_equipment_board_table_selection(self) -> None:
        selected_items = self.equipment_boards_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_board_visible_rows):
            return
        board = self.equipment_board_visible_rows[row_index]
        self.current_selected_record = dict(board)
        self.current_selected_summary = self._format_equipment_board_summary(board)
        self.selected_equipment_board_id = str(board["id"])
        self.selected_equipment_component_id = None
        self.board_full_summary.setPlainText(self._format_equipment_board_summary(board))
        self.board_context_label.setText(f"Objeto: {self._board_label(board)}")
        self._refresh_equipment_components_table()
        self._update_equipment_action_state()

    def _handle_equipment_component_table_selection(self) -> None:
        selected_items = self.equipment_components_table.selectedItems()
        if not selected_items:
            return
        row_index = selected_items[0].row()
        if row_index >= len(self.equipment_component_visible_rows):
            return
        component = self.equipment_component_visible_rows[row_index]
        self.current_selected_record = dict(component)
        self.current_selected_summary = self._format_equipment_component_summary(component)
        self.selected_equipment_component_id = str(component["id"])
        self.component_full_summary.setPlainText(
            self._format_equipment_component_summary(component)
        )
        self._update_equipment_action_state()
