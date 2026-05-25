from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QPushButton,
    QSizePolicy,
    QTableWidget,
)

from frontend.app.core.display import DisplayProfile, detect_display_profile
from frontend.app.core.grid import span_for_items
from frontend.app.core.icons import build_icon
from frontend.app.themes.tokens import EQUIPMENT_SCROLL_MIN_HEIGHT


class DashboardLayoutMixin:
    def _recommended_dashboard_columns(self, width: int | None = None) -> int:
        active_width = width if width is not None else self.width()
        if active_width < 1500 or self.ui_scale_value >= 1.22:
            return 2
        return 4

    def _apply_responsive_form_guards(self) -> None:
        wrap_rows = self.width() < 1500 or self.ui_scale_value >= 1.22
        row_policy = (
            QFormLayout.RowWrapPolicy.WrapLongRows
            if wrap_rows
            else QFormLayout.RowWrapPolicy.DontWrapRows
        )
        for form_layout in self.findChildren(QFormLayout):
            form_layout.setRowWrapPolicy(row_policy)
            form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    def _configure_sidebar_button(self, button: QPushButton, icon_name: str, tooltip: str) -> None:
        button.setText("")
        button.setToolTip(tooltip)
        button.setIcon(build_icon(icon_name, self.sidebar_icon_color))
        button.setIconSize(self.sidebar_icon_size)
        button.setFixedSize(44, 44)
        self.sidebar_buttons_by_icon[button] = icon_name

    def _apply_compact_density(self) -> None:
        for frame in self.findChildren(QFrame):
            layout = frame.layout()
            if layout is None:
                continue

            object_name = frame.objectName()
            if object_name == "formPanel":
                layout.setContentsMargins(10, 10, 10, 10)
                layout.setSpacing(8)
            elif object_name in {"formSubPanel", "workflowPanel", "equipmentSection"}:
                layout.setContentsMargins(8, 8, 8, 8)
                layout.setSpacing(6)

            if object_name in {"formSubPanel", "toolPanel", "toolResultPanel", "adminDetailsPanel"}:
                frame.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Maximum,
                )
                layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for form_layout in self.findChildren(QFormLayout):
            form_layout.setHorizontalSpacing(8)
            form_layout.setVerticalSpacing(6)

        for table in self.findChildren(QTableWidget):
            table.verticalHeader().setDefaultSectionSize(34)
            table.horizontalHeader().setMinimumSectionSize(96)
            table.setShowGrid(False)
            table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def apply_sidebar_icon_color(self, color: str) -> None:
        self.sidebar_icon_color = color
        for button, icon_name in self.sidebar_buttons_by_icon.items():
            button.setIcon(build_icon(icon_name, color))
            button.setIconSize(self.sidebar_icon_size)

    def apply_record_editor_icon_colors(self, inactive_color: str, active_color: str) -> None:
        self.record_editor_icon_color = inactive_color
        self.record_editor_active_icon_color = active_color
        for button in getattr(self, "summary_copy_buttons", []):
            button.setIcon(build_icon("copy", inactive_color, 18))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel and isinstance(watched, (QComboBox, QAbstractSpinBox)):
            return True
        try:
            if (
                watched is self.table.viewport()
                and event.type() == QEvent.Type.MouseButtonPress
                and self.table.itemAt(event.position().toPoint()) is None
            ):
                self._clear_current_selection()
        except RuntimeError:
            return False
        for equipment_table in (
            getattr(self, "equipment_table", None),
            getattr(self, "equipment_boards_table", None),
            getattr(self, "equipment_components_table", None),
        ):
            try:
                if (
                    equipment_table is not None
                    and watched is equipment_table.viewport()
                    and event.type() == QEvent.Type.MouseButtonPress
                    and equipment_table.itemAt(event.position().toPoint()) is None
                ):
                    self._clear_equipment_selection_from_table(equipment_table)
            except RuntimeError:
                continue

        return super().eventFilter(watched, event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if not hasattr(self, "dashboard_grid_layout"):
            return
        self._set_dashboard_grid_columns(self._recommended_dashboard_columns())
        self._apply_responsive_form_guards()
        self._sync_scroll_policy(self.active_module_key)
        self._position_record_editor()

    def apply_display_profile(self, profile: DisplayProfile | None = None) -> None:
        active_profile = profile or detect_display_profile()
        self.ui_scale_min = active_profile.ui_scale_min
        self.ui_scale_max = active_profile.ui_scale_max
        self.ui_scale_value = active_profile.ui_scale
        if hasattr(self, "settings_ui_scale_slider"):
            self.configure_ui_scale(
                active_profile.ui_scale_min,
                active_profile.ui_scale_max,
                active_profile.ui_scale,
            )
        self.sidebar_expanded_width = active_profile.sidebar_width
        self.sidebar_collapsed_width = active_profile.collapsed_sidebar_width
        self.sidebar_margin = active_profile.content_margin
        self.sidebar_collapsed = False
        self.sidebar.setFixedWidth(self.sidebar_expanded_width)
        self.content_layout.setContentsMargins(
            active_profile.content_margin,
            active_profile.content_margin,
            active_profile.content_margin,
            active_profile.content_margin,
        )
        self.content_layout.setSpacing(active_profile.section_spacing)
        self.dashboard_grid_layout.setSpacing(max(6, active_profile.section_spacing // 2))
        self.record_editor_width = int(max(860, min(round(920 * active_profile.ui_scale), 1080)))
        self._set_dashboard_grid_columns(active_profile.dashboard_columns)
        self._apply_responsive_form_guards()
        self._sync_active_module_space(self.active_module_key)
        self._position_sidebar()
        self._position_record_editor()

    def _position_sidebar(self) -> None:
        if not hasattr(self, "sidebar"):
            return

        self.sidebar.setFixedWidth(self.sidebar_expanded_width)

    def _reset_content_row_stretches(self) -> None:
        if not hasattr(self, "content_layout"):
            return
        for row in range(10):
            self.content_layout.setRowStretch(row, 0)

    def _sync_active_module_space(self, module_key: str) -> None:
        self._reset_content_row_stretches()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._sync_scroll_policy(module_key)
        if module_key != "dashboard":
            self.content_layout.setRowStretch(1, 1)

    def _sync_scroll_policy(self, module_key: str) -> None:
        if not hasattr(self, "main_scroll_area"):
            return
        if module_key == "equipment" and self.height() >= EQUIPMENT_SCROLL_MIN_HEIGHT:
            self.main_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            return
        self.main_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def _position_record_editor(self) -> None:
        if not hasattr(self, "generic_form_column") or not hasattr(self, "record_toggle_rail"):
            return

        is_record_module = self.active_module_key in self.record_module_keys
        is_open = not self.record_editor_collapsed
        is_docked = self.active_module_key == "service_orders"
        should_show_rail = is_record_module and is_docked
        self.record_toggle_rail.setVisible(should_show_rail)
        if not should_show_rail:
            self.generic_form_column.hide()
            return

        top = self.command_bar.height() + 14 if hasattr(self, "command_bar") else 14
        bottom = self.session_footer.height() + 14 if hasattr(self, "session_footer") else 14
        overlay_height = max(420, self.height() - top - bottom)
        right_margin = 12
        rail_width = self.record_toggle_rail.width()
        rail_x = max(0, self.width() - rail_width - right_margin)
        self.record_toggle_rail.setGeometry(rail_x, top, rail_width, overlay_height)
        self.record_toggle_rail.raise_()

        if not is_open:
            self.generic_form_column.hide()
            return

        content_width = max(860, self.width() - self.sidebar.width() - 80)
        max_width = max(760, content_width - 48)
        width = min(max_width, max(820, min(round(content_width * 0.48), 980)))
        width = max(760, width)
        panel_gap = 12
        panel_x = max(0, rail_x - panel_gap - width)
        self.generic_form_column.setParent(self)
        self.generic_form_column.setFixedWidth(width)
        self.generic_form_column.setGeometry(panel_x, top, width, overlay_height)
        self.generic_form_column.show()
        self.generic_form_column.raise_()

    def _set_dashboard_grid_columns(self, columns: int) -> None:
        normalized_columns = max(1, min(columns, 4))
        if normalized_columns == self.dashboard_grid_columns:
            return

        while self.dashboard_grid_layout.count():
            self.dashboard_grid_layout.takeAt(0)

        card_span = span_for_items(normalized_columns)
        for index, key in enumerate(self.dashboard_card_order):
            self.dashboard_grid_layout.addWidget(
                self.dashboard_cards[key],
                index // normalized_columns,
                (index % normalized_columns) * card_span,
                1,
                card_span,
            )
        self.dashboard_grid_columns = normalized_columns

    def _toggle_sidebar(self) -> None:
        self._set_sidebar_collapsed(False)

    def _set_sidebar_collapsed(self, collapsed: bool) -> None:
        self.sidebar_collapsed = False
        self.sidebar_nav_container.setVisible(True)
        self.logout_button.setVisible(True)
        self.exit_button.setVisible(True)
        self._sync_module_visibility()
        self.sidebar_layout.setContentsMargins(8, 8, 8, 8)
        self.sidebar.setFixedWidth(self.sidebar_expanded_width)
        self._position_sidebar()
