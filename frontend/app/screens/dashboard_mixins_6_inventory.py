from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFileDialog, QLabel, QLineEdit, QPushButton

from frontend.app.core.id_system import generate_entity_code
from frontend.app.core.inventory_catalog import (
    categories_for_group,
    required_field_keys_for_category,
    technical_field_labels_for_category,
    technical_fields_for_category,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardInventoryActionsMixin:
    def _generate_inventory_sku(self) -> None:
        if self.selected_inventory_item_id:
            return
        prefix_by_group = {
            "components": "CMP",
            "tools": "TLS",
            "software": "SFT",
        }
        group_prefix = prefix_by_group.get(self._current_inventory_stock_group(), "INV")
        self.inventory_sku_input.setText(generate_entity_code(group_prefix))

    def _initialize_inventory_wizard(self) -> None:
        self.inventory_wizard_step = 0
        self.inventory_active_stock_group = "components"
        self.selected_inventory_document_path = None
        self._sync_inventory_categories()
        self._generate_inventory_sku()
        self._set_inventory_wizard_step(0)

    def _set_inventory_wizard_step(self, step_index: int) -> None:
        self.inventory_wizard_step = max(0, min(step_index, 2))
        self.inventory_step_1_panel.setVisible(self.inventory_wizard_step == 0)
        self.inventory_step_2_panel.setVisible(self.inventory_wizard_step == 1)
        self.inventory_step_3_panel.setVisible(self.inventory_wizard_step == 2)

        step_titles = {
            0: "ETAPA 1/3 - CATEGORIA",
            1: "ETAPA 2/3 - DADOS TECNICOS",
            2: "ETAPA 3/3 - CONFIGURACOES FINAIS",
        }
        self.inventory_step_title.setText(step_titles.get(self.inventory_wizard_step, ""))
        self.inventory_back_button.setEnabled(self.inventory_wizard_step > 0)
        self.inventory_next_button.setVisible(self.inventory_wizard_step < 2)
        self.inventory_save_button.setVisible(self.inventory_wizard_step == 2)

    def _go_inventory_previous_step(self) -> None:
        self._set_inventory_wizard_step(self.inventory_wizard_step - 1)

    def _go_inventory_next_step(self) -> None:
        if self.inventory_wizard_step == 0:
            category = str(self.inventory_category_input.currentText() or "").strip()
            if not category:
                self.set_inventory_form_status(
                    "Selecione uma categoria para continuar.", is_error=True
                )
                return
        self._set_inventory_wizard_step(self.inventory_wizard_step + 1)

    def _current_inventory_stock_group(self) -> str:
        index = self.inventory_group_tabs.currentIndex()
        if index < 0 or index >= len(self.inventory_stock_group_keys):
            return "components"
        return self.inventory_stock_group_keys[index]

    def _sync_inventory_categories(self) -> None:
        stock_group = self._current_inventory_stock_group()
        categories = categories_for_group(stock_group)
        previous_category = str(self.inventory_category_input.currentText() or "").strip()
        self.inventory_category_input.blockSignals(True)
        self.inventory_category_input.clear()
        for category in categories:
            self.inventory_category_input.addItem(category)
        self.inventory_category_input.blockSignals(False)
        if previous_category in categories:
            self.inventory_category_input.setCurrentText(previous_category)
        self._rebuild_inventory_dynamic_fields(
            str(self.inventory_category_input.currentText() or "")
        )

    def _handle_inventory_stock_group_changed(self, _index: int) -> None:
        self.inventory_active_stock_group = self._current_inventory_stock_group()
        self._sync_inventory_categories()
        if not self.selected_inventory_item_id:
            self._generate_inventory_sku()
        if self.active_module_key == "inventory":
            self._populate_current_table(self._filtered_rows())

    def _handle_inventory_category_changed(self, _index: int) -> None:
        category = str(self.inventory_category_input.currentText() or "").strip()
        self._rebuild_inventory_dynamic_fields(category)

    def _clear_inventory_dynamic_fields(self) -> None:
        while self.inventory_dynamic_specs_layout.count():
            item = self.inventory_dynamic_specs_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.inventory_dynamic_fields = []

    def _rebuild_inventory_dynamic_fields(self, category: str) -> None:
        self._clear_inventory_dynamic_fields()
        for key, label in technical_fields_for_category(category):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Informe {label.lower()}")
            self.inventory_dynamic_specs_layout.addRow(f"{label}", line_edit)
            self.inventory_dynamic_fields.append((key, line_edit))

    def _current_inventory_technical_data(self) -> dict[str, str]:
        return {
            key: field.text().strip()
            for key, field in self.inventory_dynamic_fields
            if field.text().strip()
        }

    def _populate_inventory_dynamic_data(self, technical_data: dict[str, Any] | None) -> None:
        source = technical_data or {}
        for key, field in self.inventory_dynamic_fields:
            value = source.get(key)
            field.setText(str(value or ""))

    def _select_inventory_stock_group(self, stock_group: str) -> None:
        target = stock_group or "components"
        for index, key in enumerate(self.inventory_stock_group_keys):
            if key == target:
                self.inventory_group_tabs.setCurrentIndex(index)
                self.inventory_active_stock_group = key
                return

    def _select_inventory_document(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Selecionar datasheet",
            "",
            "PDF (*.pdf)",
        )
        if not file_path:
            return
        self.selected_inventory_document_path = file_path
        self.inventory_document_path_input.setText(file_path)

    def _remove_inventory_document(self) -> None:
        self.selected_inventory_document_path = None
        self.inventory_document_path_input.clear()

    def _clear_inventory_document_buttons(self) -> None:
        while self.inventory_documents_buttons_layout.count():
            item = self.inventory_documents_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_inventory_document_buttons(self, documents: list[dict[str, Any]]) -> None:
        self._clear_inventory_document_buttons()
        if not documents:
            self.inventory_documents_buttons_layout.addWidget(
                QLabel("Nenhum anexo disponivel para download.")
            )
            return

        for index, document in enumerate(documents, start=1):
            document_id = str(document.get("id") or "")
            file_name = str(document.get("file_name") or f"anexo_{index}")
            button = QPushButton(f"Baixar {file_name}")
            button.setObjectName("secondaryButton")
            if document_id:
                button.clicked.connect(
                    lambda _checked=False, doc_id=document_id, name=file_name: (
                        self.inventory_document_download_requested.emit(doc_id, name)
                    )
                )
            else:
                button.setEnabled(False)
                button.setText(f"Baixar {file_name} (indisponivel)")
            self.inventory_documents_buttons_layout.addWidget(button)

        if self.inventory_documents_buttons_layout.count() == 0:
            self.inventory_documents_buttons_layout.addWidget(
                QLabel("Nenhum anexo disponivel para download.")
            )

    def _populate_inventory_form(self, item: dict[str, Any]) -> None:
        self.selected_inventory_item_id = str(item["id"])
        self._select_inventory_stock_group(str(item.get("stock_group") or "components"))
        self.inventory_active_stock_group = self._current_inventory_stock_group()
        self._sync_inventory_categories()
        self.inventory_category_input.setCurrentText(str(item.get("category") or ""))
        self.inventory_sku_input.setText(str(item.get("sku") or ""))
        self.inventory_name_input.setText(str(item.get("name") or ""))
        self.inventory_quantity_input.setText(str(item.get("quantity") or "0"))
        self.inventory_minimum_quantity_input.setText(str(item.get("minimum_quantity") or "0"))
        self.inventory_location_input.setText(str(item.get("location") or ""))
        self.inventory_unit_cost_input.setText(str(item.get("unit_cost") or "0"))
        self.inventory_notes_input.setPlainText(str(item.get("notes") or ""))
        technical_data = (
            item.get("technical_data") if isinstance(item.get("technical_data"), dict) else {}
        )
        self._populate_inventory_dynamic_data(technical_data)
        self.inventory_full_summary.setPlainText(self._format_inventory_full_summary(item))
        documents = item.get("documents") if isinstance(item.get("documents"), list) else []
        document_lines = self._format_inventory_documents(documents)
        self.inventory_documents_summary.setPlainText(
            "\n".join(document_lines) if document_lines else "Nenhum anexo vinculado ao item."
        )
        self._render_inventory_document_buttons(documents)
        self.selected_inventory_document_path = None
        self.inventory_document_path_input.clear()
        if self._inventory_is_low(item):
            self._set_inventory_stock_status(
                "Estoque critico: quantidade no minimo ou abaixo.", "error"
            )
        else:
            self._set_inventory_stock_status("Estoque em nivel operacional.", "info")
        self._refresh_inventory_reorder_status(item)
        self._set_inventory_wizard_step(1)
        self.inventory_delete_button.setEnabled(True)
        self.set_inventory_form_status("Editando item selecionado.")

    def _request_inventory_save(self) -> None:
        name = self.inventory_name_input.text().strip()
        if not name:
            self.set_inventory_form_status("Informe o nome do item.", is_error=True)
            return

        quantity = self._decimal_text(self.inventory_quantity_input, "Quantidade")
        minimum_quantity = self._decimal_text(
            self.inventory_minimum_quantity_input,
            "Quantidade minima",
        )
        unit_cost = self._decimal_text(self.inventory_unit_cost_input, "Custo unitario")
        if quantity is None or minimum_quantity is None or unit_cost is None:
            return

        if not self.selected_inventory_item_id and not self.inventory_sku_input.text().strip():
            self._generate_inventory_sku()

        payload = {
            "sku": self._optional_text(self.inventory_sku_input),
            "name": name,
            "category": str(self.inventory_category_input.currentText() or "").strip() or None,
            "stock_group": self._current_inventory_stock_group(),
            "location": self._optional_text(self.inventory_location_input),
            "quantity": quantity,
            "minimum_quantity": minimum_quantity,
            "unit_cost": unit_cost,
            "notes": self.inventory_notes_input.toPlainText().strip() or None,
            "technical_data": self._current_inventory_technical_data() or None,
        }
        if not self._validate_inventory_category_specific_fields(
            str(payload.get("category") or ""),
            dict(payload.get("technical_data") or {}),
        ):
            return
        if self.selected_inventory_document_path:
            payload["_document_path"] = self.selected_inventory_document_path

        self.set_inventory_form_status("")
        if self.selected_inventory_item_id:
            self.inventory_update_requested.emit(self.selected_inventory_item_id, payload)
            return

        self.inventory_create_requested.emit(payload)

    def _request_inventory_delete(self) -> None:
        if not self.selected_inventory_item_id:
            self.set_inventory_form_status("Selecione um item.", is_error=True)
            return
        if not confirm_destructive_action(
            self,
            "Excluir item",
            "Excluir o item de estoque selecionado?",
        ):
            return
        self.inventory_delete_requested.emit(self.selected_inventory_item_id)

    def _refresh_inventory_reorder_status(self, item: dict[str, Any]) -> None:
        quantity = self._safe_float(item.get("quantity"))
        minimum = self._safe_float(item.get("minimum_quantity"))
        unit_cost = self._safe_float(item.get("unit_cost"))
        reorder_quantity = max(0.0, minimum - quantity)
        stock_value = max(0.0, quantity * unit_cost)
        reorder_value = max(0.0, reorder_quantity * unit_cost)

        if reorder_quantity > 0:
            self._set_inventory_reorder_status(
                "Reposicao necessaria: "
                f"{self._format_number(reorder_quantity)} unidade(s), "
                f"custo estimado R$ {self._format_number(reorder_value)}. "
                f"Valor atual em estoque R$ {self._format_number(stock_value)}.",
                "error",
            )
            return

        if minimum > 0:
            surplus = quantity - minimum
            self._set_inventory_reorder_status(
                "Reposicao em dia: "
                f"{self._format_number(surplus)} unidade(s) acima do minimo. "
                f"Valor atual em estoque R$ {self._format_number(stock_value)}.",
                "info",
            )
            return

        self._set_inventory_reorder_status(
            "Reposicao sem minimo configurado. Defina um minimo para gerar alerta operacional. "
            f"Valor atual em estoque R$ {self._format_number(stock_value)}.",
            "warning",
        )

    def _inventory_row_matches_stock_group(self, row: dict[str, Any]) -> bool:
        active_group = str(getattr(self, "inventory_active_stock_group", "components") or "")
        row_group = str(row.get("stock_group") or "components")
        return not active_group or row_group == active_group

    def _validate_inventory_category_specific_fields(
        self,
        category: str,
        technical_data: dict[str, str],
    ) -> bool:
        required_keys = required_field_keys_for_category(category)
        if not required_keys:
            return True
        labels = technical_field_labels_for_category(category)
        missing_labels = [
            labels.get(key, key)
            for key in required_keys
            if not str(technical_data.get(key) or "").strip()
        ]
        if missing_labels:
            self.set_inventory_form_status(
                "Campos obrigatorios para categoria selecionada: "
                + ", ".join(missing_labels)
                + ".",
                is_error=True,
            )
            self._set_inventory_wizard_step(1)
            return False
        return True
