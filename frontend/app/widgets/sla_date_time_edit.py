from __future__ import annotations

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QDateTimeEdit


class SlaDateTimeEdit(QDateTimeEdit):
    def __init__(self) -> None:
        super().__init__()
        self._has_value = False
        self._programmatic_change = False
        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.setDateTime(QDateTime.currentDateTime())
        self.setToolTip("Selecionar prazo SLA")
        self.dateTimeChanged.connect(self._mark_value_selected)

    def clear(self) -> None:  # type: ignore[override]
        self._programmatic_change = True
        self._has_value = False
        self.setDateTime(QDateTime.currentDateTime())
        self._programmatic_change = False

    def setText(self, value: str) -> None:
        value = value.strip()
        if not value:
            self.clear()
            return

        parsed = QDateTime.fromString(value, "yyyy-MM-ddTHH:mm:ss")
        if not parsed.isValid():
            parsed = QDateTime.fromString(value, "yyyy-MM-dd HH:mm")
        if parsed.isValid():
            self._programmatic_change = True
            self.setDateTime(parsed)
            self._programmatic_change = False
            self._has_value = True

    def text(self) -> str:  # type: ignore[override]
        if not self._has_value:
            return ""
        return self.dateTime().toString("yyyy-MM-ddTHH:mm:ss")

    def _mark_value_selected(self) -> None:
        if not self._programmatic_change:
            self._has_value = True
