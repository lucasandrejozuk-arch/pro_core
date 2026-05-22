from __future__ import annotations

from typing import Any


class DashboardFormStatePasswordResetMixin:
    def clear_password_reset_form(self) -> None:
        self.selected_password_reset_request_id = None
        self.selected_password_reset_status = None
        self.password_reset_requester_label.setText("Selecione uma solicitacao.")
        self.password_reset_new_password_input.clear()
        self.password_reset_generate_button.setEnabled(False)
        self.password_reset_resolve_button.setEnabled(False)
        self.password_reset_cancel_button.setEnabled(False)
        self.password_reset_full_summary.setPlainText("Nenhuma solicitacao selecionada.")
        self.password_reset_form_status.setText("")
        self._refresh_password_reset_operational_status()
        self.table.clearSelection()

    def set_password_reset_form_status(self, message: str, is_error: bool = False) -> None:
        self._set_inline_status(self.password_reset_form_status, message, is_error)

    def set_password_reset_form_loading(self, is_loading: bool) -> None:
        can_resolve = self._password_reset_can_resolve()
        has_generated_password = bool(self.password_reset_new_password_input.text())
        self.password_reset_generate_button.setEnabled(not is_loading and can_resolve)
        self.password_reset_cancel_button.setEnabled(not is_loading and can_resolve)
        self.password_reset_resolve_button.setEnabled(
            not is_loading and can_resolve and has_generated_password
        )
        self.password_reset_resolve_button.setText(
            "Redefinindo..." if is_loading else "Redefinir senha"
        )
        self.password_reset_cancel_button.setText(
            "Ignorando..." if is_loading else "Ignorar solicitacao"
        )

    def _set_password_reset_operational_status(self, message: str, level: str) -> None:
        self.password_reset_operational_status.setText(message)
        self.password_reset_operational_status.setProperty("level", level)
        self.password_reset_operational_status.style().unpolish(
            self.password_reset_operational_status
        )
        self.password_reset_operational_status.style().polish(
            self.password_reset_operational_status
        )

    def _refresh_password_reset_operational_status(
        self, request: dict[str, Any] | None = None
    ) -> None:
        if request is not None:
            requester = str(
                request.get("requester_full_name") or request.get("requester_email") or "-"
            )
            status_key = self._password_reset_status_key(request.get("status"))
            status_label = self._password_reset_status_label(status_key)
            level = "warning" if status_key == "pending" else "info"
            self._set_password_reset_operational_status(
                f"Solicitacao selecionada: {requester} | Status: {status_label}.",
                level,
            )
            if status_key == "pending":
                self.password_reset_security_status.setText(
                    "Seguranca: gere uma senha temporaria de 6 caracteres para atendimento."
                )
            else:
                self.password_reset_security_status.setText(
                    "Seguranca: solicitacao encerrada; acoes de atendimento bloqueadas."
                )
            return

        request_count = len(self.all_rows) if self.active_module_key == "password_resets" else 0
        pending_count = sum(
            1
            for row in self.all_rows
            if self._password_reset_status_key(row.get("status")) == "pending"
        )
        if request_count:
            self._set_password_reset_operational_status(
                f"{request_count} solicitacao(oes) carregada(s); {pending_count} pendente(s).",
                "warning" if pending_count else "info",
            )
        else:
            self._set_password_reset_operational_status(
                "Nenhuma solicitacao de senha carregada para atendimento.",
                "warning",
            )
        self.password_reset_security_status.setText(
            "Seguranca: selecione uma solicitacao pendente para definir senha temporaria."
        )

    def _password_reset_can_resolve(self) -> bool:
        return bool(self.selected_password_reset_request_id) and (
            self.selected_password_reset_status == "pending"
        )

    def _password_reset_status_key(self, status: Any) -> str:
        return str(status or "pending").strip().lower()

    def _password_reset_status_label(self, status: Any) -> str:
        status_key = self._password_reset_status_key(status)
        return {
            "pending": "Pendente",
            "resolved": "Resolvida",
            "completed": "Resolvida",
            "cancelled": "Cancelada",
            "ignored": "Ignorada",
        }.get(status_key, self._format_value(status_key) or "Pendente")
