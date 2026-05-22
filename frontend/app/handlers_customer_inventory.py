from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from frontend.app.core.api_client import ApiError


class CustomerInventoryHandlersMixin:
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

    def handle_inventory_create(self, payload: dict) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        document_path = str(payload.pop("_document_path", "") or "").strip() or None
        self.dashboard_window.set_inventory_form_loading(True)
        try:
            created_item = self.api_client.create_inventory_item(self.session.access_token, payload)
            if document_path:
                self.api_client.upload_document(
                    access_token=self.session.access_token,
                    file_path=document_path,
                    document_type="pdf",
                    inventory_item_id=str(created_item.get("id") or ""),
                )
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

        document_path = str(payload.pop("_document_path", "") or "").strip() or None
        self.dashboard_window.set_inventory_form_loading(True)
        try:
            self.api_client.update_inventory_item(self.session.access_token, item_id, payload)
            if document_path:
                self.api_client.upload_document(
                    access_token=self.session.access_token,
                    file_path=document_path,
                    document_type="pdf",
                    inventory_item_id=item_id,
                )
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

    def handle_inventory_document_download(self, document_id: str, file_name: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        target_path, _selected_filter = QFileDialog.getSaveFileName(
            self.dashboard_window,
            "Salvar anexo",
            str(Path(file_name or "anexo.pdf").name),
            "Todos os arquivos (*.*)",
        )
        if not target_path:
            return

        self.dashboard_window.set_inventory_form_loading(True)
        try:
            content = self.api_client.download_document(self.session.access_token, document_id)
            Path(target_path).write_bytes(content)
        except ApiError as exc:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(exc.display_message, is_error=True)
            return
        except OSError:
            self.dashboard_window.set_inventory_form_loading(False)
            self.dashboard_window.set_inventory_form_status(
                "Nao foi possivel salvar o arquivo no destino selecionado.",
                is_error=True,
            )
            return

        self.dashboard_window.set_inventory_form_loading(False)
        self.dashboard_window.set_inventory_form_status("Anexo baixado com sucesso.")

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

    def handle_sector_delete(self, sector_id: str) -> None:
        if not self.session.access_token:
            self.show_login()
            return

        self.dashboard_window.set_sector_form_loading(True)
        try:
            self.api_client.delete_sector(self.session.access_token, sector_id)
        except ApiError as exc:
            self.dashboard_window.set_sector_form_loading(False)
            self.dashboard_window.set_sector_form_status(exc.display_message, is_error=True)
            return

        self.dashboard_window.set_sector_form_loading(False)
        self.dashboard_window.set_sector_form_status("Setor excluido.")
        self.load_module("sectors")
