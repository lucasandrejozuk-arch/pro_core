from __future__ import annotations

from PySide6.QtWidgets import QTextEdit


def create_summary_text(min_height: int = 84, max_height: int = 120) -> QTextEdit:
    summary = QTextEdit()
    summary.setObjectName("summaryText")
    summary.setReadOnly(True)
    summary.setMinimumHeight(min_height)
    summary.setMaximumHeight(max_height)
    return summary
