from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardEquipmentMixin:
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
        self.equipment_context_label.setText(
            f"_EQUIPAMENTO: {self._equipment_label(equipment).upper()}_"
        )
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
        self.board_context_label.setText(f"_OBJETO: {self._board_label(board).upper()}_")
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

    def _open_equipment_create_dialog(self) -> None:
        dialog = EquipmentAssetDialog(
            "NOVO EQUIPAMENTO",
            self._equipment_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_create_requested.emit(dialog.payload())

    def _open_equipment_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR EQUIPAMENTO",
            self._equipment_dialog_fields(),
            equipment,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_update_requested.emit(str(equipment["id"]), dialog.payload())

    def _request_equipment_delete(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Remover equipamento",
            "Remover o equipamento selecionado?",
        ):
            return
        self.equipment_delete_requested.emit(str(equipment["id"]))

    def _request_equipment_import(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Importar Equipamentos - CSV",
            "",
            "CSV (*.csv)",
        )
        if not file_path:
            return
        answer = QMessageBox.question(
            self,
            "Importar Equipamentos",
            "Deseja substituir os equipamentos atuais? Escolha Nao para apenas adicionar.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return
        replace = answer == QMessageBox.StandardButton.Yes
        self.equipment_import_requested.emit(file_path, replace)

    def _request_equipment_export(self, export_format: str) -> None:
        extension = export_format.lower()
        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar Equipamentos",
            f"equipamentos.{extension}",
            f"{extension.upper()} (*.{extension})",
        )
        if not file_path:
            return
        if not file_path.lower().endswith(f".{extension}"):
            file_path = f"{file_path}.{extension}"
        self.equipment_export_requested.emit(export_format, file_path)

    def _request_equipment_defect_cases_open(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        self.equipment_defect_cases_requested.emit(str(equipment["id"]))

    def open_equipment_defect_cases_dialog(
        self,
        equipment_id: str,
        list_cases: Callable[[str], list[dict[str, Any]]],
        create_case: Callable[[dict[str, Any]], dict[str, Any]],
        update_case: Callable[[str, dict[str, Any]], dict[str, Any]],
        delete_case: Callable[[str], None],
    ) -> None:
        equipment = self._find_by_id(self.current_rows, equipment_id)
        if not equipment:
            self.set_equipment_form_status("Equipamento nao encontrado.", is_error=True)
            return
        dialog = EquipmentDefectCasesDialog(
            equipment,
            list_cases=list_cases,
            create_case=create_case,
            update_case=update_case,
            delete_case=delete_case,
            parent=self,
        )
        dialog.exec()
        self.equipment_form_status.setText("Casos de defeito atualizados.")

    def _request_equipment_board_create(self) -> None:
        equipment = self._selected_equipment()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "NOVO OBJETO VINCULADO",
            self._board_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_board_create_requested.emit(str(equipment["id"]), dialog.payload())

    def _open_equipment_board_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment or not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR OBJETO VINCULADO",
            self._board_dialog_fields(),
            board,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_board_update_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            dialog.payload(),
        )

    def _request_equipment_board_delete(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment or not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Remover objeto",
            "Remover o objeto vinculado selecionado?",
        ):
            return
        self.equipment_board_delete_requested.emit(str(equipment["id"]), str(board["id"]))

    def _request_equipment_component_create(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        if not equipment:
            self.set_equipment_form_status("Selecione um equipamento.", is_error=True)
            return
        if not board:
            self.set_equipment_form_status("Selecione um objeto vinculado.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "NOVO COMPONENTE",
            self._component_dialog_fields(),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_component_create_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            dialog.payload(),
        )

    def _open_equipment_component_edit_dialog(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        if not equipment or not board or not component:
            self.set_equipment_form_status("Selecione um componente.", is_error=True)
            return
        dialog = EquipmentAssetDialog(
            "EDITAR COMPONENTE",
            self._component_dialog_fields(),
            component,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.equipment_component_update_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            str(component["id"]),
            dialog.payload(),
        )

    def _request_equipment_component_delete(self) -> None:
        equipment = self._selected_equipment()
        board = self._selected_equipment_board()
        component = self._selected_equipment_component()
        if not equipment or not board or not component:
            self.set_equipment_form_status("Selecione um componente.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Remover componente",
            "Remover o componente selecionado?",
        ):
            return
        self.equipment_component_delete_requested.emit(
            str(equipment["id"]),
            str(board["id"]),
            str(component["id"]),
        )
