from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMenu,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)

from frontend.app.core.i18n import apply_language_to_widgets
from frontend.app.screens.dashboard_modules import MODULE_BY_KEY


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardContextMenuMixin:
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
            "resource_access",
        }:
            new_action = QAction("Novo", self)
            new_action.triggered.connect(self._new_current_record_from_context)
            menu.addAction(new_action)

        edit_label = "Resolver" if self.active_module_key == "password_resets" else "Editar"
        if self.active_module_key in {"audit_logs"}:
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
            "resource_access": self.clear_resource_access_form,
            "password_resets": self.clear_password_reset_form,
        }
        callback = clear_callbacks.get(self.active_module_key)
        if callback is not None:
            callback()
        self._open_record_editor()

    def _delete_callback_for_active_module(self) -> Callable[[], None] | None:
        if self.active_module_key == "service_orders" and self.current_user_role not in {
            "admin",
            "manager",
        }:
            return None
        return {
            "customers": self._request_customer_delete,
            "inventory": self._request_inventory_delete,
            "service_orders": self._request_service_order_delete,
            "sectors": self._request_sector_delete,
            "users": self._request_user_delete,
            "audit_logs": self._request_audit_delete,
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
            "sectors": "Setores e estrutura operacional.",
            "users": "Usuarios, perfis e redefinicao de senha.",
            "password_resets": "Solicitacoes de recuperacao de acesso.",
            "resource_access": "Acessos de recursos por conta e modulo.",
            "settings": "Identidade visual, empresa, tema e backup.",
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

        apply_language_to_widgets(self._current_ui_language(), dialog)
        dialog.exec()

    def _select_admin_module(self, dialog: QDialog, module_key: str) -> None:
        dialog.accept()
        self.module_selected.emit(module_key)

    def _sync_module_visibility(self) -> None:
        user_resources = {
            str(item) for item in (self.current_user.get("resource_access") or []) if str(item)
        }
        for module_key, button in self.module_buttons.items():
            module = MODULE_BY_KEY.get(module_key)
            if module_key in self.admin_module_keys:
                visible = False
            elif module is None:
                visible = True
            elif module.admin_only and not module.manager_visible:
                visible = self.current_user_role == "admin"
            elif module.manager_visible:
                visible = self.current_user_role in {"admin", "manager"}
            else:
                visible = True
            if visible and user_resources:
                visible = module_key in user_resources
            button.setVisible(visible)

    def _allowed_admin_modules(self) -> tuple[str, ...]:
        user_resources = {
            str(item) for item in (self.current_user.get("resource_access") or []) if str(item)
        }

        if self.current_user_role == "admin":
            modules = self.admin_module_keys + ("settings",)
        elif self.current_user_role == "manager":
            modules = ("sectors", "users", "resource_access", "password_resets")
        else:
            return ()

        if not user_resources:
            return modules
        return tuple(module_key for module_key in modules if module_key in user_resources)
