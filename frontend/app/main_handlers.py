from __future__ import annotations

from frontend.app.core.api_client import ApiError
from frontend.app.core.display import build_display_profile


class ProCoreHandlersMixin:
    def handle_customer_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_customer_form_loading(True)
        try:
            self.api_client.create_customer(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_customer_form_loading(False)
            self.dashboard_window.set_customer_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_customer_form_loading(False)
        self.dashboard_window.set_customer_form_status("Cliente criado.")
        self.load_module("customers")

    def handle_customer_update(self, customer_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_customer_form_loading(True)
        try:
            self.api_client.update_customer(self.session.access_token, customer_id, payload)
        except ApiError as exc:
            self.dashboard_window.set_customer_form_loading(False)
            self.dashboard_window.set_customer_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_customer_form_loading(False)
        self.dashboard_window.set_customer_form_status("Cliente atualizado.")
        self.load_module("customers")

    def handle_customer_delete(self, customer_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_customer_form_loading(True)
        try:
            self.api_client.delete_customer(self.session.access_token, customer_id)
        except ApiError as exc:
            self.dashboard_window.set_customer_form_loading(False)
            self.dashboard_window.set_customer_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_customer_form_loading(False)
        self.dashboard_window.set_customer_form_status("Cliente excluido.")
        self.load_module("customers")

    def handle_customer_document_upload(
        self,
        customer_id: str,
        document_type: str,
        file_path: str,
    ) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_customer_document_upload_loading(True)
        try:
            self.api_client.upload_document(
                access_token=self.session.access_token,
                file_path=file_path,
                document_type=document_type,
                customer_id=customer_id,
            )
        except ApiError as exc:
            self.dashboard_window.set_customer_document_upload_loading(False)
            self.dashboard_window.set_customer_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_customer_document_upload_loading(False)
        self.dashboard_window.set_customer_form_status("Anexo enviado.")
        self.load_module("customers")

    def handle_equipment_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_form_loading(True)
        try:
            self.api_client.create_equipment(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_equipment_form_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_form_loading(False)
        self.dashboard_window.set_equipment_form_status("Equipamento criado.")
        self.load_module("equipment")

    def handle_equipment_update(self, equipment_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_form_loading(True)
        try:
            self.api_client.update_equipment(self.session.access_token, equipment_id, payload)
        except ApiError as exc:
            self.dashboard_window.set_equipment_form_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_form_loading(False)
        self.dashboard_window.set_equipment_form_status("Equipamento atualizado.")
        self.load_module("equipment")

    def handle_equipment_delete(self, equipment_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_form_loading(True)
        try:
            self.api_client.delete_equipment(self.session.access_token, equipment_id)
        except ApiError as exc:
            self.dashboard_window.set_equipment_form_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_form_loading(False)
        self.dashboard_window.set_equipment_form_status("Equipamento removido.")
        self.load_module("equipment")

    def handle_equipment_board_create(self, equipment_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_object_loading(True)
        try:
            self.api_client.create_equipment_board(
                self.session.access_token,
                equipment_id,
                payload,
            )
        except ApiError as exc:
            self.dashboard_window.set_equipment_object_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Placa vinculada.")
        self.load_module("equipment")

    def handle_equipment_board_update(
        self,
        equipment_id: str,
        board_id: str,
        payload: dict,
    ) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_object_loading(True)
        try:
            self.api_client.update_equipment_board(
                self.session.access_token,
                equipment_id,
                board_id,
                payload,
            )
        except ApiError as exc:
            self.dashboard_window.set_equipment_object_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Objeto vinculado atualizado.")
        self.load_module("equipment")

    def handle_equipment_board_delete(self, equipment_id: str, board_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_object_loading(True)
        try:
            self.api_client.delete_equipment_board(
                self.session.access_token,
                equipment_id,
                board_id,
            )
        except ApiError as exc:
            self.dashboard_window.set_equipment_object_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Objeto vinculado removido.")
        self.load_module("equipment")

    def handle_equipment_component_create(
        self,
        equipment_id: str,
        board_id: str,
        payload: dict,
    ) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_object_loading(True)
        try:
            self.api_client.create_equipment_board_component(
                self.session.access_token,
                equipment_id,
                board_id,
                payload,
            )
        except ApiError as exc:
            self.dashboard_window.set_equipment_object_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Componente vinculado.")
        self.load_module("equipment")

    def handle_equipment_component_update(
        self,
        equipment_id: str,
        board_id: str,
        component_id: str,
        payload: dict,
    ) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_object_loading(True)
        try:
            self.api_client.update_equipment_board_component(
                self.session.access_token,
                equipment_id,
                board_id,
                component_id,
                payload,
            )
        except ApiError as exc:
            self.dashboard_window.set_equipment_object_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Componente atualizado.")
        self.load_module("equipment")

    def handle_equipment_component_delete(
        self,
        equipment_id: str,
        board_id: str,
        component_id: str,
    ) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_object_loading(True)
        try:
            self.api_client.delete_equipment_board_component(
                self.session.access_token,
                equipment_id,
                board_id,
                component_id,
            )
        except ApiError as exc:
            self.dashboard_window.set_equipment_object_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Componente removido.")
        self.load_module("equipment")

    def handle_equipment_defect_cases(self, equipment_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        access_token = self.session.access_token

        def list_cases(query: str) -> list[dict]:
            return self.api_client.list_equipment_defect_cases(access_token, equipment_id, query)

        def create_case(payload: dict) -> dict:
            return self.api_client.create_equipment_defect_case(access_token, equipment_id, payload)

        def update_case(case_id: str, payload: dict) -> dict:
            return self.api_client.update_equipment_defect_case(
                access_token,
                equipment_id,
                case_id,
                payload,
            )

        def delete_case(case_id: str) -> None:
            self.api_client.delete_equipment_defect_case(access_token, equipment_id, case_id)

        self.dashboard_window.open_equipment_defect_cases_dialog(
            equipment_id,
            list_cases,
            create_case,
            update_case,
            delete_case,
        )
        self.load_module("equipment")

    def handle_equipment_import(self, file_path: str, replace: bool) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_form_loading(True)
        try:
            result = self.api_client.import_equipment(
                self.session.access_token,
                file_path,
                replace=replace,
            )
        except (ApiError, OSError) as exc:
            self.dashboard_window.set_equipment_form_loading(False)
            message = exc.display_message if isinstance(exc, ApiError) else str(exc)
            self.dashboard_window.set_equipment_form_status(message, is_error=True)
            return

        self.dashboard_window.set_equipment_form_loading(False)
        self.dashboard_window.set_equipment_form_status(
            f"Importacao concluida: {result.get('processed_rows', 0)} linha(s)."
        )
        self.load_module("equipment")

    def handle_equipment_export(self, export_format: str, file_path: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_form_loading(True)
        try:
            content = self.api_client.export_equipment(self.session.access_token, export_format)
            with open(file_path, "wb") as output_file:
                output_file.write(content)
        except (ApiError, OSError) as exc:
            self.dashboard_window.set_equipment_form_loading(False)
            message = exc.display_message if isinstance(exc, ApiError) else str(exc)
            self.dashboard_window.set_equipment_form_status(message, is_error=True)
            return

        self.dashboard_window.set_equipment_form_loading(False)
        self.dashboard_window.set_equipment_form_status(f"Arquivo salvo em {file_path}.")

    def handle_inventory_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_inventory_form_loading(True)
        try:
            self.api_client.create_inventory_item(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_inventory_form_loading(False)
        self.dashboard_window.set_inventory_form_status("Item de estoque criado.")
        self.load_module("inventory")

    def handle_inventory_update(self, item_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_inventory_form_loading(True)
        try:
            self.api_client.update_inventory_item(self.session.access_token, item_id, payload)
        except ApiError as exc:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_inventory_form_loading(False)
        self.dashboard_window.set_inventory_form_status("Item de estoque atualizado.")
        self.load_module("inventory")

    def handle_inventory_delete(self, item_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_inventory_form_loading(True)
        try:
            self.api_client.delete_inventory_item(self.session.access_token, item_id)
        except ApiError as exc:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_inventory_form_loading(False)
        self.dashboard_window.set_inventory_form_status("Item de estoque excluido.")
        self.load_module("inventory")

    def handle_sector_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_sector_form_loading(True)
        try:
            self.api_client.create_sector(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_sector_form_loading(False)
            self.dashboard_window.set_sector_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_sector_form_loading(False)
        self.dashboard_window.set_sector_form_status("Setor criado.")
        self.load_module("sectors")

    def handle_sector_update(self, sector_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_sector_form_loading(True)
        try:
            self.api_client.update_sector(self.session.access_token, sector_id, payload)
        except ApiError as exc:
            self.dashboard_window.set_sector_form_loading(False)
            self.dashboard_window.set_sector_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_sector_form_loading(False)
        self.dashboard_window.set_sector_form_status("Setor atualizado.")
        self.load_module("sectors")

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
        self.dashboard_window.set_service_order_form_status("Ordem de servico criada.")
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
        self.dashboard_window.set_service_order_form_status("Ordem de servico atualizada.")
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
        self.dashboard_window.set_service_order_form_status("Ordem de servico excluida.")
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
            "Diagnostico registrado.",
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
            "Item de orcamento adicionado.",
        )

    def handle_service_order_submit_quote(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.submit_service_order_quote(
                access_token,
                service_order_id,
            ),
            "Orcamento enviado.",
        )

    def handle_service_order_approve(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.approve_service_order(
                access_token,
                service_order_id,
            ),
            "Ordem de servico aprovada.",
        )

    def handle_service_order_reject(self, service_order_id: str, rejection_reason: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.reject_service_order(
                access_token,
                service_order_id,
                rejection_reason,
            ),
            "Ordem de servico reprovada.",
        )

    def handle_service_order_start(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.start_service_order(
                access_token,
                service_order_id,
            ),
            "Execucao iniciada.",
        )

    def handle_service_order_complete(self, service_order_id: str) -> None:
        self._run_service_order_action(
            lambda access_token: self.api_client.complete_service_order(
                access_token,
                service_order_id,
            ),
            "Ordem de servico concluida.",
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

    def handle_user_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_form_loading(True)
        try:
            self.api_client.create_user(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_user_form_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_form_loading(False)
        self.dashboard_window.set_user_form_status("Usuario criado.")
        self.load_module("users")

    def handle_user_update(self, user_id: str, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_form_loading(True)
        try:
            self.api_client.update_user(self.session.access_token, user_id, payload)
        except ApiError as exc:
            self.dashboard_window.set_user_form_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_form_loading(False)
        self.dashboard_window.set_user_form_status("Usuario atualizado.")
        self.load_module("users")

    def handle_user_password_reset(self, user_id: str, new_password: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_user_password_reset_loading(True)
        try:
            self.api_client.reset_user_password(
                self.session.access_token,
                user_id,
                new_password,
            )
        except ApiError as exc:
            self.dashboard_window.set_user_password_reset_loading(False)
            self.dashboard_window.set_user_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_user_password_reset_loading(False)
        self.dashboard_window.set_user_form_status("Senha redefinida.")
        self.load_module("users")

    def handle_password_reset_request(self, email: str) -> None:
        self.login_window.set_password_reset_loading(True)
        try:
            response = self.api_client.request_password_reset(email)
        except ApiError as exc:
            self.login_window.set_password_reset_loading(False)
            self.login_window.set_error(exc.display_message)
            return

        self.login_window.set_password_reset_loading(False)
        self.login_window.set_info(str(response.get("message") or "Solicitacao enviada."))

    def handle_password_reset_resolve(self, request_id: str, new_password: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_password_reset_form_loading(True)
        try:
            self.api_client.resolve_password_reset_request(
                self.session.access_token,
                request_id,
                new_password,
            )
        except ApiError as exc:
            self.dashboard_window.set_password_reset_form_loading(False)
            self.dashboard_window.set_password_reset_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_password_reset_form_loading(False)
        self.dashboard_window.set_password_reset_form_status("Senha redefinida.")
        self.load_module("password_resets")

    def handle_settings_update(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_settings_form_loading(True)
        try:
            settings = self.api_client.update_settings(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_settings_form_loading(False)
            self.dashboard_window.set_settings_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_settings_form_loading(False)
        self._remember_appearance(settings)
        self._apply_local_theme()
        self.dashboard_window.render_settings(settings)
        self.dashboard_window.set_settings_form_status("Configuracoes salvas.")

    def handle_ui_scale_changed(self, scale: float) -> None:
        self.local_settings.setValue("appearance/ui_scale", str(scale))
        self._apply_local_theme()
        profile = build_display_profile(
            self.dashboard_window.width(),
            max(self.dashboard_window.height(), 640),
            scale,
        )
        self.dashboard_window.apply_display_profile(profile)

    def handle_backup_run(self) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_backup_run_loading(True)
        try:
            backup = self.api_client.run_backup(self.session.access_token)
            settings = self.api_client.get_settings(self.session.access_token)
        except ApiError as exc:
            self.dashboard_window.set_backup_run_loading(False)
            self.dashboard_window.set_settings_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_backup_run_loading(False)
        self.dashboard_window.render_settings(settings)
        self.dashboard_window.set_settings_form_status(
            f"Backup validado: {backup.get('file_name')}"
        )

    def handle_report_view(self, module_key: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_report_loading(True)
        try:
            report = self.api_client.get_report(self.session.access_token, module_key)
        except ApiError as exc:
            self.dashboard_window.set_report_loading(False)
            self.dashboard_window.set_report_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_report_loading(False)
        self.dashboard_window.render_report(report)
        self.dashboard_window.set_report_status("Relatorio carregado.")

    def handle_report_export(self, module_key: str, report_format: str, file_path: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_report_export_loading(True)
        try:
            content = self.api_client.export_report(
                self.session.access_token,
                module_key,
                report_format,
            )
        except ApiError as exc:
            self.dashboard_window.set_report_export_loading(False)
            self.dashboard_window.set_report_status(exc.display_message, is_error=True)
            return

        try:
            with open(file_path, "wb") as output_file:
                output_file.write(content)
        except OSError as exc:
            self.dashboard_window.set_report_export_loading(False)
            self.dashboard_window.set_report_status(
                f"Nao foi possivel salvar o relatorio: {exc}",
                is_error=True,
            )
            return

        self.dashboard_window.set_report_export_loading(False)
        self.dashboard_window.set_report_status(f"Relatorio salvo em {file_path}.")

    def handle_financial_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_financial_form_loading(True)
        try:
            self.api_client.create_financial_record(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_financial_form_loading(False)
            self.dashboard_window.set_financial_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_financial_form_loading(False)
        self.dashboard_window.set_financial_form_status("Lancamento criado.")
        self.load_module("financial")

    def handle_financial_mark_paid(self, record_id: str) -> None:
        self._run_financial_action(
            lambda access_token: self.api_client.mark_financial_record_paid(
                access_token,
                record_id,
            ),
            "Lancamento marcado como pago.",
        )

    def handle_financial_cancel(self, record_id: str) -> None:
        self._run_financial_action(
            lambda access_token: self.api_client.cancel_financial_record(access_token, record_id),
            "Lancamento cancelado.",
        )

    def handle_financial_delete(self, record_id: str) -> None:
        self._run_financial_action(
            lambda access_token: self.api_client.delete_financial_record(access_token, record_id),
            "Lancamento excluido.",
        )

    def _run_financial_action(self, action, success_message: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_financial_form_loading(True)
        try:
            action(self.session.access_token)
        except ApiError as exc:
            self.dashboard_window.set_financial_form_loading(False)
            self.dashboard_window.set_financial_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_financial_form_loading(False)
        self.dashboard_window.set_financial_form_status(success_message)
        self.load_module("financial")
