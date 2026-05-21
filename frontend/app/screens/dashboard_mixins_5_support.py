from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardEquipmentSupportMixin:
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
        self._resize_table_to_content(table, len(rows), minimum=table.minimumHeight(), maximum=280)
        table.blockSignals(False)

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

    @staticmethod
    def _equipment_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "category",
                "label": "Tipo:",
                "placeholder": "Tipo do equipamento",
                "required": True,
            },
            {"key": "brand", "label": "Marca:", "placeholder": "Marca do equipamento"},
            {"key": "model", "label": "Modelo:", "placeholder": "Modelo do equipamento"},
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, S120-CU320",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 1499,90",
                "money": True,
            },
            {
                "key": "description",
                "label": "Notas:",
                "placeholder": "Observacoes gerais (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _board_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Nome:",
                "placeholder": "Nome do objeto vinculado",
                "required": True,
            },
            {
                "key": "special_number",
                "label": "No Especial:",
                "placeholder": "Ex.: A5E02814482, numero de inventario",
            },
            {"key": "model", "label": "Modelo / Tipo:", "placeholder": "Modelo / tipo da placa"},
            {"key": "revision", "label": "Revisao:", "placeholder": "Ex.: A01, B02, Rev.C"},
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 980,00",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Notas:",
                "placeholder": "Observacoes (opcional)",
                "multiline": True,
            },
        ]

    @staticmethod
    def _component_dialog_fields() -> list[dict[str, Any]]:
        return [
            {
                "key": "name",
                "label": "Dados:",
                "placeholder": "Dados do componente",
                "required": True,
            },
            {"key": "category", "label": "Categoria:", "placeholder": "Categoria do componente"},
            {
                "key": "part_number",
                "label": "Modelo / Part Number:",
                "placeholder": "Ex.: BC547B, IRFZ44N",
            },
            {
                "key": "location",
                "label": "Localizacao:",
                "placeholder": "Ex.: Gaveta A3, Bandeja 2",
            },
            {
                "key": "unit_price",
                "label": "Valor Unitario (R$):",
                "placeholder": "Ex.: 12,50",
                "money": True,
            },
            {
                "key": "notes",
                "label": "Observacoes:",
                "placeholder": "Observacoes",
                "multiline": True,
            },
        ]
