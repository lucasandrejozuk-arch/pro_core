from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSettings, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsOpacityEffect,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from frontend.app.core.i18n import apply_language_to_widgets, normalize_language, translate_ui_text
from frontend.app.themes.tokens import (
    EDITOR_DEFAULT_MAX_HEIGHT,
    EDITOR_SERVICE_ORDER_MAX_HEIGHT,
    FOOTER_MESSAGE_TIMEOUT_MS,
)
from frontend.app.widgets import create_summary_text


class DashboardStatusMixin:
    def _current_ui_language(self) -> str:
        settings = getattr(self, "current_settings", {})
        language = str(
            QSettings("PRO CORE", "PRO CORE").value("appearance/language", "pt-BR") or "pt-BR"
        )
        if isinstance(settings, dict):
            language = str(settings.get("language") or language)
        return normalize_language(language)

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
        if hasattr(self, "backend_restart_button"):
            self._sync_backend_restart_control()
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

    def set_backend_connection_status(
        self,
        is_connected: bool,
        message: str | None = None,
        level: str | None = None,
    ) -> None:
        normalized_level = level or ("success" if is_connected else "error")
        if normalized_level not in {"success", "warning", "error", "info"}:
            normalized_level = "success" if is_connected else "error"
        self.backend_status_dot.setProperty("level", normalized_level)
        self.backend_status_text.setText(
            message or ("Backend: conectado" if is_connected else "Backend: desconectado")
        )
        self.backend_status_dot.style().unpolish(self.backend_status_dot)
        self.backend_status_dot.style().polish(self.backend_status_dot)

    def set_internal_server_status(self, level: str, message: str) -> None:
        normalized_level = level if level in {"success", "warning", "error", "info"} else "info"
        self.internal_server_status_dot.setProperty("level", normalized_level)
        self.internal_server_status_text.setText(message)
        self.internal_server_status_dot.style().unpolish(self.internal_server_status_dot)
        self.internal_server_status_dot.style().polish(self.internal_server_status_dot)

    def _set_footer_message(self, message: str, level: str = "info") -> None:
        if not hasattr(self, "_footer_message_timer"):
            self._footer_message_timer = QTimer(self)
            self._footer_message_timer.setSingleShot(True)
            self._footer_message_timer.timeout.connect(self._clear_footer_message)
        self._footer_message_timer.stop()
        translated_message = translate_ui_text(message, self._current_ui_language())
        self.footer_message_label.setText(translated_message)
        self.footer_message_label.setProperty("level", level)
        self.footer_message_label.style().unpolish(self.footer_message_label)
        self.footer_message_label.style().polish(self.footer_message_label)
        if message:
            self._footer_message_timer.start(FOOTER_MESSAGE_TIMEOUT_MS)

    def _clear_footer_message(self) -> None:
        if hasattr(self, "footer_message_label"):
            self.footer_message_label.setText("")

    def _set_inline_status(self, label: QLabel, message: str, is_error: bool = False) -> None:
        label.setObjectName("errorText" if is_error else "mutedText")
        label.setText("")
        label.style().unpolish(label)
        label.style().polish(label)
        if message:
            self._set_footer_message(message, "error" if is_error else "success")

    def _animate_content_transition(self) -> None:
        if not hasattr(self, "main_scroll_area"):
            return
        content = self.main_scroll_area.widget()
        if content is None:
            return

        effect = content.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(content)
            content.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(140)
        animation.setStartValue(0.92)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self.content_fade_animation = animation

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

    def _set_record_editor_open(self, is_open: bool) -> None:
        self.record_editor_collapsed = not is_open
        if hasattr(self, "command_editor_button"):
            self.command_editor_button.setText("Fechar editor" if is_open else "Editor")
        if self._uses_docked_record_editor():
            self._attach_record_editor_overlay()
            self.generic_form_column.setVisible(is_open)
            self._position_record_editor()
            return
        if is_open:
            self._show_record_editor_dialog()
        elif self.record_editor_dialog is not None:
            self.record_editor_dialog.close()

    def _uses_docked_record_editor(self) -> bool:
        return self.active_module_key == "service_orders"

    def _attach_record_editor_overlay(self) -> None:
        if self.generic_form_column.parentWidget() is self:
            return
        self.generic_form_column.setParent(self)
        self.generic_form_column.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )

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
        max_height = (
            EDITOR_SERVICE_ORDER_MAX_HEIGHT
            if self.active_module_key == "service_orders"
            else EDITOR_DEFAULT_MAX_HEIGHT
        )
        editor_height = min(max(700, self.height() - 140), max_height)
        editor_width = self.record_editor_width
        if self.active_module_key == "service_orders":
            editor_width = max(editor_width, 1120)
        dialog.resize(editor_width, editor_height)
        dialog.setMinimumWidth(min(editor_width, 980))
        dialog.setMinimumHeight(680)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.generic_form_column.setParent(dialog)
        self.generic_form_column.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self.generic_form_column.show()
        layout.addWidget(self.generic_form_column)
        self.record_editor_popup_layout = layout
        self.record_editor_dialog = dialog
        dialog.finished.connect(self._restore_record_editor_from_dialog)
        apply_language_to_widgets(self._current_ui_language(), dialog)
        dialog.show()

    def _restore_record_editor_from_dialog(self) -> None:
        if self.record_editor_dialog is None:
            return
        self._attach_record_editor_overlay()
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
        dialog.resize(self.record_editor_width, 520)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("DADOS COMPLETOS")
        title.setObjectName("formGroupTitle")
        details = create_summary_text(220, 360)
        details.setPlainText(self.current_selected_summary or "Nenhum item selecionado.")
        close_button = QPushButton("Fechar")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(title)
        layout.addWidget(details)
        layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)
        self.record_details_dialog = dialog
        apply_language_to_widgets(self._current_ui_language(), dialog)
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
