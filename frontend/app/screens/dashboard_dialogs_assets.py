from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.i18n import apply_language_to_widgets, current_ui_language, translate_ui_text


def confirm_destructive_action(parent: QWidget, title: str, message: str) -> bool:
    language = current_ui_language()
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setWindowTitle(translate_ui_text(title, language))
    dialog.setText(translate_ui_text(message, language))
    dialog.setInformativeText(translate_ui_text("Esta acao nao pode ser desfeita.", language))
    dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    dialog.setDefaultButton(QMessageBox.StandardButton.No)
    yes_button = dialog.button(QMessageBox.StandardButton.Yes)
    no_button = dialog.button(QMessageBox.StandardButton.No)
    if yes_button is not None:
        yes_button.setText(translate_ui_text("Excluir", language))
    if no_button is not None:
        no_button.setText(translate_ui_text("Cancelar", language))
    return dialog.exec() == QMessageBox.StandardButton.Yes


class EquipmentAssetDialog(QDialog):
    def __init__(
        self,
        title: str,
        fields: list[dict[str, Any]],
        values: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setObjectName("assetDialog")
        self.fields = fields
        self.inputs: dict[str, QLineEdit | QTextEdit] = {}
        self._payload: dict[str, Any] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setSpacing(4)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        values = values or {}
        for field in fields:
            key = str(field["key"])
            if field.get("multiline"):
                input_widget = QTextEdit()
                input_widget.setPlaceholderText(str(field.get("placeholder") or ""))
                input_widget.setPlainText(str(values.get(key) or ""))
                input_widget.setMinimumHeight(72)
                input_widget.setMaximumHeight(96)
            else:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(str(field.get("placeholder") or ""))
                input_widget.setText(str(values.get(key) or ""))
            self.inputs[key] = input_widget
            form_layout.addRow(str(field["label"]), input_widget)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorText")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)
        button_layout.addStretch()
        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self._accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(form_layout)
        layout.addWidget(self.error_label)
        layout.addLayout(button_layout)
        self.resize(420, 280)
        apply_language_to_widgets(current_ui_language(), self)

    def payload(self) -> dict[str, Any]:
        return dict(self._payload)

    def _accept(self) -> None:
        try:
            self._payload = self._build_payload()
        except ValueError as exc:
            self.error_label.setText(str(exc))
            return
        self.accept()

    def _build_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for field in self.fields:
            key = str(field["key"])
            input_widget = self.inputs[key]
            if isinstance(input_widget, QTextEdit):
                raw_value = input_widget.toPlainText().strip()
            else:
                raw_value = input_widget.text().strip()

            if field.get("required") and not raw_value:
                raise ValueError(f"Informe {str(field['label']).replace(':', '').lower()}.")

            if field.get("money"):
                payload[key] = self._normalize_money(raw_value)
                continue

            payload[key] = raw_value or None

        return payload

    @staticmethod
    def _normalize_money(raw_value: str) -> str:
        value = raw_value.strip()
        if not value:
            return "0"
        if "," in value:
            value = value.replace(".", "").replace(",", ".")
        try:
            decimal_value = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("Valor unitario deve ser numerico.") from exc
        if decimal_value < 0:
            raise ValueError("Valor unitario nao pode ser negativo.")
        return str(decimal_value)
