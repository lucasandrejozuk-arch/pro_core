from __future__ import annotations

from PySide6.QtCore import QEvent

from frontend.app.screens.dashboard import DashboardWindow


def test_service_order_delete_is_limited_to_management_profiles(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_user({"full_name": "Tecnico", "email": "tecnico@example.com", "role": "technician"})
    emitted: list[str] = []
    window.service_order_delete_requested.connect(emitted.append)
    window.set_service_order_dependencies(
        customers=[{"id": "customer-id", "name": "Cliente"}],
        equipment=[{"id": "equipment-id", "category": "Fonte"}],
        technicians=[],
    )

    window._populate_service_order_form(
        {
            "id": "os-id",
            "code": "OS-1",
            "customer_id": "customer-id",
            "equipment_id": "equipment-id",
            "status": "open",
            "problem_description": "Nao liga",
        }
    )

    assert not window.service_order_delete_button.isEnabled()

    window._request_service_order_delete()

    assert emitted == []
    assert "administradores e gestores" in window.footer_message_label.text().lower()


def test_combo_mouse_wheel_is_blocked_to_prevent_accidental_changes(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    wheel_event = QEvent(QEvent.Type.Wheel)
    regular_event = QEvent(QEvent.Type.MouseButtonPress)

    assert window.eventFilter(window.service_order_customer_combo, wheel_event) is True
    assert window.eventFilter(window.service_order_customer_combo, regular_event) is False


def test_service_order_populates_workflow_and_full_summary(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_service_order_dependencies(
        customers=[{"id": "customer-id", "name": "Cliente Teste"}],
        equipment=[
            {
                "id": "equipment-id",
                "customer_id": "customer-id",
                "category": "Notebook",
                "brand": "Dell",
                "model": "Latitude",
                "special_number": "NE-01",
                "serial_number": "SER-01",
            }
        ],
        technicians=[{"id": "technician-id", "full_name": "Tecnico Teste"}],
    )

    window._populate_service_order_form(
        {
            "id": "service-order-id",
            "code": "OS-000001",
            "status": "pending_approval",
            "customer_id": "customer-id",
            "equipment_id": "equipment-id",
            "assigned_technician_id": "technician-id",
            "problem_description": "Nao liga",
            "technical_diagnosis": "Fonte com falha",
            "quoted_total": "250.00",
            "created_at": "2026-05-14T10:00:00",
            "budget_items": [],
            "documents": [],
        }
    )

    assert window.service_order_workflow_steps[3].property("stage") == "active"
    assert "aprovar" in window.service_order_next_step_label.text().lower()
    assert window.service_order_approve_button.isEnabled()
    assert window.service_order_reject_button.isEnabled()
    assert not window.service_order_start_button.isEnabled()
    assert "Cliente Teste" in window.service_order_full_summary.toPlainText()
    assert "Notebook - Dell - Latitude - NE-01 - SER-01" in (
        window.service_order_full_summary.toPlainText()
    )


def test_service_order_workflow_actions_follow_status(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_service_order_dependencies(
        customers=[{"id": "customer-id", "name": "Cliente Teste"}],
        equipment=[{"id": "equipment-id", "customer_id": "customer-id", "category": "Notebook"}],
        technicians=[],
    )

    window._populate_service_order_form(
        {
            "id": "service-order-id",
            "code": "OS-000001",
            "status": "open",
            "customer_id": "customer-id",
            "equipment_id": "equipment-id",
            "problem_description": "Nao liga",
        }
    )

    assert window.service_order_workflow_steps[0].property("stage") == "active"
    assert window.service_order_diagnosis_button.isEnabled()
    assert window.service_order_submit_quote_button.isEnabled()
    assert not window.service_order_approve_button.isEnabled()
    assert not window.service_order_start_button.isEnabled()

    window._select_combo_value(window.service_order_status_combo, "approved")

    assert window.service_order_workflow_steps[3].property("stage") == "active"
    assert "iniciar" in window.service_order_next_step_label.text().lower()
    assert window.service_order_start_button.isEnabled()
    assert not window.service_order_approve_button.isEnabled()
    assert not window.service_order_complete_button.isEnabled()

    window._select_combo_value(window.service_order_status_combo, "in_progress")

    assert window.service_order_workflow_steps[4].property("stage") == "active"
    assert window.service_order_complete_button.isEnabled()
    assert not window.service_order_start_button.isEnabled()


def test_customer_populates_complete_summary(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_customer_form(
        {
            "id": "customer-id",
            "name": "Cliente Teste",
            "email": "cliente@example.com",
            "phone": "(11) 99999-9999",
            "address": "Rua Central, 100",
            "notes": "Cliente recorrente",
            "is_active": True,
        }
    )

    summary = window.customer_full_summary.toPlainText()
    assert "Nome: Cliente Teste" in summary
    assert "Email: cliente@example.com" in summary
    assert "Telefone: (11) 99999-9999" in summary
