from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
)

from frontend.app.core.display import DisplayProfile, detect_display_profile
from frontend.app.core.grid import span_for_items
from frontend.app.core.icons import build_icon
from frontend.app.widgets import create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin1:
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

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel and isinstance(watched, (QComboBox, QAbstractSpinBox)):
            return True
        if (
            watched is self.table.viewport()
            and event.type() == QEvent.Type.MouseButtonPress
            and self.table.itemAt(event.position().toPoint()) is None
        ):
            self._clear_current_selection()
        for equipment_table in (
            getattr(self, "equipment_table", None),
            getattr(self, "equipment_boards_table", None),
            getattr(self, "equipment_components_table", None),
        ):
            if (
                equipment_table is not None
                and watched is equipment_table.viewport()
                and event.type() == QEvent.Type.MouseButtonPress
                and equipment_table.itemAt(event.position().toPoint()) is None
            ):
                equipment_table.clearSelection()

        return super().eventFilter(watched, event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if not hasattr(self, "dashboard_grid_layout"):
            return
        if self.width() < 1320:
            self._set_dashboard_grid_columns(2)
        elif self.width() >= 1500:
            self._set_dashboard_grid_columns(4)
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
        self.record_editor_width = int(max(640, min(round(720 * active_profile.ui_scale), 900)))
        self._set_dashboard_grid_columns(active_profile.dashboard_columns)
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
        if module_key in self.record_module_keys:
            self.content_layout.setRowStretch(6, 1)
            return
        if module_key == "equipment":
            self.content_layout.setRowStretch(7, 1)
            return
        if module_key == "tools":
            self.content_layout.setRowStretch(8, 1)
            return
        if module_key == "settings":
            self.content_layout.setRowStretch(9, 1)
            return
        if module_key == "dashboard":
            self.content_layout.setRowStretch(5, 0)

    def _position_record_editor(self) -> None:
        if not hasattr(self, "generic_form_column"):
            return

        is_record_module = self.active_module_key in self.record_module_keys
        is_open = not self.record_editor_collapsed
        self.generic_form_column.setVisible(is_record_module and is_open)
        if not is_record_module or not is_open:
            return

        margin = 10
        available_width = max(320, self.generic_record_container.width() - margin)
        target_width = max(self.record_editor_width, round(available_width * 0.46))
        width = min(target_width, available_width)
        height = max(260, self.generic_record_container.height())
        x = max(0, self.generic_record_container.width() - width - margin)
        self.generic_form_column.setGeometry(x, 0, width, height)
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

    def set_user(self, user: dict[str, Any]) -> None:
        self.current_user = dict(user)
        role_key = str(user.get("role", ""))
        self.current_user_role = role_key
        role = self._format_value(role_key) or role_key.replace("_", " ").title()
        full_name = user.get("full_name", "Usuario")
        email = user.get("email", "")
        self.user_label.setText(f"{full_name} | {email} | Perfil: {role}")
        self.session_info_label.setText(
            "\n".join(
                [
                    "Sessao ativa",
                    str(full_name or "Usuario"),
                    str(email or "-"),
                    f"Perfil: {role}",
                ]
            )
        )
        if hasattr(self, "session_button"):
            self.session_button.setToolTip(self.session_info_label.text())
        self._sync_module_visibility()
        if "users_total" in self.dashboard_cards:
            self.dashboard_cards["users_total"].setVisible(role_key in {"admin", "manager"})
        if "customers_total" in self.dashboard_cards:
            self.dashboard_cards["customers_total"].setVisible(role_key in {"admin", "manager"})
        self._refresh_session_footer()

    def set_session_login_at(self, login_at: datetime | None) -> None:
        self.session_login_at = login_at
        self._refresh_session_footer()

    def _refresh_session_footer(self) -> None:
        if not hasattr(self, "session_footer_label"):
            return

        role = self._format_value(self.current_user.get("role")) or "Usuario"
        sector = (
            str(self.current_user.get("sector_name") or "").strip()
            or self._lookup_label(
                self.user_sectors,
                self.current_user.get("sector_id"),
                "name",
                "",
            )
            or "Sem setor"
        )
        if self.session_login_at is None:
            login_text = "-"
            elapsed_text = "00:00:00"
        else:
            login_text = self.session_login_at.strftime("%Y-%m-%d %H:%M:%S")
            total_seconds = max(0, int((datetime.now() - self.session_login_at).total_seconds()))
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.session_footer_label.setText(
            f"* Sessao: {role} | Setor: {sector} | Login: {login_text} | Tempo: {elapsed_text}"
        )

    def set_backend_connection_status(self, is_connected: bool) -> None:
        self.backend_status_dot.setProperty("level", "success" if is_connected else "error")
        self.backend_status_text.setText(
            "Backend: conectado" if is_connected else "Backend: desconectado"
        )
        self.backend_status_dot.style().unpolish(self.backend_status_dot)
        self.backend_status_dot.style().polish(self.backend_status_dot)

    def _set_footer_message(self, message: str, level: str = "info") -> None:
        self.footer_message_label.setText(message)
        self.footer_message_label.setProperty("level", level)
        self.footer_message_label.style().unpolish(self.footer_message_label)
        self.footer_message_label.style().polish(self.footer_message_label)

    def _set_inline_status(self, label: QLabel, message: str, is_error: bool = False) -> None:
        label.setObjectName("errorText" if is_error else "mutedText")
        label.setText(message)
        label.style().unpolish(label)
        label.style().polish(label)
        if message:
            self._set_footer_message(message, "error" if is_error else "success")

    def apply_branding(self, settings: dict[str, Any]) -> None:
        brand_name = str(
            settings.get("brand_name")
            or settings.get("trade_name")
            or settings.get("company_name")
            or "PRO CORE"
        ).strip()
        brand_subtitle = str(
            settings.get("brand_subtitle") or settings.get("trade_name") or "Assistencia tecnica"
        ).strip()
        self.sidebar_title.setText(brand_name or "PRO CORE")
        self.sidebar_text.setText(brand_subtitle or "Assistencia tecnica")
        self.sidebar.setToolTip(
            f"{brand_name or 'PRO CORE'}\n{brand_subtitle or 'Assistencia tecnica'}"
        )
        self.setWindowTitle(f"{brand_name or 'PRO CORE'} - {self.title_label.text()}")

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

    def _set_record_editor_open(self, is_open: bool) -> None:
        self.record_editor_collapsed = not is_open
        if hasattr(self, "command_editor_button"):
            self.command_editor_button.setText("Fechar editor" if is_open else "Editor")
        if is_open:
            self._show_record_editor_dialog()
        elif self.record_editor_dialog is not None:
            self.record_editor_dialog.close()

    def _open_record_editor(self) -> None:
        if self.active_module_key not in self.record_module_keys:
            return
        self._set_record_editor_open(self.record_editor_collapsed)

    def _show_record_editor_dialog(self) -> None:
        if self.record_editor_dialog is not None:
            self.record_editor_dialog.raise_()
            self.record_editor_dialog.activateWindow()
            return

        dialog = QDialog(self)
        dialog.setObjectName("assetDialog")
        dialog.setWindowTitle(
            f"Editor - {self.module_labels.get(self.active_module_key, 'Registro')}"
        )
        dialog.resize(self.record_editor_width, max(560, self.height() - 180))
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)
        self.generic_form_column.setParent(dialog)
        self.generic_form_column.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.generic_form_column.show()
        layout.addWidget(self.generic_form_column)
        self.record_editor_popup_layout = layout
        self.record_editor_dialog = dialog
        dialog.finished.connect(self._restore_record_editor_from_dialog)
        dialog.show()

    def _restore_record_editor_from_dialog(self) -> None:
        if self.record_editor_dialog is None:
            return
        self.generic_form_column.setParent(self.generic_record_container)
        self.generic_form_column.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        self.generic_form_column.hide()
        self.record_editor_dialog = None
        self.record_editor_popup_layout = None
        self.record_editor_collapsed = True
        if hasattr(self, "command_editor_button"):
            self.command_editor_button.setText("Editor")

    def _open_record_details(self) -> None:
        if (
            self.active_module_key not in self.record_module_keys
            and self.active_module_key != "equipment"
        ):
            return

        dialog = QDialog(self)
        dialog.setObjectName("assetDialog")
        dialog.setWindowTitle("Dados completos")
        dialog.resize(self.record_editor_width, max(420, self.height() - 240))
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        title = QLabel("DADOS COMPLETOS")
        title.setObjectName("formGroupTitle")
        details = create_summary_text(220, 360)
        details.setPlainText(self.current_selected_summary or "Nenhum item selecionado.")
        close_button = QPushButton("Fechar")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(title)
        layout.addWidget(details, 1)
        layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)
        self.record_details_dialog = dialog
        dialog.exec()

    def _clear_current_selection(self) -> None:
        self.table.blockSignals(True)
        self.table.clearSelection()
        self.table.blockSignals(False)
        self.current_selected_record = None
        self.current_selected_summary = "Nenhum item selecionado."
        self._update_record_summary_panel()
        self._reset_selected_record_ids()
        self._set_footer_message("Selecao limpa.", "info")

    def _reset_selected_record_ids(self) -> None:
        self.selected_customer_id = None
        self.selected_inventory_item_id = None
        self.selected_service_order_id = None
        self.selected_sector_id = None
        self.selected_user_id = None
        self.selected_password_reset_request_id = None
