# ruff: noqa: F401, F821, E501
from __future__ import annotations

import math
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QResizeEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from frontend.app.core.display import DisplayProfile, detect_display_profile
from frontend.app.core.grid import GRID_COLUMNS, add_layout, add_widget, create_grid, span_for_items
from frontend.app.core.icons import build_icon
from frontend.app.screens.dashboard_dialogs import (
    EquipmentAssetDialog,
    EquipmentDefectCasesDialog,
)
from frontend.app.themes.styles import COLOR_PALETTE_OPTIONS, DEFAULT_COLOR_PALETTE
from frontend.app.widgets import DashboardKpiCard, create_summary_text


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

        if hasattr(self, "record_editor_toggle_button"):
            self._refresh_record_editor_button_icon()

    def apply_record_editor_icon_colors(self, inactive_color: str, active_color: str) -> None:
        self.record_editor_icon_color = inactive_color
        self.record_editor_active_icon_color = active_color
        if hasattr(self, "record_editor_toggle_button"):
            self._refresh_record_editor_button_icon()

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
            self.content_layout.setRowStretch(5, 1)

    def _position_record_editor(self) -> None:
        if not hasattr(self, "generic_form_column"):
            return

        is_record_module = self.active_module_key in self.record_module_keys
        is_open = not self.record_editor_collapsed
        self.generic_form_column.setVisible(is_record_module and is_open)
        if not is_record_module or not is_open:
            return

        rail_width = self.record_toggle_rail.width() if hasattr(self, "record_toggle_rail") else 88
        margin = 10
        available_width = max(320, self.generic_record_container.width() - rail_width - margin)
        target_width = max(self.record_editor_width, round(available_width * 0.46))
        width = min(target_width, available_width)
        height = max(260, self.generic_record_container.height())
        x = max(0, self.generic_record_container.width() - rail_width - width - margin)
        self.generic_form_column.setGeometry(x, 0, width, height)
        self.generic_form_column.raise_()
        self.record_toggle_rail.raise_()

    def _refresh_record_editor_button_icon(self) -> None:
        self.record_editor_toggle_button.setIcon(QIcon())
        self.record_editor_toggle_button.setIconSize(QSize(0, 0))

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
        self.session_button.setVisible(True)
        self.logout_button.setVisible(True)
        self._sync_module_visibility()
        self.sidebar_layout.setContentsMargins(8, 8, 8, 8)
        self.sidebar.setFixedWidth(self.sidebar_expanded_width)
        self._position_sidebar()

    def _set_record_editor_open(self, is_open: bool) -> None:
        self.record_editor_collapsed = not is_open
        self.record_editor_toggle_button.setToolTip(
            "Fechar editor de registro" if is_open else "Abrir editor de registro"
        )
        self.record_editor_toggle_button.setProperty(
            "collapsed",
            "false" if is_open else "true",
        )
        self.record_editor_toggle_button.style().unpolish(self.record_editor_toggle_button)
        self.record_editor_toggle_button.style().polish(self.record_editor_toggle_button)
        self._refresh_record_editor_button_icon()
        if is_open:
            self._show_record_editor_dialog()
        elif self.record_editor_dialog is not None:
            self.record_editor_dialog.close()

    def _open_record_editor(self) -> None:
        if self.active_module_key not in self.record_module_keys:
            return
        if not self.record_editor_toggle_button.isChecked():
            self.record_editor_toggle_button.setChecked(True)
            return
        self._set_record_editor_open(True)

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
        self.record_editor_toggle_button.blockSignals(True)
        self.record_editor_toggle_button.setChecked(False)
        self.record_editor_toggle_button.blockSignals(False)
        self.record_editor_toggle_button.setProperty("collapsed", "true")
        self.record_editor_toggle_button.style().unpolish(self.record_editor_toggle_button)
        self.record_editor_toggle_button.style().polish(self.record_editor_toggle_button)

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
        self._reset_selected_record_ids()
        self._set_footer_message("Selecao limpa.", "info")

    def _reset_selected_record_ids(self) -> None:
        self.selected_customer_id = None
        self.selected_inventory_item_id = None
        self.selected_service_order_id = None
        self.selected_sector_id = None
        self.selected_user_id = None
        self.selected_password_reset_request_id = None
        self.selected_financial_record_id = None

    def _open_record_table_context_menu(self, position) -> None:
        if self.active_module_key not in self.record_module_keys:
            return

        clicked_item = self.table.itemAt(position)
        if clicked_item is not None:
            self.table.selectRow(clicked_item.row())

        menu = QMenu(self)
        has_selection = bool(self.table.selectedItems())

        if self.active_module_key in {
            "customers",
            "inventory",
            "service_orders",
            "sectors",
            "users",
            "financial",
        }:
            new_action = QAction("Novo", self)
            new_action.triggered.connect(self._new_current_record_from_context)
            menu.addAction(new_action)

        edit_label = "Resolver" if self.active_module_key == "password_resets" else "Editar"
        if self.active_module_key in {"audit_logs", "notifications"}:
            edit_label = "Ver detalhes"
        edit_action = QAction(edit_label, self)
        edit_action.setEnabled(has_selection)
        edit_action.triggered.connect(self._open_record_editor)
        menu.addAction(edit_action)
        details_action = QAction("Dados completos", self)
        details_action.setEnabled(has_selection)
        details_action.triggered.connect(self._open_record_details)
        menu.addAction(details_action)

        delete_callback = self._delete_callback_for_active_module()
        if delete_callback is not None:
            delete_action = QAction("Excluir", self)
            delete_action.setEnabled(has_selection)
            delete_action.triggered.connect(delete_callback)
            menu.addAction(delete_action)

        if self.active_module_key == "financial":
            menu.addSeparator()
            paid_action = QAction("Marcar como pago", self)
            paid_action.setEnabled(has_selection)
            paid_action.triggered.connect(self._request_financial_mark_paid)
            menu.addAction(paid_action)
            cancel_action = QAction("Cancelar lancamento", self)
            cancel_action.setEnabled(has_selection)
            cancel_action.triggered.connect(self._request_financial_cancel)
            menu.addAction(cancel_action)

        if self.active_module_key == "reports":
            menu.addSeparator()
            view_action = QAction("Gerar relatorio", self)
            view_action.triggered.connect(self._request_report_view)
            menu.addAction(view_action)

        if has_selection:
            menu.addSeparator()
            clear_action = QAction("Limpar selecao", self)
            clear_action.triggered.connect(self._clear_current_selection)
            menu.addAction(clear_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _open_equipment_table_context_menu(self, table: QTableWidget, position) -> None:
        clicked_item = table.itemAt(position)
        if clicked_item is not None:
            table.selectRow(clicked_item.row())

        menu = QMenu(self)
        if table is self.equipment_table:
            menu.addAction(
                self._context_action(
                    "Novo equipamento",
                    self._open_equipment_create_dialog,
                )
            )
            menu.addAction(
                self._context_action(
                    "Editar equipamento",
                    self._open_equipment_edit_dialog,
                    bool(self.selected_equipment_id),
                )
            )
            menu.addAction(
                self._context_action(
                    "Excluir equipamento",
                    self._request_equipment_delete,
                    bool(self.selected_equipment_id),
                )
            )
            menu.addSeparator()
            menu.addAction(
                self._context_action(
                    "Casos de defeito",
                    self._request_equipment_defect_cases_open,
                    bool(self.selected_equipment_id),
                )
            )
        elif table is self.equipment_boards_table:
            menu.addAction(
                self._context_action(
                    "Novo objeto vinculado",
                    self._request_equipment_board_create,
                    bool(self.selected_equipment_id),
                )
            )
            menu.addAction(
                self._context_action(
                    "Editar objeto",
                    self._open_equipment_board_edit_dialog,
                    bool(self.selected_equipment_board_id),
                )
            )
            menu.addAction(
                self._context_action(
                    "Excluir objeto",
                    self._request_equipment_board_delete,
                    bool(self.selected_equipment_board_id),
                )
            )
        elif table is self.equipment_components_table:
            menu.addAction(
                self._context_action(
                    "Novo componente",
                    self._request_equipment_component_create,
                    bool(self.selected_equipment_board_id),
                )
            )
            menu.addAction(
                self._context_action(
                    "Editar componente",
                    self._open_equipment_component_edit_dialog,
                    bool(self.selected_equipment_component_id),
                )
            )
            menu.addAction(
                self._context_action(
                    "Excluir componente",
                    self._request_equipment_component_delete,
                    bool(self.selected_equipment_component_id),
                )
            )

        if not menu.actions():
            return
        menu.exec(table.viewport().mapToGlobal(position))

    def _context_action(
        self,
        label: str,
        callback: Callable[[], None],
        enabled: bool = True,
    ) -> QAction:
        action = QAction(label, self)
        action.setEnabled(enabled)
        action.triggered.connect(callback)
        return action

    def _new_current_record_from_context(self) -> None:
        clear_callbacks = {
            "customers": self.clear_customer_form,
            "inventory": self.clear_inventory_form,
            "service_orders": self.clear_service_order_form,
            "sectors": self.clear_sector_form,
            "users": self.clear_user_form,
            "password_resets": self.clear_password_reset_form,
            "reports": self.clear_report_form,
            "financial": self.clear_financial_form,
        }
        callback = clear_callbacks.get(self.active_module_key)
        if callback is not None:
            callback()
        self._open_record_editor()

    def _delete_callback_for_active_module(self) -> Callable[[], None] | None:
        return {
            "customers": self._request_customer_delete,
            "inventory": self._request_inventory_delete,
            "service_orders": self._request_service_order_delete,
            "financial": self._request_financial_delete,
        }.get(self.active_module_key)

    def _open_admin_menu(self) -> None:
        allowed_modules = self._allowed_admin_modules()
        if not allowed_modules:
            return

        dialog = QDialog(self)
        dialog.setObjectName("adminMenuDialog")
        dialog.setWindowTitle("Area Administrativa")
        dialog.setModal(True)
        dialog.resize(480, 420)

        title = QLabel("Area Administrativa")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Acesse configuracoes e rotinas administrativas.")
        subtitle.setObjectName("mutedText")
        subtitle.setWordWrap(True)

        descriptions = {
            "financial": "Lancamentos, baixas e controle financeiro.",
            "notifications": "Fila de notificacoes por email, WhatsApp e sistema.",
            "sectors": "Setores e estrutura operacional.",
            "users": "Usuarios, perfis e redefinicao de senha.",
            "password_resets": "Solicitacoes de recuperacao de acesso.",
            "settings": "Identidade visual, empresa, tema e backup.",
            "reports": "Relatorios operacionais e exportacoes.",
            "audit_logs": "Rastreabilidade administrativa e operacional.",
        }

        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        for module_key in allowed_modules:
            button = QPushButton(self.module_labels[module_key])
            button.setObjectName("adminMenuButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(descriptions[module_key])
            button.clicked.connect(
                lambda checked=False, key=module_key: self._select_admin_module(dialog, key)
            )
            actions_layout.addWidget(button)

        close_button = QPushButton("Fechar")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(dialog.reject)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(actions_layout)
        layout.addStretch()
        layout.addWidget(close_button)

        dialog.exec()

    def _select_admin_module(self, dialog: QDialog, module_key: str) -> None:
        dialog.accept()
        self.module_selected.emit(module_key)

    def _open_settings_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setObjectName("assetDialog")
        dialog.setWindowTitle("Personalizacao e Configuracoes")
        dialog.setModal(True)
        dialog.resize(680, 520)

        settings = dict(self.current_settings)
        tabs = QTabWidget()

        company_name = self._dialog_line_edit(settings, "company_name", "Minha Assistencia")
        trade_name = self._dialog_line_edit(settings, "trade_name", "Nome fantasia")
        document_number = self._dialog_line_edit(settings, "document_number", "Documento")
        company_email = self._dialog_line_edit(settings, "email", "Email")
        company_phone = self._dialog_line_edit(settings, "phone", "Telefone")
        company_tab = QWidget()
        company_form = QFormLayout(company_tab)
        company_form.setSpacing(8)
        company_form.addRow("Empresa", company_name)
        company_form.addRow("Nome fantasia", trade_name)
        company_form.addRow("Documento", document_number)
        company_form.addRow("Email", company_email)
        company_form.addRow("Telefone", company_phone)

        brand_name = self._dialog_line_edit(settings, "brand_name", "Nome exibido")
        brand_subtitle = self._dialog_line_edit(settings, "brand_subtitle", "Subtitulo")
        color_palette_combo = QComboBox()
        self._populate_color_palette_combo(color_palette_combo)
        self._select_combo_value(
            color_palette_combo,
            str(settings.get("color_palette") or DEFAULT_COLOR_PALETTE),
        )
        theme_combo = QComboBox()
        theme_combo.addItem("Claro", "light")
        theme_combo.addItem("Escuro", "dark")
        self._select_combo_value(theme_combo, str(settings.get("theme") or "dark"))
        scale_label = QLabel(f"{round(self.ui_scale_value * 100)}%")
        scale_label.setObjectName("mutedText")
        scale_slider = QSlider(Qt.Orientation.Horizontal)
        scale_slider.setMinimum(round(self.ui_scale_min * 100))
        scale_slider.setMaximum(round(self.ui_scale_max * 100))
        scale_slider.setValue(round(self.ui_scale_value * 100))

        def handle_scale_change(value: int) -> None:
            scale_label.setText(f"{value}%")
            self.ui_scale_changed.emit(value / 100)

        scale_slider.valueChanged.connect(handle_scale_change)
        appearance_tab = QWidget()
        appearance_form = QFormLayout(appearance_tab)
        appearance_form.setSpacing(8)
        appearance_form.addRow("Nome exibido", brand_name)
        appearance_form.addRow("Subtitulo", brand_subtitle)
        appearance_form.addRow("Paleta", color_palette_combo)
        appearance_form.addRow("Tema", theme_combo)
        appearance_form.addRow("Escala", scale_slider)
        appearance_form.addRow("", scale_label)

        backup_enabled = QCheckBox("Backup automatico ativo")
        backup_enabled.setChecked(bool(settings.get("backup_enabled", True)))
        backup_interval = self._dialog_line_edit(settings, "backup_interval_hours", "24")
        backup_path = self._dialog_line_edit(settings, "backup_storage_path", "backups")
        backup_last_run = QLabel(str(settings.get("backup_last_run_at") or "Ultimo backup: nunca"))
        backup_last_run.setObjectName("mutedText")
        backup_run_button = QPushButton("Executar backup agora")
        backup_run_button.setObjectName("secondaryButton")
        backup_run_button.clicked.connect(self.backup_run_requested.emit)
        backup_tab = QWidget()
        backup_form = QFormLayout(backup_tab)
        backup_form.setSpacing(8)
        backup_form.addRow("", backup_enabled)
        backup_form.addRow("Intervalo (horas)", backup_interval)
        backup_form.addRow("Destino", backup_path)
        backup_form.addRow("Status", backup_last_run)
        backup_form.addRow("", backup_run_button)

        session_tab = QWidget()
        session_layout = QVBoxLayout(session_tab)
        session_layout.setContentsMargins(8, 8, 8, 8)
        session_summary = create_summary_text(160, 220)
        session_summary.setPlainText(self.session_footer_label.text())
        session_layout.addWidget(session_summary)

        tabs.addTab(company_tab, "Empresa")
        tabs.addTab(appearance_tab, "Aparencia")
        tabs.addTab(backup_tab, "Backup")
        tabs.addTab(session_tab, "Sessao")

        status_label = QLabel("")
        status_label.setObjectName("mutedText")
        save_button = QPushButton("Salvar")
        cancel_button = QPushButton("Fechar")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(dialog.reject)

        def save_settings() -> None:
            values = {
                "company_name": company_name.text().strip(),
                "trade_name": trade_name.text().strip() or None,
                "document_number": document_number.text().strip() or None,
                "email": company_email.text().strip() or None,
                "phone": company_phone.text().strip() or None,
                "brand_name": brand_name.text().strip() or None,
                "brand_subtitle": brand_subtitle.text().strip() or None,
                "color_palette": str(color_palette_combo.currentData() or DEFAULT_COLOR_PALETTE),
                "theme": str(theme_combo.currentData() or "light"),
                "backup_enabled": backup_enabled.isChecked(),
                "backup_storage_path": backup_path.text().strip(),
            }
            if not values["company_name"]:
                status_label.setObjectName("errorText")
                status_label.setText("Informe o nome da empresa.")
                status_label.style().unpolish(status_label)
                status_label.style().polish(status_label)
                return
            try:
                values["backup_interval_hours"] = int(backup_interval.text().strip())
            except ValueError:
                status_label.setObjectName("errorText")
                status_label.setText("Intervalo de backup deve ser inteiro.")
                status_label.style().unpolish(status_label)
                status_label.style().polish(status_label)
                return
            if not values["backup_storage_path"]:
                status_label.setObjectName("errorText")
                status_label.setText("Informe a pasta de backup.")
                status_label.style().unpolish(status_label)
                status_label.style().polish(status_label)
                return
            self.settings_update_requested.emit(values)
            dialog.accept()

        save_button.clicked.connect(save_settings)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(cancel_button)
        actions.addWidget(save_button)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(tabs)
        layout.addWidget(status_label)
        layout.addLayout(actions)
        dialog.exec()

    @staticmethod
    def _dialog_line_edit(
        settings: dict[str, Any],
        key: str,
        placeholder: str,
    ) -> QLineEdit:
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        value = settings.get(key)
        if value is not None:
            line_edit.setText(str(value))
        return line_edit

    def _sync_module_visibility(self) -> None:
        allowed_admin_modules = set(self._allowed_admin_modules())
        for module_key, button in self.module_buttons.items():
            if module_key in {"customers", "admin_area"}:
                visible = self.current_user_role in {"admin", "manager"}
            elif module_key == "settings":
                visible = self.current_user_role == "admin"
            elif module_key in self.admin_module_keys:
                visible = False
            elif module_key in self.management_module_keys:
                visible = (
                    module_key in allowed_admin_modules
                    or module_key in {"financial", "reports"}
                )
            else:
                visible = True
            button.setVisible(visible)

    def _allowed_admin_modules(self) -> tuple[str, ...]:
        if self.current_user_role == "admin":
            return self.admin_module_keys + self.management_module_keys + ("settings",)
        if self.current_user_role == "manager":
            return ("financial", "reports", "notifications", "sectors", "users", "password_resets")
        return ()

