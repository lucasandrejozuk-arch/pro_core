from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

from frontend.app.core.api_client import ApiClient, ApiError
from frontend.app.core.session import AppSession
from frontend.app.core.settings import get_frontend_settings
from frontend.app.screens.dashboard import DashboardWindow
from frontend.app.screens.login import LoginWindow
from frontend.app.screens.password_change import PasswordChangeWindow
from frontend.app.screens.splash import SplashScreen
from frontend.app.themes.styles import apply_theme


class ProCoreApplication:
    def __init__(self) -> None:
        self.qt_app = QApplication(sys.argv)
        apply_theme(self.qt_app)

        settings = get_frontend_settings()
        self.api_client = ApiClient(settings.api_base_url)
        self.session = AppSession()

        self.splash = SplashScreen()
        self.login_window = LoginWindow()
        self.password_window = PasswordChangeWindow()
        self.dashboard_window = DashboardWindow()
        self.active_module = "dashboard"

        self.splash.finished.connect(self.show_login)
        self.login_window.login_requested.connect(self.handle_login)
        self.login_window.password_reset_requested.connect(self.handle_password_reset_request)
        self.password_window.password_change_requested.connect(self.handle_password_change)
        self.dashboard_window.logout_requested.connect(self.handle_logout)
        self.dashboard_window.module_selected.connect(self.load_module)
        self.dashboard_window.refresh_requested.connect(self.refresh_active_module)
        self.dashboard_window.customer_create_requested.connect(self.handle_customer_create)
        self.dashboard_window.customer_update_requested.connect(self.handle_customer_update)
        self.dashboard_window.customer_document_upload_requested.connect(
            self.handle_customer_document_upload
        )
        self.dashboard_window.equipment_create_requested.connect(self.handle_equipment_create)
        self.dashboard_window.equipment_update_requested.connect(self.handle_equipment_update)
        self.dashboard_window.equipment_board_create_requested.connect(
            self.handle_equipment_board_create
        )
        self.dashboard_window.equipment_component_create_requested.connect(
            self.handle_equipment_component_create
        )
        self.dashboard_window.inventory_create_requested.connect(self.handle_inventory_create)
        self.dashboard_window.inventory_update_requested.connect(self.handle_inventory_update)
        self.dashboard_window.sector_create_requested.connect(self.handle_sector_create)
        self.dashboard_window.sector_update_requested.connect(self.handle_sector_update)
        self.dashboard_window.service_order_create_requested.connect(self.handle_service_order_create)
        self.dashboard_window.service_order_update_requested.connect(self.handle_service_order_update)
        self.dashboard_window.service_order_diagnosis_requested.connect(
            self.handle_service_order_diagnosis
        )
        self.dashboard_window.service_order_budget_item_requested.connect(
            self.handle_service_order_budget_item
        )
        self.dashboard_window.service_order_submit_quote_requested.connect(
            self.handle_service_order_submit_quote
        )
        self.dashboard_window.service_order_approve_requested.connect(
            self.handle_service_order_approve
        )
        self.dashboard_window.service_order_reject_requested.connect(
            self.handle_service_order_reject
        )
        self.dashboard_window.service_order_start_requested.connect(self.handle_service_order_start)
        self.dashboard_window.service_order_complete_requested.connect(
            self.handle_service_order_complete
        )
        self.dashboard_window.service_order_document_upload_requested.connect(
            self.handle_service_order_document_upload
        )
        self.dashboard_window.user_create_requested.connect(self.handle_user_create)
        self.dashboard_window.user_update_requested.connect(self.handle_user_update)
        self.dashboard_window.user_password_reset_requested.connect(self.handle_user_password_reset)
        self.dashboard_window.password_reset_resolve_requested.connect(
            self.handle_password_reset_resolve
        )
        self.dashboard_window.settings_update_requested.connect(self.handle_settings_update)
        self.dashboard_window.backup_run_requested.connect(self.handle_backup_run)
        self.dashboard_window.report_view_requested.connect(self.handle_report_view)
        self.dashboard_window.report_export_requested.connect(self.handle_report_export)

    def run(self) -> int:
        self.splash.start()
        try:
            return self.qt_app.exec()
        finally:
            self.api_client.close()

    def show_login(self) -> None:
        self.splash.close()
        self.password_window.hide()
        self.dashboard_window.hide()
        self.login_window.clear_form()
        self.login_window.show()

    def handle_login(self, email: str, password: str) -> None:
        self.login_window.set_loading(True)

        try:
            auth_response = self.api_client.login(email=email, password=password)
        except ApiError as exc:
            self.login_window.set_loading(False)
            self.login_window.set_error(exc.message)
            return

        self.session.set_authentication(
            access_token=auth_response["access_token"],
            user=auth_response["user"],
        )
        self.login_window.persist_remembered_user(email.strip().lower())
        self.login_window.hide()
        self.login_window.set_loading(False)

        if auth_response.get("must_change_password"):
            self.show_password_change()
            return

        self.show_dashboard()

    def show_password_change(self) -> None:
        self.password_window.clear_form()
        self.password_window.show()

    def handle_password_change(self, current_password: str, new_password: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.password_window.set_loading(True)

        try:
            user = self.api_client.change_password(
                access_token=self.session.access_token,
                current_password=current_password,
                new_password=new_password,
            )
        except ApiError as exc:
            self.password_window.set_loading(False)
            self.password_window.set_error(exc.message)
            return

        self.session.update_user(user)
        self.password_window.hide()
        self.password_window.set_loading(False)
        self.show_dashboard()

    def show_dashboard(self) -> None:
        self._apply_saved_theme()
        self.dashboard_window.set_user(self.session.user)
        self.dashboard_window.show()
        self.load_module(self.active_module)

    def handle_logout(self) -> None:
        self.session.clear()
        self.show_login()

    def refresh_active_module(self) -> None:
        self.load_module(self.active_module)

    def load_module(self, module_key: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.active_module = module_key
        title, columns = self._module_columns(module_key)
        self.dashboard_window.render_loading(title, module_key)

        try:
            if module_key == "dashboard":
                self.dashboard_window.render_dashboard(
                    self._build_dashboard_summary(self.session.access_token)
                )
                return
            if module_key == "settings":
                settings = self.api_client.get_settings(self.session.access_token)
                self.dashboard_window.render_settings(settings)
                return
            if module_key == "reports":
                report = self.api_client.get_report(
                    self.session.access_token,
                    self.dashboard_window.current_report_module_key,
                )
                self.dashboard_window.render_report(report)
                return

            user_sectors = (
                self.api_client.list_sectors(self.session.access_token)
                if module_key == "users"
                else None
            )
            equipment_customers = (
                self.api_client.list_customers(self.session.access_token)
                if module_key == "equipment"
                else None
            )
            service_order_dependencies = (
                (
                    self.api_client.list_customers(self.session.access_token),
                    self.api_client.list_equipment(self.session.access_token),
                    self.api_client.list_technicians(self.session.access_token),
                )
                if module_key == "service_orders"
                else None
            )
            rows = self._load_module_rows(module_key, self.session.access_token)
        except ApiError as exc:
            self.dashboard_window.render_error(title, exc.message, module_key)
            return

        if user_sectors is not None:
            sector_names = {
                str(sector["id"]): str(sector.get("name") or "")
                for sector in user_sectors
            }
            for row in rows:
                row["sector_name"] = sector_names.get(str(row.get("sector_id")), "")
            self.dashboard_window.set_user_sectors(user_sectors)
        if equipment_customers is not None:
            self.dashboard_window.set_equipment_customers(equipment_customers)
        if service_order_dependencies is not None:
            self.dashboard_window.set_service_order_dependencies(*service_order_dependencies)

        self.dashboard_window.render_rows(title, rows, columns, module_key)

    def handle_customer_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_customer_form_loading(True)
        try:
            self.api_client.create_customer(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_customer_form_loading(False)
            self.dashboard_window.set_customer_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_customer_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_customer_form_loading(False)
        self.dashboard_window.set_customer_form_status("Cliente atualizado.")
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
            self.dashboard_window.set_customer_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_equipment_form_loading(False)
        self.dashboard_window.set_equipment_form_status("Equipamento atualizado.")
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Placa vinculada.")
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_equipment_object_loading(False)
        self.dashboard_window.set_equipment_form_status("Componente vinculado.")
        self.load_module("equipment")

    def handle_inventory_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_inventory_form_loading(True)
        try:
            self.api_client.create_inventory_item(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_inventory_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_inventory_form_loading(False)
        self.dashboard_window.set_inventory_form_status("Item de estoque atualizado.")
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
            self.dashboard_window.set_sector_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_sector_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_service_order_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_service_order_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_service_order_form_loading(False)
        self.dashboard_window.set_service_order_form_status("Ordem de servico atualizada.")
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
            self.dashboard_window.set_service_order_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_user_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_user_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_user_form_status(exc.message, is_error=True)
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
            self.login_window.set_error(exc.message)
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
            self.dashboard_window.set_password_reset_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_settings_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_settings_form_loading(False)
        apply_theme(self.qt_app, str(settings.get("theme") or "light"))
        self.dashboard_window.render_settings(settings)
        self.dashboard_window.set_settings_form_status("Configuracoes salvas.")

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
            self.dashboard_window.set_settings_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_report_status(exc.message, is_error=True)
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
            self.dashboard_window.set_report_status(exc.message, is_error=True)
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

    def _apply_saved_theme(self) -> None:
        if not self.session.access_token or self.session.user.get("role") != "admin":
            return

        try:
            settings = self.api_client.get_settings(self.session.access_token)
        except ApiError:
            return

        apply_theme(self.qt_app, str(settings.get("theme") or "light"))

    def _load_module_rows(self, module_key: str, access_token: str) -> list[dict]:
        if module_key == "customers":
            return self.api_client.list_customers(access_token)
        if module_key == "equipment":
            return self.api_client.list_equipment(access_token)
        if module_key == "inventory":
            return self.api_client.list_inventory(access_token)
        if module_key == "users":
            return self.api_client.list_users(access_token)
        if module_key == "password_resets":
            return self.api_client.list_password_reset_requests(access_token)
        if module_key == "sectors":
            return self.api_client.list_sectors(access_token)
        return self.api_client.list_service_orders(access_token)

    def _build_dashboard_summary(self, access_token: str) -> dict:
        alerts: list[dict[str, str]] = []

        def safe_list(label: str, loader) -> list[dict]:
            try:
                return loader()
            except ApiError as exc:
                alerts.append(
                    {
                        "message": f"Nao foi possivel carregar {label}: {exc.message}",
                        "level": "warning",
                    }
                )
                return []

        service_orders = safe_list(
            "ordens de servico",
            lambda: self.api_client.list_service_orders(access_token),
        )
        customers = safe_list("clientes", lambda: self.api_client.list_customers(access_token))
        equipment = safe_list("equipamentos", lambda: self.api_client.list_equipment(access_token))
        inventory = safe_list("estoque", lambda: self.api_client.list_inventory(access_token))

        users: list[dict] = []
        password_requests: list[dict] = []
        role = str(self.session.user.get("role") or "")
        if role in {"admin", "manager"}:
            users = safe_list("usuarios", lambda: self.api_client.list_users(access_token))
            password_requests = safe_list(
                "solicitacoes de senha",
                lambda: self.api_client.list_password_reset_requests(access_token),
            )

        open_statuses = {
            "open",
            "assigned",
            "pending_quote",
            "quote_sent",
            "pending_approval",
            "approved",
            "in_progress",
        }
        service_orders_open = [
            order for order in service_orders if str(order.get("status") or "") in open_statuses
        ]
        service_orders_pending = [
            order
            for order in service_orders
            if str(order.get("status") or "") == "pending_approval"
        ]
        inventory_low = [
            item
            for item in inventory
            if self._to_decimal(item.get("quantity"))
            <= self._to_decimal(item.get("minimum_quantity"))
            and self._to_decimal(item.get("minimum_quantity")) > 0
        ]
        active_customers = [customer for customer in customers if customer.get("is_active", True)]
        active_users = [user for user in users if user.get("is_active", True)]
        pending_password_requests = [
            request
            for request in password_requests
            if str(request.get("status") or "") == "pending"
        ]

        if service_orders_pending:
            alerts.append(
                {
                    "message": f"{len(service_orders_pending)} OS aguardando aprovacao do cliente.",
                    "level": "warning",
                }
            )
        if inventory_low:
            alerts.append(
                {
                    "message": f"{len(inventory_low)} item(ns) com estoque critico.",
                    "level": "error",
                }
            )
        if pending_password_requests:
            alerts.append(
                {
                    "message": (
                        f"{len(pending_password_requests)} solicitacao(oes) de senha "
                        "pendente(s)."
                    ),
                    "level": "warning",
                }
            )

        pending_count = (
            len(service_orders_pending)
            + len(inventory_low)
            + len(pending_password_requests)
        )
        return {
            "greeting": self._dashboard_greeting(),
            "last_refresh": f"Atualizado: {datetime.now().strftime('%H:%M:%S')}",
            "cards": {
                "service_orders_open": len(service_orders_open),
                "service_orders_pending": len(service_orders_pending),
                "inventory_total": len(inventory),
                "inventory_low": len(inventory_low),
                "customers_total": len(active_customers),
                "equipment_total": len(equipment),
                "users_total": len(active_users),
                "system_health": pending_count,
            },
            "alerts": alerts,
        }

    def _dashboard_greeting(self) -> str:
        full_name = str(self.session.user.get("full_name") or "usuario")
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        return f"{greeting}, {full_name}. Acompanhe os indicadores operacionais do dia."

    @staticmethod
    def _to_decimal(value) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _module_columns(module_key: str) -> tuple[str, list[tuple[str, str]]]:
        if module_key == "customers":
            return (
                "Clientes",
                [
                    ("Nome", "name"),
                    ("Email", "email"),
                    ("Telefone", "phone"),
                    ("Ativo", "is_active"),
                ],
            )

        if module_key == "equipment":
            return (
                "Equipamentos",
                [
                    ("Categoria", "category"),
                    ("Marca", "brand"),
                    ("Modelo", "model"),
                    ("N especial", "special_number"),
                    ("Serie", "serial_number"),
                ],
            )

        if module_key == "inventory":
            return (
                "Estoque",
                [
                    ("SKU", "sku"),
                    ("Nome", "name"),
                    ("Quantidade", "quantity"),
                    ("Minimo", "minimum_quantity"),
                    ("Custo", "unit_cost"),
                ],
            )

        if module_key == "users":
            return (
                "Usuarios",
                [
                    ("Nome", "full_name"),
                    ("Email", "email"),
                    ("Perfil", "role"),
                    ("Setor", "sector_name"),
                    ("Ativo", "is_active"),
                    ("Troca senha", "must_change_password"),
                ],
            )

        if module_key == "sectors":
            return (
                "Setores",
                [
                    ("Nome", "name"),
                    ("Descricao", "description"),
                    ("Criado em", "created_at"),
                ],
            )

        if module_key == "password_resets":
            return (
                "Solicitacoes de Senha",
                [
                    ("Solicitante", "requester_full_name"),
                    ("Email", "requester_email"),
                    ("Perfil", "requester_role"),
                    ("Status", "status"),
                    ("Criada em", "created_at"),
                ],
            )

        if module_key == "settings":
            return ("Configuracoes", [])
        if module_key == "reports":
            return ("Relatorios", [])
        if module_key == "dashboard":
            return ("Dashboard", [])

        return (
            "Ordens de Servico",
            [
                ("Codigo", "code"),
                ("Status", "status"),
                ("Problema", "problem_description"),
                ("Total", "quoted_total"),
                ("Criada em", "created_at"),
            ],
        )


def main() -> int:
    return ProCoreApplication().run()


if __name__ == "__main__":
    raise SystemExit(main())
