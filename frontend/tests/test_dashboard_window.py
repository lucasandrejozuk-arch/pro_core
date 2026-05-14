from __future__ import annotations

from PySide6.QtCore import QEvent

from frontend.app.screens.dashboard import DashboardWindow


def test_dashboard_is_independent_active_sidebar_module(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_dashboard(
        {
            "greeting": "Bom dia, Admin.",
            "last_refresh": "Atualizado: 10:00:00",
            "cards": {
                "service_orders_open": 3,
                "service_orders_pending": 1,
                "inventory_total": 8,
                "inventory_low": 2,
                "customers_total": 5,
                "equipment_total": 7,
                "users_total": 4,
                "system_health": 3,
            },
            "alerts": [{"message": "1 OS aguardando aprovacao.", "level": "warning"}],
        }
    )

    assert window.active_module_key == "dashboard"
    assert window.module_buttons["dashboard"].property("active") == "true"
    assert window.module_buttons["customers"].property("active") == "false"
    assert not window.dashboard_grid_widget.isHidden()
    assert window.table.isHidden()
    assert window.title_label.text() == "Painel Principal"
    assert window.dashboard_cards["service_orders_open"].value_label.text() == "3"
    assert window.dashboard_cards["inventory_low"].value_label.text() == "2"


def test_switching_modules_hides_dashboard_grid_and_marks_nav(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_rows("Clientes", [], [("Nome", "name")], "customers")

    assert window.active_module_key == "customers"
    assert window.module_buttons["dashboard"].property("active") == "false"
    assert window.module_buttons["customers"].property("active") == "true"
    assert window.dashboard_grid_widget.isHidden()
    assert not window.customer_form_panel.isHidden()


def test_admin_modules_are_hidden_for_technician(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.set_user(
        {
            "full_name": "Tecnico",
            "email": "tecnico@example.com",
            "role": "technician",
        }
    )

    assert window.module_buttons["users"].isHidden()
    assert window.module_buttons["password_resets"].isHidden()
    assert window.module_buttons["sectors"].isHidden()
    assert window.module_buttons["settings"].isHidden()
    assert window.module_buttons["reports"].isHidden()


def test_combo_mouse_wheel_is_blocked_to_prevent_accidental_changes(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    wheel_event = QEvent(QEvent.Type.Wheel)
    regular_event = QEvent(QEvent.Type.MouseButtonPress)

    assert window.eventFilter(window.equipment_customer_combo, wheel_event) is True
    assert window.eventFilter(window.equipment_customer_combo, regular_event) is False


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
    assert "Cliente Teste" in window.service_order_full_summary.toPlainText()
    assert "Notebook - Dell - Latitude - NE-01 - SER-01" in (
        window.service_order_full_summary.toPlainText()
    )


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
