from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.i18n import apply_language_to_widgets, current_ui_language
from frontend.app.screens.dashboard_dialogs_assets import confirm_destructive_action
from frontend.app.widgets import create_summary_text


class DefectCaseEditDialog(QDialog):
    def __init__(
        self,
        equipment: dict[str, Any],
        values: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("NOVO CASO DE DEFEITO" if not values else "EDITAR CASO DE DEFEITO")
        self.setModal(True)
        self.setObjectName("assetDialog")
        self._payload: dict[str, Any] = {}
        values = values or {}

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ex.: Falha de comunicacao do modulo")
        self.title_input.setText(str(values.get("title") or ""))

        self.board_combo = QComboBox()
        self.board_combo.addItem("(Sem objeto especifico)", None)
        for board in equipment.get("boards") or []:
            self.board_combo.addItem(
                str(board.get("name") or board.get("model") or "Objeto vinculado"),
                str(board.get("id")),
            )
        self._select_combo_value(self.board_combo, str(values.get("board_id") or ""))

        self.symptom_input = self._make_text("Descreva sintomas observados", values.get("symptom"))
        self.root_cause_input = self._make_text("Descreva a causa raiz", values.get("root_cause"))
        self.solution_input = self._make_text("Descreva a solucao aplicada", values.get("solution"))
        self.notes_input = self._make_text("Observacoes adicionais (opcional)", values.get("notes"))

        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Titulo:", self.title_input)
        form.addRow("Objeto vinculado:", self.board_combo)
        form.addRow("Sintoma:", self.symptom_input)
        form.addRow("Causa raiz:", self.root_cause_input)
        form.addRow("Solucao:", self.solution_input)
        form.addRow("Observacoes:", self.notes_input)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorText")

        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self._accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(self.reject)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(save_button)
        actions.addWidget(cancel_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addLayout(actions)
        self.resize(520, 430)
        apply_language_to_widgets(current_ui_language(), self)

    def payload(self) -> dict[str, Any]:
        return dict(self._payload)

    def _accept(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            self.error_label.setText("Informe o titulo.")
            return
        self._payload = {
            "board_id": self.board_combo.currentData() or None,
            "title": title,
            "symptom": self.symptom_input.toPlainText().strip() or None,
            "root_cause": self.root_cause_input.toPlainText().strip() or None,
            "solution": self.solution_input.toPlainText().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }
        self.accept()

    @staticmethod
    def _make_text(placeholder: str, value: Any) -> QTextEdit:
        widget = QTextEdit()
        widget.setPlaceholderText(placeholder)
        widget.setPlainText(str(value or ""))
        widget.setMinimumHeight(72)
        return widget

    @staticmethod
    def _select_combo_value(combo: QComboBox, value: str) -> None:
        if not value:
            return
        for index in range(combo.count()):
            if str(combo.itemData(index)) == value:
                combo.setCurrentIndex(index)
                return


class EquipmentDefectCasesDialog(QDialog):
    def __init__(
        self,
        equipment: dict[str, Any],
        list_cases: Callable[[str], list[dict[str, Any]]],
        create_case: Callable[[dict[str, Any]], dict[str, Any]],
        update_case: Callable[[str, dict[str, Any]], dict[str, Any]],
        delete_case: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.equipment = equipment
        self._list_cases = list_cases
        self._create_case = create_case
        self._update_case = update_case
        self._delete_case = delete_case
        self._cases: list[dict[str, Any]] = []
        self._selected_case_id: str | None = None

        self.setWindowTitle(f"CASOS DE DEFEITO - EQUIPAMENTO {str(equipment.get('id') or '')[:8]}")
        self.setObjectName("assetDialog")
        self.setMinimumSize(920, 520)
        self._build_ui()
        self._reload_cases()

    def _build_ui(self) -> None:
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar casos de defeito...")
        self.search_input.textChanged.connect(self._reload_cases)

        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "TITULO", "SINTOMA", "CAUSA RAIZ", "ATUALIZADO"]
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self._handle_selection)

        self.new_button = QPushButton("+Caso de Defeito")
        self.new_button.clicked.connect(self._create)
        self.edit_button = QPushButton("Editar")
        self.edit_button.setObjectName("secondaryButton")
        self.edit_button.clicked.connect(self._edit)
        self.remove_button = QPushButton("Remover")
        self.remove_button.setObjectName("dangerButton")
        self.remove_button.clicked.connect(self._remove)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(self.new_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.remove_button)
        actions.addStretch()

        self.summary = create_summary_text(110, 150)
        self.summary.setPlainText("Selecione um caso para ver detalhes.")

        close_button = QPushButton("Fechar")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.accept)
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_row.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table, 1)
        layout.addLayout(actions)
        layout.addWidget(QLabel("RESUMO:"))
        layout.addWidget(self.summary)
        layout.addLayout(close_row)
        apply_language_to_widgets(current_ui_language(), self)

    def _reload_cases(self) -> None:
        try:
            self._cases = self._list_cases(self.search_input.text().strip())
        except Exception as exc:
            self.summary.setPlainText(f"Falha ao carregar casos: {exc}")
            self._cases = []
        self._fill_table()

    def _fill_table(self) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(len(self._cases))
        for row_index, defect_case in enumerate(self._cases):
            values = [
                str(defect_case.get("id") or "")[:8],
                str(defect_case.get("title") or ""),
                str(defect_case.get("symptom") or ""),
                str(defect_case.get("root_cause") or ""),
                str(defect_case.get("updated_at") or ""),
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, str(defect_case.get("id") or ""))
                self.table.setItem(row_index, column_index, item)
        self.table.blockSignals(False)
        if self._cases:
            self.table.selectRow(0)
        else:
            self._selected_case_id = None
            self.summary.setPlainText("Nenhum caso encontrado.")
        self._update_actions()

    def _handle_selection(self) -> None:
        selected_items = self.table.selectedItems()
        if not selected_items:
            self._selected_case_id = None
            self.summary.setPlainText("Selecione um caso para ver detalhes.")
            self._update_actions()
            return
        row_index = selected_items[0].row()
        if row_index >= len(self._cases):
            return
        defect_case = self._cases[row_index]
        self._selected_case_id = str(defect_case.get("id") or "")
        self.summary.setPlainText(self._format_case_summary(defect_case))
        self._update_actions()

    def _create(self) -> None:
        dialog = DefectCaseEditDialog(self.equipment, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            saved = self._create_case(dialog.payload())
            self._selected_case_id = str(saved.get("id") or "")
        except Exception as exc:
            self.summary.setPlainText(f"Falha ao salvar caso: {exc}")
            return
        self._reload_cases()

    def _edit(self) -> None:
        defect_case = self._selected_case()
        if not defect_case:
            return
        dialog = DefectCaseEditDialog(self.equipment, defect_case, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._update_case(str(defect_case["id"]), dialog.payload())
        except Exception as exc:
            self.summary.setPlainText(f"Falha ao atualizar caso: {exc}")
            return
        self._reload_cases()

    def _remove(self) -> None:
        defect_case = self._selected_case()
        if not defect_case:
            return
        if not confirm_destructive_action(
            self,
            "Remover caso de defeito",
            "Remover o caso de defeito selecionado?",
        ):
            return
        try:
            self._delete_case(str(defect_case["id"]))
        except Exception as exc:
            self.summary.setPlainText(f"Falha ao remover caso: {exc}")
            return
        self._selected_case_id = None
        self._reload_cases()

    def _selected_case(self) -> dict[str, Any] | None:
        for defect_case in self._cases:
            if str(defect_case.get("id")) == self._selected_case_id:
                return defect_case
        return None

    def _update_actions(self) -> None:
        has_case = bool(self._selected_case_id)
        self.edit_button.setEnabled(has_case)
        self.remove_button.setEnabled(has_case)

    def _format_case_summary(self, defect_case: dict[str, Any]) -> str:
        board_name = "Equipamento"
        board_id = str(defect_case.get("board_id") or "")
        for board in self.equipment.get("boards") or []:
            if str(board.get("id")) == board_id:
                board_name = str(board.get("name") or board.get("model") or "Objeto vinculado")
                break
        return "\n".join(
            [
                f"ID: {defect_case.get('id') or '-'}",
                f"Objeto vinculado: {board_name}",
                f"Titulo: {defect_case.get('title') or '-'}",
                f"Sintoma: {defect_case.get('symptom') or '-'}",
                f"Causa raiz: {defect_case.get('root_cause') or '-'}",
                f"Solucao: {defect_case.get('solution') or '-'}",
                f"Observacoes: {defect_case.get('notes') or '-'}",
                f"Atualizado em: {defect_case.get('updated_at') or '-'}",
            ]
        )
