# ruff: noqa: E402
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from frontend.app.core.api_client import ApiClient, ApiError
from frontend.app.core.display import build_display_profile, prepare_window_for_display
from frontend.app.core.icons import build_app_icon
from frontend.app.core.session import AppSession
from frontend.app.core.settings import get_frontend_settings
from frontend.app.screens.dashboard import DashboardWindow
from frontend.app.screens.login import LoginWindow
from frontend.app.screens.password_change import PasswordChangeWindow
from frontend.app.screens.splash import SplashScreen
from frontend.app.themes.styles import apply_theme, build_theme_palette


class ProCoreApplication:
    def __init__(self) -> None:
        self._set_windows_app_id()
        self.qt_app = QApplication(sys.argv)
        self.app_icon = build_app_icon()
        self.qt_app.setWindowIcon(self.app_icon)
        self.local_settings = QSettings("PRO CORE", "PRO CORE")
        self._apply_local_theme()

        settings = get_frontend_settings()
        self.api_client = ApiClient(settings.api_base_url)
        self.session = AppSession()

        self.splash = SplashScreen()
        self.login_window = LoginWindow()
        self.password_window = PasswordChangeWindow()
        self.dashboard_window = DashboardWindow()
        self._apply_cached_login_branding()
        for window in (
            self.splash,
            self.login_window,
            self.password_window,
            self.dashboard_window,
        ):
            window.setWindowIcon(self.app_icon)
        self._apply_local_theme()
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
        self.dashboard_window.customer_delete_requested.connect(self.handle_customer_delete)
        self.dashboard_window.customer_document_upload_requested.connect(
            self.handle_customer_document_upload
        )
        self.dashboard_window.equipment_create_requested.connect(self.handle_equipment_create)
        self.dashboard_window.equipment_update_requested.connect(self.handle_equipment_update)
        self.dashboard_window.equipment_delete_requested.connect(self.handle_equipment_delete)
        self.dashboard_window.equipment_board_create_requested.connect(
            self.handle_equipment_board_create
        )
        self.dashboard_window.equipment_board_update_requested.connect(
            self.handle_equipment_board_update
        )
        self.dashboard_window.equipment_board_delete_requested.connect(
            self.handle_equipment_board_delete
        )
        self.dashboard_window.equipment_component_create_requested.connect(
            self.handle_equipment_component_create
        )
        self.dashboard_window.equipment_component_update_requested.connect(
            self.handle_equipment_component_update
        )
        self.dashboard_window.equipment_component_delete_requested.connect(
            self.handle_equipment_component_delete
        )
        self.dashboard_window.equipment_defect_cases_requested.connect(
            self.handle_equipment_defect_cases
        )
        self.dashboard_window.equipment_import_requested.connect(self.handle_equipment_import)
        self.dashboard_window.equipment_export_requested.connect(self.handle_equipment_export)
        self.dashboard_window.inventory_create_requested.connect(self.handle_inventory_create)
        self.dashboard_window.inventory_update_requested.connect(self.handle_inventory_update)
        self.dashboard_window.inventory_delete_requested.connect(self.handle_inventory_delete)
        self.dashboard_window.sector_create_requested.connect(self.handle_sector_create)
        self.dashboard_window.sector_update_requested.connect(self.handle_sector_update)
        self.dashboard_window.service_order_create_requested.connect(
            self.handle_service_order_create
        )
        self.dashboard_window.service_order_update_requested.connect(
            self.handle_service_order_update
        )
        self.dashboard_window.service_order_delete_requested.connect(
            self.handle_service_order_delete
        )
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
        self.dashboard_window.ui_scale_changed.connect(self.handle_ui_scale_changed)
        self.dashboard_window.backup_run_requested.connect(self.handle_backup_run)
        self.dashboard_window.report_view_requested.connect(self.handle_report_view)
        self.dashboard_window.report_export_requested.connect(self.handle_report_export)
        self.dashboard_window.financial_create_requested.connect(self.handle_financial_create)
        self.dashboard_window.financial_mark_paid_requested.connect(self.handle_financial_mark_paid)
        self.dashboard_window.financial_cancel_requested.connect(self.handle_financial_cancel)
        self.dashboard_window.financial_delete_requested.connect(self.handle_financial_delete)

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
        self._refresh_login_branding()
        self.login_window.clear_form()
        profile = prepare_window_for_display(
            self.login_window,
            preferred_size=(1100, 680),
            minimum_size=(760, 520),
        )
        if profile.should_maximize:
            self.login_window.showMaximized()
            return
        self.login_window.show()

    def handle_login(self, email: str, password: str) -> None:
        self.login_window.set_loading(True)

        try:
            auth_response = self.api_client.login(email=email, password=password)
        except ApiError as exc:
            self.login_window.set_loading(False)
            self.login_window.set_backend_connection_status(
                exc.status_code is not None,
                "Backend conectado." if exc.status_code is not None else "Backend indisponivel.",
            )
            self.login_window.set_error(exc.message)
            return

        self.login_window.set_backend_connection_status(True)
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
        prepare_window_for_display(
            self.password_window,
            preferred_size=(700, 520),
            minimum_size=(520, 420),
        )
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
        self.dashboard_window.set_session_login_at(self.session.login_at)
        profile = prepare_window_for_display(
            self.dashboard_window,
            preferred_size=(1680, 960),
            minimum_size=(980, 640),
        )
        profile = build_display_profile(profile.width, profile.height, self._local_ui_scale())
        self.dashboard_window.apply_display_profile(profile)
        self.dashboard_window.showMaximized()
        self.load_module(self.active_module)

    @staticmethod
    def _set_windows_app_id() -> None:
        if sys.platform != "win32":
            return

        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PROCORE.Desktop")
        except Exception:
            return

    def handle_logout(self) -> None:
        self.session.clear()
        self.show_login()

    def refresh_active_module(self) -> None:
        self.load_module(self.active_module)

    def load_module(self, module_key: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        if not self._module_allowed(module_key):
            self.dashboard_window.render_error(
                "Acesso negado",
                "Seu perfil nao possui acesso a este modulo.",
                self.active_module or "dashboard",
            )
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
            if module_key == "tools":
                tools = self.api_client.list_tools(self.session.access_token)
                self.dashboard_window.render_tools(tools)
                return
            if module_key in {"financial", "audit_logs", "notifications"}:
                rows = self._load_module_rows(module_key, self.session.access_token)
                self.dashboard_window.render_rows(title, rows, columns, module_key)
                return

            user_sectors = (
                self.api_client.list_sectors(self.session.access_token)
                if module_key == "users"
                else None
            )
            rows = self._load_module_rows(module_key, self.session.access_token)
            service_order_dependencies = None
            if module_key == "service_orders":
                if str(self.session.user.get("role") or "") in {"admin", "manager"}:
                    service_order_dependencies = (
                        self.api_client.list_customers(self.session.access_token),
                        self.api_client.list_equipment(self.session.access_token),
                        self.api_client.list_technicians(self.session.access_token),
                    )
                else:
                    service_order_dependencies = self._dependencies_from_service_orders(rows)
        except ApiError as exc:
            self.dashboard_window.render_error(title, exc.message, module_key)
            return

        if user_sectors is not None:
            sector_names = {
                str(sector["id"]): str(sector.get("name") or "") for sector in user_sectors
            }
            for row in rows:
                row["sector_name"] = sector_names.get(str(row.get("sector_id")), "")
            self.dashboard_window.set_user_sectors(user_sectors)
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

    def handle_customer_delete(self, customer_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_customer_form_loading(True)
        try:
            self.api_client.delete_customer(self.session.access_token, customer_id)
        except ApiError as exc:
            self.dashboard_window.set_customer_form_loading(False)
            self.dashboard_window.set_customer_form_status(exc.message, is_error=True)
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

    def handle_equipment_delete(self, equipment_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_equipment_form_loading(True)
        try:
            self.api_client.delete_equipment(self.session.access_token, equipment_id)
        except ApiError as exc:
            self.dashboard_window.set_equipment_form_loading(False)
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_equipment_form_status(exc.message, is_error=True)
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
            message = exc.message if isinstance(exc, ApiError) else str(exc)
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
            message = exc.message if isinstance(exc, ApiError) else str(exc)
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

    def handle_inventory_delete(self, item_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_inventory_form_loading(True)
        try:
            self.api_client.delete_inventory_item(self.session.access_token, item_id)
        except ApiError as exc:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(exc.message, is_error=True)
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

    def handle_service_order_delete(self, service_order_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_service_order_form_loading(True)
        try:
            self.api_client.delete_service_order(self.session.access_token, service_order_id)
        except ApiError as exc:
            self.dashboard_window.set_service_order_form_loading(False)
            self.dashboard_window.set_service_order_form_status(exc.message, is_error=True)
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

    def handle_financial_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_financial_form_loading(True)
        try:
            self.api_client.create_financial_record(self.session.access_token, payload)
        except ApiError as exc:
            self.dashboard_window.set_financial_form_loading(False)
            self.dashboard_window.set_financial_form_status(exc.message, is_error=True)
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
            self.dashboard_window.set_financial_form_status(exc.message, is_error=True)
            return

        self.dashboard_window.set_financial_form_loading(False)
        self.dashboard_window.set_financial_form_status(success_message)
        self.load_module("financial")

    def _apply_saved_theme(self) -> None:
        if not self.session.access_token:
            return

        try:
            settings = self.api_client.get_appearance_settings(self.session.access_token)
        except ApiError:
            return

        self._remember_appearance(settings)
        self._apply_local_theme()
        self.dashboard_window.apply_branding(settings)

    def _apply_local_theme(self) -> None:
        theme = str(self.local_settings.value("appearance/theme", "light") or "light")
        primary_color = str(self.local_settings.value("appearance/primary_color", "") or "")
        ui_scale = self._local_ui_scale()
        apply_theme(
            self.qt_app,
            theme,
            primary_color,
            ui_scale,
        )
        if hasattr(self, "dashboard_window"):
            palette = build_theme_palette(theme, primary_color)
            self.dashboard_window.apply_sidebar_icon_color(palette["button_text"])
            self.dashboard_window.apply_record_editor_icon_colors(
                palette["primary"],
                palette["button_text"],
            )

    def _remember_appearance(self, settings: dict) -> None:
        self.local_settings.setValue("appearance/theme", str(settings.get("theme") or "light"))
        self.local_settings.setValue(
            "appearance/primary_color",
            str(settings.get("primary_color") or ""),
        )
        self.local_settings.setValue("appearance/brand_name", str(settings.get("brand_name") or ""))
        self.local_settings.setValue(
            "appearance/brand_subtitle",
            str(settings.get("brand_subtitle") or ""),
        )
        self.login_window.apply_branding(settings)

    def _apply_cached_login_branding(self) -> None:
        self.login_window.apply_branding(
            {
                "brand_name": self.local_settings.value("appearance/brand_name", ""),
                "brand_subtitle": self.local_settings.value("appearance/brand_subtitle", ""),
            }
        )

    def _refresh_login_branding(self) -> None:
        try:
            settings = self.api_client.get_login_appearance_settings()
        except ApiError:
            self.login_window.set_backend_connection_status(False)
            self._apply_cached_login_branding()
            return

        self.login_window.set_backend_connection_status(True)
        self._remember_appearance(settings)

    def _local_ui_scale(self) -> float:
        try:
            return float(self.local_settings.value("appearance/ui_scale", 1.0) or 1.0)
        except (TypeError, ValueError):
            return 1.0

    def _module_allowed(self, module_key: str) -> bool:
        role = str(self.session.user.get("role") or "")
        if module_key == "customers":
            return role in {"admin", "manager"}
        return True

    @staticmethod
    def _dependencies_from_service_orders(
        rows: list[dict],
    ) -> tuple[list[dict], list[dict], list[dict]]:
        customers: dict[str, dict] = {}
        equipment: dict[str, dict] = {}
        for row in rows:
            customer_id = str(row.get("customer_id") or "")
            if customer_id:
                customers[customer_id] = {
                    "id": customer_id,
                    "name": row.get("customer_name") or customer_id,
                    "email": row.get("customer_email") or "",
                }
            equipment_id = str(row.get("equipment_id") or "")
            if equipment_id:
                equipment[equipment_id] = {
                    "id": equipment_id,
                    "category": row.get("equipment_label") or equipment_id,
                    "brand": "",
                    "model": "",
                    "special_number": "",
                    "serial_number": "",
                }
        return list(customers.values()), list(equipment.values()), []

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
        if module_key == "financial":
            return self.api_client.list_financial_records(access_token)
        if module_key == "audit_logs":
            return self.api_client.list_audit_logs(access_token)
        if module_key == "notifications":
            return self.api_client.list_notifications(access_token)
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
        role = str(self.session.user.get("role") or "")
        customers = (
            safe_list("clientes", lambda: self.api_client.list_customers(access_token))
            if role in {"admin", "manager"}
            else []
        )
        equipment = safe_list("equipamentos", lambda: self.api_client.list_equipment(access_token))
        inventory = safe_list("estoque", lambda: self.api_client.list_inventory(access_token))

        users: list[dict] = []
        password_requests: list[dict] = []
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
            len(service_orders_pending) + len(inventory_low) + len(pending_password_requests)
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

        if module_key == "financial":
            return (
                "Financeiro",
                [
                    ("Descricao", "description"),
                    ("Tipo", "record_type"),
                    ("Status", "status"),
                    ("Valor", "amount"),
                    ("Vencimento", "due_date"),
                ],
            )

        if module_key == "audit_logs":
            return (
                "Logs/Auditoria",
                [
                    ("Acao", "action"),
                    ("Entidade", "entity_type"),
                    ("Resumo", "summary"),
                    ("Criado em", "created_at"),
                ],
            )

        if module_key == "notifications":
            return (
                "Notificacoes",
                [
                    ("Canal", "channel"),
                    ("Status", "status"),
                    ("Destinatario", "recipient"),
                    ("Assunto", "subject"),
                    ("Criada em", "created_at"),
                ],
            )

        if module_key == "settings":
            return ("Configuracoes", [])
        if module_key == "reports":
            return ("Relatorios", [])
        if module_key == "tools":
            return ("Ferramentas", [])
        if module_key == "dashboard":
            return ("Dashboard", [])

        return (
            "Ordens de Servico",
            [
                ("Codigo", "code"),
                ("Status", "status"),
                ("Prioridade", "priority"),
                ("Problema", "problem_description"),
                ("Total", "quoted_total"),
                ("SLA", "sla_due_at"),
                ("Criada em", "created_at"),
            ],
        )


def main() -> int:
    return ProCoreApplication().run()


if __name__ == "__main__":
    raise SystemExit(main())
