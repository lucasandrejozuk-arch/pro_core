from __future__ import annotations

from frontend.app.core.api_client import ApiError


class EquipmentHandlersMixin:
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
