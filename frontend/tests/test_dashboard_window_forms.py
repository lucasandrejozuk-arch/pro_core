from __future__ import annotations

from frontend.app.screens.dashboard import DashboardWindow


def test_customer_save_emits_create_payload(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.customer_create_requested.connect(lambda payload: emitted.append(payload))

    window.customer_name_input.setText("Cliente Novo")
    window.customer_email_input.setText("cliente@example.com")
    window.customer_phone_input.setText("(11) 99999-9999")
    window.customer_address_input.setText("Rua Central")
    window.customer_notes_input.setText("Observacao")

    window._request_customer_save()

    assert emitted == [
        {
            "name": "Cliente Novo",
            "email": "cliente@example.com",
            "phone": "(11) 99999-9999",
            "address": "Rua Central",
            "notes": "Observacao",
            "is_active": True,
        }
    ]


def test_customer_save_rejects_incomplete_phone(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.customer_create_requested.connect(lambda payload: emitted.append(payload))

    window.customer_name_input.setText("Cliente Novo")
    window.customer_email_input.setText("cliente@example.com")
    window.customer_phone_input.setText("(11) 9999")

    window._request_customer_save()

    assert emitted == []
    assert window.customer_form_status.text() == ""
    assert "telefone" in window.footer_message_label.text().lower()


def test_customer_save_rejects_invalid_email(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.customer_create_requested.connect(lambda payload: emitted.append(payload))

    window.customer_name_input.setText("Cliente Novo")
    window.customer_email_input.setText("cliente-invalido")
    window.customer_phone_input.setText("(11) 99999-9999")

    window._request_customer_save()

    assert emitted == []
    assert "email valido" in window.footer_message_label.text().lower()


def test_customer_operational_status_and_document_flow(qtbot, tmp_path, monkeypatch) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[tuple[str, str, str]] = []
    window.customer_document_upload_requested.connect(
        lambda customer_id, document_type, file_path: emitted.append(
            (customer_id, document_type, file_path)
        )
    )

    window.clear_customer_form()

    assert "novo cliente" in window.customer_operational_status.text().lower()
    assert window.customer_operational_status.property("level") == "warning"
    assert not window.customer_upload_document_button.isEnabled()

    window._populate_customer_form(
        {
            "id": "customer-id",
            "name": "Cliente Ativo",
            "email": "cliente@example.com",
            "phone": "(11) 99999-9999",
            "is_active": True,
        }
    )

    assert "cliente ativo" in window.customer_operational_status.text().lower()
    assert window.customer_operational_status.property("level") == "info"
    assert "selecione um arquivo" in window.customer_document_status.text().lower()
    assert not window.customer_upload_document_button.isEnabled()

    document_path = tmp_path / "contrato.pdf"
    document_path.write_text("arquivo", encoding="utf-8")
    monkeypatch.setattr(
        "frontend.app.screens.dashboard_mixins_5.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(document_path), "PDF"),
    )

    window._select_customer_document()

    assert window.customer_upload_document_button.isEnabled()
    assert "pronto para envio" in window.customer_document_status.text().lower()

    window._request_customer_document_upload()

    assert emitted == [("customer-id", "other", str(document_path))]

    window.customer_active_checkbox.setChecked(False)

    assert "cliente inativo" in window.customer_operational_status.text().lower()
    assert window.customer_operational_status.property("level") == "error"


def test_service_order_budget_item_emits_payload(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[tuple[str, dict]] = []
    window.service_order_budget_item_requested.connect(
        lambda service_order_id, payload: emitted.append((service_order_id, payload))
    )
    window.selected_service_order_id = "service-order-id"
    window.service_order_budget_description_input.setText("Troca de SSD")
    window.service_order_budget_quantity_input.setText("2")
    window.service_order_budget_unit_price_input.setText("150.00")

    window._request_service_order_budget_item()

    assert emitted == [
        (
            "service-order-id",
            {
                "inventory_item_id": None,
                "item_type": "service",
                "description": "Troca de SSD",
                "quantity": "2",
                "unit_price": "150.00",
            },
        )
    ]


def test_service_order_save_emits_priority_and_sla(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.service_order_create_requested.connect(lambda payload: emitted.append(payload))
    window.set_service_order_dependencies(
        customers=[{"id": "customer-id", "name": "Cliente"}],
        equipment=[{"id": "equipment-id", "customer_id": "customer-id", "category": "Notebook"}],
        technicians=[{"id": "technician-id", "full_name": "Tecnico"}],
    )

    window._select_combo_value(window.service_order_priority_combo, "urgent")
    window.service_order_sla_input.setText("2026-05-20T10:00:00")
    window.service_order_problem_input.setText("Nao liga")

    window._request_service_order_save()

    assert emitted[0]["priority"] == "urgent"
    assert emitted[0]["sla_due_at"] == "2026-05-20T10:00:00"


def test_service_order_filters_equipment_by_type(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_service_order_dependencies(
        customers=[{"id": "customer-id", "name": "Cliente"}],
        equipment=[
            {
                "id": "notebook-id",
                "customer_id": "customer-id",
                "category": "Notebook",
                "brand": "Dell",
            },
            {
                "id": "desktop-id",
                "customer_id": "customer-id",
                "category": "Desktop",
                "brand": "HP",
            },
        ],
        technicians=[],
    )

    window._select_combo_value(window.service_order_equipment_type_combo, "Desktop")

    assert window.service_order_equipment_combo.count() == 1
    assert window.service_order_equipment_combo.currentData() == "desktop-id"


def test_service_order_sla_uses_calendar_popup_and_iso_text(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    assert window.service_order_sla_input.calendarPopup() is True

    window.service_order_sla_input.setText("2026-05-20T10:00:00")

    assert window.service_order_sla_input.text() == "2026-05-20T10:00:00"
