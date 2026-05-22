from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardEquipmentActionsMixin:
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
