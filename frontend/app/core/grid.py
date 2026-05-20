from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLayout, QWidget

GRID_COLUMNS = 12


def create_grid(spacing: int = 8, margins: tuple[int, int, int, int] = (0, 0, 0, 0)) -> QGridLayout:
    layout = QGridLayout()
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    configure_grid(layout)
    return layout


def configure_grid(layout: QGridLayout) -> QGridLayout:
    for column in range(GRID_COLUMNS):
        layout.setColumnStretch(column, 1)
    return layout


def add_widget(
    layout: QGridLayout,
    widget: QWidget,
    row: int,
    column: int = 0,
    span: int = GRID_COLUMNS,
) -> None:
    layout.addWidget(widget, row, column, 1, span)


def add_layout(
    layout: QGridLayout,
    child_layout: QLayout,
    row: int,
    column: int = 0,
    span: int = GRID_COLUMNS,
) -> None:
    layout.addLayout(child_layout, row, column, 1, span)


def span_for_items(items_per_row: int) -> int:
    safe_items_per_row = max(1, min(items_per_row, GRID_COLUMNS))
    return max(1, GRID_COLUMNS // safe_items_per_row)
