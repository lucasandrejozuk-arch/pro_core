from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
)

from frontend.app.core.inventory_catalog import (
    categories_for_group,
    required_field_keys_for_category,
    technical_field_labels_for_category,
    technical_fields_for_category,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin6:
    def _initialize_inventory_wizard(self) -> None:
        self.inventory_wizard_step = 0
        self.inventory_active_stock_group = "components"
        self.selected_inventory_document_path = None
        self._sync_inventory_categories()
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
                    lambda _checked=False, doc_id=document_id, name=file_name: self.inventory_document_download_requested.emit(
                        doc_id, name
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

    def _populate_service_order_form(self, service_order: dict[str, Any]) -> None:
        self.selected_service_order_id = str(service_order["id"])
        self.service_order_custom_id_input.setText(
            str(service_order.get("custom_id") or service_order.get("code") or "")
        )
        self._select_combo_value(
            self.service_order_customer_combo,
            str(service_order.get("customer_id") or ""),
        )
        selected_equipment = self._service_order_equipment_by_id(service_order.get("equipment_id"))
        if selected_equipment is not None:
            self._select_combo_value(
                self.service_order_equipment_type_combo,
                str(selected_equipment.get("category") or ""),
            )
        self._refresh_service_order_equipment_combo()
        self._select_combo_value(
            self.service_order_equipment_combo,
            str(service_order.get("equipment_id") or ""),
        )
        self._select_combo_value(
            self.service_order_technician_combo,
            str(service_order.get("assigned_technician_id") or ""),
        )
        self._select_combo_value(
            self.service_order_priority_combo,
            str(service_order.get("priority") or "normal"),
        )
        self._select_combo_value(
            self.service_order_service_type_combo,
            str(service_order.get("service_type") or "repair"),
        )
        self._select_combo_value(
            self.service_order_status_combo,
            str(service_order.get("status") or "open"),
        )
        self._select_combo_value(
            self.service_order_customer_approval_combo,
            str(service_order.get("customer_approval") or "pending"),
        )
        self.service_order_entry_date_input.setText(
            str(service_order.get("entry_date") or str(service_order.get("created_at") or "")[:10])
        )
        self.service_order_budget_sent_at_input.setText(
            str(service_order.get("budget_sent_at") or "")
        )
        self.service_order_sla_input.setText(str(service_order.get("sla_due_at") or ""))
        self.service_order_special_number_input.setText(
            str(
                (selected_equipment or {}).get("special_number")
                or service_order.get("special_number")
                or ""
            )
        )
        self.service_order_serial_number_input.setText(
            str(
                (selected_equipment or {}).get("serial_number")
                or service_order.get("serial_number")
                or ""
            )
        )
        self.service_order_problem_input.setText(
            str(service_order.get("problem_description") or "")
        )
        self.service_order_diagnosis_input.setText(
            str(service_order.get("technical_diagnosis") or "")
        )
        self.service_order_inspection_visual_input.setPlainText(
            str(service_order.get("inspection_visual") or "")
        )
        self.service_order_proposed_solution_input.setPlainText(
            str(service_order.get("proposed_solution") or "")
        )
        self.service_order_proposed_actions_input.setPlainText(
            str(service_order.get("proposed_actions") or "")
        )
        self.service_order_intake_checklist_input.setPlainText(
            str(service_order.get("intake_checklist") or "")
        )
        self.service_order_linked_objects_input.setPlainText(
            str(service_order.get("linked_objects") or "")
        )
        self.service_order_parts_used_input.setPlainText(str(service_order.get("parts_used") or ""))
        self.service_order_workflow_history_input.setPlainText(
            str(service_order.get("workflow_history") or "")
        )
        self.service_order_notes_input.setPlainText(str(service_order.get("notes") or ""))
        self.service_order_rejection_input.setText(str(service_order.get("rejection_reason") or ""))
        self.service_order_budget_description_input.clear()
        self.service_order_budget_quantity_input.setText("1")
        self.service_order_budget_unit_price_input.setText("0")
        self.selected_service_order_document_path = None
        self.service_order_document_path_input.clear()
        self.service_order_current_status.setText(
            f"Status: {self._format_value(service_order.get('status'))}"
        )
        self._update_service_order_workflow(str(service_order.get("status") or ""))
        self.service_order_full_summary.setPlainText(
            self._format_service_order_full_summary(service_order)
        )
        self.service_order_budget_summary.setText(self._format_service_order_budget(service_order))
        self.service_order_documents_summary.setText(
            self._format_service_order_documents(service_order)
        )
        self._set_service_order_flow_buttons_enabled(True, str(service_order.get("status") or ""))
        self.service_order_delete_button.setEnabled(self._can_delete_service_order())
        self.set_service_order_form_status("Editando ordem de servico selecionada.")

    def _request_service_order_save(self) -> None:
        customer_id = self.service_order_customer_combo.currentData()
        equipment_id = self.service_order_equipment_combo.currentData()
        technician_id = self.service_order_technician_combo.currentData()
        problem_description = self.service_order_problem_input.text().strip()

        if not customer_id:
            self.set_service_order_form_status("Selecione um cliente.", is_error=True)
            return

        if not equipment_id:
            self.set_service_order_form_status("Selecione um equipamento.", is_error=True)
            return

        if not problem_description:
            self.set_service_order_form_status("Informe o problema da OS.", is_error=True)
            return

        if self.selected_service_order_id:
            payload = {
                "assigned_technician_id": str(technician_id) if technician_id else None,
                "priority": str(self.service_order_priority_combo.currentData() or "normal"),
                "sla_due_at": self._optional_text(self.service_order_sla_input),
                "problem_description": problem_description,
                "technical_diagnosis": self._optional_text(self.service_order_diagnosis_input),
                "rejection_reason": self._optional_text(self.service_order_rejection_input),
            }
            self.service_order_update_requested.emit(self.selected_service_order_id, payload)
            return

        payload = {
            "customer_id": str(customer_id),
            "equipment_id": str(equipment_id),
            "assigned_technician_id": str(technician_id) if technician_id else None,
            "priority": str(self.service_order_priority_combo.currentData() or "normal"),
            "sla_due_at": self._optional_text(self.service_order_sla_input),
            "problem_description": problem_description,
        }
        self.service_order_create_requested.emit(payload)

    def _service_order_equipment_by_id(self, equipment_id: Any) -> dict[str, Any] | None:
        for equipment in self.service_order_equipment:
            if str(equipment.get("id")) == str(equipment_id):
                return equipment
        return None

    def _request_service_order_delete(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return
        if not self._can_delete_service_order():
            self.set_service_order_form_status(
                "Apenas administradores e gestores podem excluir OS.",
                is_error=True,
            )
            return
        if not confirm_destructive_action(
            self,
            "Excluir OS",
            "Excluir a ordem de servico selecionada?",
        ):
            return
        self.service_order_delete_requested.emit(self.selected_service_order_id)

    def _request_service_order_diagnosis(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return

        diagnosis = self.service_order_diagnosis_input.text().strip()
        if not diagnosis:
            self.set_service_order_form_status("Informe o diagnostico tecnico.", is_error=True)
            return

        self.set_service_order_form_status("")
        self.service_order_diagnosis_requested.emit(self.selected_service_order_id, diagnosis)

    def _request_service_order_budget_item(self) -> None:
        if not self.selected_service_order_id:
            self.set_service_order_form_status("Selecione uma OS.", is_error=True)
            return

        description = self.service_order_budget_description_input.text().strip()
        if not description:
            self.set_service_order_form_status("Informe a descricao do item.", is_error=True)
            return

        quantity = self._decimal_text_for_service_order(
            self.service_order_budget_quantity_input,
            "Quantidade",
            allow_zero=False,
        )
        unit_price = self._decimal_text_for_service_order(
            self.service_order_budget_unit_price_input,
            "Valor unitario",
            allow_zero=True,
        )
        if quantity is None or unit_price is None:
            return

        payload = {
            "inventory_item_id": None,
            "item_type": str(self.service_order_budget_type_combo.currentData() or "service"),
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
        }
        self.set_service_order_form_status("")
        self.service_order_budget_item_requested.emit(self.selected_service_order_id, payload)

    def _request_service_order_submit_quote(self) -> None:
        if self._require_selected_service_order():
            self.service_order_submit_quote_requested.emit(self.selected_service_order_id)

    def _request_service_order_approve(self) -> None:
        if self._require_selected_service_order():
            self.service_order_approve_requested.emit(self.selected_service_order_id)

    def _request_service_order_reject(self) -> None:
        if not self._require_selected_service_order():
            return

        rejection_reason = self.service_order_rejection_input.text().strip()
        if not rejection_reason:
            self.set_service_order_form_status("Informe o motivo da reprovacao.", is_error=True)
            return

        self.service_order_reject_requested.emit(self.selected_service_order_id, rejection_reason)

    def _request_service_order_start(self) -> None:
        if self._require_selected_service_order():
            self.service_order_start_requested.emit(self.selected_service_order_id)

    def _request_service_order_complete(self) -> None:
        if self._require_selected_service_order():
            self.service_order_complete_requested.emit(self.selected_service_order_id)

    def _select_service_order_document(self) -> None:
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Selecionar anexo",
            "",
            "Arquivos (*.*)",
        )
        if not file_path:
            return

        self.selected_service_order_document_path = file_path
        self.service_order_document_path_input.setText(file_path)

    def _request_service_order_document_upload(self) -> None:
        if not self._require_selected_service_order():
            return

        file_path = self.selected_service_order_document_path
        if not file_path:
            self.set_service_order_form_status("Selecione um arquivo.", is_error=True)
            return

        if not Path(file_path).exists():
            self.set_service_order_form_status("Arquivo selecionado nao existe.", is_error=True)
            return

        document_type = str(self.service_order_document_type_combo.currentData() or "other")
        self.set_service_order_form_status("")
        self.service_order_document_upload_requested.emit(
            self.selected_service_order_id,
            document_type,
            file_path,
        )

    def _require_selected_service_order(self) -> bool:
        if self.selected_service_order_id:
            self.set_service_order_form_status("")
            return True

        self.set_service_order_form_status("Selecione uma OS.", is_error=True)
        return False

    def _handle_service_order_status_changed(self, *_args: Any) -> None:
        status = str(self.service_order_status_combo.currentData() or "")
        self._update_service_order_workflow(status)
        self._set_service_order_flow_buttons_enabled(bool(self.selected_service_order_id), status)

    def _update_service_order_workflow(self, status: str | None) -> None:
        stage_by_status = {
            "open": 0,
            "assigned": 0,
            "pending_tech": 0,
            "diagnosis": 1,
            "pending_quote": 2,
            "quote_sent": 2,
            "pending_approval": 3,
            "approved": 3,
            "in_progress": 4,
            "ready_dispatch": 5,
            "completed": 5,
            "rejected": 5,
            "closed": 5,
        }
        current_stage = stage_by_status.get(status or "", 0)
        for index, label in enumerate(self.service_order_workflow_steps):
            if index < current_stage:
                stage = "done"
            elif index == current_stage:
                stage = "active"
            else:
                stage = "future"
            label.setProperty("stage", stage)
            label.style().unpolish(label)
            label.style().polish(label)
        self._update_service_order_next_step(status)

    def _update_service_order_next_step(self, status: str | None) -> None:
        if not hasattr(self, "service_order_next_step_label"):
            return
        status_key = status or ""
        message, level = {
            "open": (
                "Proximo passo: validar entrada, atribuir tecnico e registrar diagnostico.",
                "warning",
            ),
            "assigned": ("Proximo passo: registrar diagnostico tecnico.", "warning"),
            "pending_tech": ("Proximo passo: atribuir tecnico responsavel.", "warning"),
            "diagnosis": ("Proximo passo: concluir diagnostico e montar orcamento.", "warning"),
            "pending_quote": ("Proximo passo: adicionar itens e enviar orcamento.", "warning"),
            "quote_sent": (
                "Proximo passo: aguardar aprovacao do cliente ou registrar reprovacao.",
                "info",
            ),
            "pending_approval": (
                "Proximo passo: aprovar, reprovar ou complementar o orcamento.",
                "info",
            ),
            "approved": ("Proximo passo: iniciar execucao do servico.", "info"),
            "in_progress": ("Proximo passo: concluir servico e preparar expedicao.", "info"),
            "ready_dispatch": ("Proximo passo: concluir OS apos entrega/expedicao.", "info"),
            "completed": ("Fluxo concluido: revise anexos e historico antes de arquivar.", "info"),
            "rejected": ("Fluxo encerrado: orcamento reprovado pelo cliente.", "error"),
            "closed": ("Fluxo encerrado.", "info"),
        }.get(
            status_key,
            ("Selecione uma OS para ver o proximo passo.", "warning"),
        )
        self.service_order_next_step_label.setText(message)
        self.service_order_next_step_label.setProperty("level", level)
        self.service_order_next_step_label.style().unpolish(self.service_order_next_step_label)
        self.service_order_next_step_label.style().polish(self.service_order_next_step_label)
