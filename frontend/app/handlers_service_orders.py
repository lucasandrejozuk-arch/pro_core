from __future__ import annotations

from frontend.app.core.api_client import ApiError


class ServiceOrderHandlersMixin:
    def handle_service_order_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_service_order_form_loading(True)
        try:
            self.api_client.create_service_order(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_service_order_form_loading(False)
            self.dashboard_window.set_service_order_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_service_order_form_loading(False)
        self.dashboard_window.set_service_order_form_status("Ordem de serviço criada.")
        self.load_module("service_orders")

    def handle_service_order_update(self, service_order_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_service_order_form_loading(True)
        try:
            self.api_client.update_service_order(
                self.session.access_token,
                service_order_id,
                payload,
            )
        except ApiError as exc:
            self.dashboard_window.set_service_order_form_loading(False)
            self.dashboard_window.set_service_order_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_service_order_form_loading(False)
        self.dashboard_window.set_service_order_form_status("Ordem de serviço atualizada.")
        self.load_module("service_orders")

    def handle_service_order_delete(self, service_order_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_service_order_form_loading(True)
        try:
            self.api_client.delete_service_order(self.session.access_token, service_order_id)
        except ApiError as exc:
            self.dashboard_window.set_service_order_form_loading(False)
            self.dashboard_window.set_service_order_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_service_order_form_loading(False)
        self.dashboard_window.set_service_order_form_status("Ordem de serviço excluída.")
        self.load_module("service_orders")

    def handle_service_order_diagnosis(
        self,
        service_order_id: str,
        technical_diagnosis: str,
    ) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.register_service_order_diagnosis(
                access_token,
                service_order_id,
                technical_diagnosis,
            ),
            "Diagnóstico registrado.",
        )

    def handle_service_order_budget_item(
        self,
        service_order_id: str,
        payload: dict,
    ) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.add_service_order_budget_item(
                access_token,
                service_order_id,
                payload,
            ),
            "Item de orçamento adicionado.",
        )

    def handle_service_order_submit_quote(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.submit_service_order_quote(
                access_token,
                service_order_id,
            ),
            "Orçamento enviado.",
        )

    def handle_service_order_approve(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.approve_service_order(
                access_token,
                service_order_id,
            ),
            "Ordem de serviço aprovada.",
        )

    def handle_service_order_reject(self, service_order_id: str, rejection_reason: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.reject_service_order(
                access_token,
                service_order_id,
                rejection_reason,
            ),
            "Ordem de serviço reprovada.",
        )

    def handle_service_order_start(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.start_service_order(
                access_token,
                service_order_id,
            ),
            "Execução iniciada.",
        )

    def handle_service_order_complete(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.complete_service_order(
                access_token,
                service_order_id,
            ),
            "Ordem de serviço concluída.",
        )

    def handle_service_order_document_upload(
        self,
        service_order_id: str,
        document_type: str,
        file_path: str,
    ) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.upload_document(
                access_token=access_token,
                file_path=file_path,
                document_type=document_type,
                service_order_id=service_order_id,
            ),
            "Anexo enviado.",
        )

    def _run_service_order_action(self, action, success_message: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_service_order_action_loading(True)
        try:
            action(self.session.access_token)
        except ApiError as exc:
            self.dashboard_window.set_service_order_action_loading(False)
            self.dashboard_window.set_service_order_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_service_order_action_loading(False)
        self.dashboard_window.set_service_order_form_status(success_message)
        self.load_module("service_orders")
