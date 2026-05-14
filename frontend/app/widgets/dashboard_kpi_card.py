from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout


class DashboardKpiCard(QFrame):
    clicked = Signal(str)

    def __init__(
        self,
        key: str,
        marker: str,
        label: str,
        accent: str,
        module_key: str | None = None,
    ) -> None:
        super().__init__()
        self.key = key
        self.module_key = module_key
        self.setObjectName("dashboardKpiCard")
        self.setMinimumHeight(112)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setProperty("accent", accent)
        if module_key:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        marker_label = QLabel(marker)
        marker_label.setObjectName("dashboardCardMarker")
        marker_label.setStyleSheet(f"color: {accent};")

        self.value_label = QLabel("0")
        self.value_label.setObjectName("dashboardCardValue")
        self.value_label.setStyleSheet(f"color: {accent};")

        label_widget = QLabel(label)
        label_widget.setObjectName("dashboardCardLabel")
        label_widget.setWordWrap(True)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        top_layout.addWidget(marker_label)
        top_layout.addStretch()
        top_layout.addWidget(self.value_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.addLayout(top_layout)
        layout.addWidget(label_widget)

    def set_value(self, value: Any) -> None:
        self.value_label.setText(str(value))

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if self.module_key:
            self.clicked.emit(self.module_key)
        super().mousePressEvent(event)
