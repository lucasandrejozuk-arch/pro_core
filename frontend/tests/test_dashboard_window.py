from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QEvent

from frontend.app.core.display import build_display_profile
from frontend.app.core.grid import GRID_COLUMNS
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


def test_sidebar_is_fixed_in_main_layout(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    main_area = window.layout().itemAt(1).widget()
    assert main_area.objectName() == "mainArea"
    assert main_area.layout().itemAt(0).widget() is window.sidebar
    assert main_area.layout().itemAt(1).widget().inherits("QScrollArea")
    assert window.sidebar.parentWidget() is main_area


def test_dashboard_content_uses_12_column_grid(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    assert window.content_layout.columnCount() == GRID_COLUMNS
    assert all(window.content_layout.columnStretch(column) == 1 for column in range(GRID_COLUMNS))
    assert window.content_layout.getItemPosition(0) == (0, 0, 1, GRID_COLUMNS)
    assert window.content_layout.rowStretch(5) == 1
    assert window.content_layout.rowStretch(6) == 0
    assert window.content_layout.rowStretch(10) == 0

    window.render_rows("Clientes", [], [("Nome", "name")], "customers")
    assert window.content_layout.rowStretch(6) == 1
    assert window.content_layout.rowStretch(7) == 0

    window._set_dashboard_grid_columns(4)
    assert window.dashboard_grid_layout.getItemPosition(0) == (0, 0, 1, 3)
    assert window.dashboard_grid_layout.getItemPosition(1) == (0, 3, 1, 3)

    window._set_dashboard_grid_columns(2)
    assert window.dashboard_grid_layout.getItemPosition(0) == (0, 0, 1, 6)
    assert window.dashboard_grid_layout.getItemPosition(1) == (0, 6, 1, 6)


def test_record_modules_use_protech_split_shell_and_search(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_rows(
        "Clientes",
        [
            {
                "id": "customer-1",
                "name": "Ana Cliente",
                "email": "ana@example.com",
                "phone": "(11) 99999-0000",
            },
            {
                "id": "customer-2",
                "name": "Bruno Cliente",
                "email": "bruno@example.com",
                "phone": "(11) 98888-0000",
            },
        ],
        [("Nome", "name"), ("Email", "email"), ("Telefone", "phone")],
        "customers",
    )

    assert not window.generic_record_container.isHidden()
    assert not window.record_toggle_rail.isHidden()
    assert window.generic_form_column.isHidden()
    assert window.module_search_input.placeholderText() == "BUSCAR CLIENTES..."

    window.module_search_input.setText("bruno")

    assert window.table.rowCount() == 1
    assert window.current_rows[0]["id"] == "customer-2"
    assert "Bruno Cliente" in window.customer_full_summary.toPlainText()
    assert not window.record_summary_panel.isHidden()
    assert "Bruno Cliente" in window.record_summary_text.toPlainText()


def test_record_editor_button_opens_floating_side_panel(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows(
        "Clientes",
        [{"id": "1", "name": "Cliente"}],
        [("Nome", "name")],
        "customers",
    )

    assert window.record_editor_collapsed is True
    window.record_editor_toggle_button.setChecked(True)

    assert not window.generic_form_column.isHidden()
    assert window.record_editor_toggle_button.property("collapsed") == "false"
    assert window.generic_form_column.parentWidget() is window.record_editor_dialog
    assert window.record_editor_dialog is not None
    assert window.record_editor_dialog.width() >= min(window.record_editor_width, 520)
    assert window.record_editor_toggle_button.text() == "E\nd\ni\nt\no\nr"
    assert window.record_editor_toggle_button.height() > window.record_editor_toggle_button.width()
    assert window.record_toggle_rail.width() <= 56

    window.record_editor_toggle_button.setChecked(False)

    assert window.record_editor_collapsed is True
    assert window.generic_form_column.isHidden()


def test_record_table_context_actions_open_editor_and_clear_form(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows(
        "Clientes",
        [{"id": "customer-id", "name": "Cliente", "email": "c@e.com", "phone": "(11) 99999-0000"}],
        [("Nome", "name")],
        "customers",
    )
    window._populate_customer_form(window.current_rows[0])

    window._new_current_record_from_context()

    assert window.selected_customer_id is None
    assert not window.generic_form_column.isHidden()
    assert window.record_editor_toggle_button.isChecked()
    assert window.record_editor_dialog is not None


def test_visual_density_is_compact_after_polish(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    form_margins = window.customer_form_panel.layout().contentsMargins()

    assert window.table.verticalHeader().defaultSectionSize() == 34
    assert form_margins.left() <= 10
    assert window.dashboard_cards["service_orders_open"].minimumHeight() == 88


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

    assert window.module_buttons["admin_area"].isHidden()
    assert window.module_buttons["settings"].isHidden()


def test_customer_module_is_hidden_for_technician(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.set_user(
        {
            "full_name": "Tecnico",
            "email": "tecnico@example.com",
            "role": "technician",
        }
    )

    assert window.module_buttons["customers"].isHidden()
    assert window.dashboard_cards["customers_total"].isHidden()


def test_record_delete_buttons_emit_selected_ids(qtbot, monkeypatch) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    monkeypatch.setattr(
        "frontend.app.screens.dashboard.confirm_destructive_action",
        lambda *args, **kwargs: True,
    )
    emitted: list[tuple[str, str]] = []
    window.customer_delete_requested.connect(lambda value: emitted.append(("customer", value)))
    window.inventory_delete_requested.connect(lambda value: emitted.append(("inventory", value)))
    window.service_order_delete_requested.connect(
        lambda value: emitted.append(("service_order", value))
    )
    window.sector_delete_requested.connect(lambda value: emitted.append(("sector", value)))
    window.user_delete_requested.connect(lambda value: emitted.append(("user", value)))
    window.audit_delete_requested.connect(lambda value: emitted.append(("audit", value)))

    window.render_rows(
        "Clientes",
        [{"id": "customer-id", "name": "Cliente", "email": "c@e.com", "phone": "(11) 99999-0000"}],
        [("Nome", "name")],
        "customers",
    )
    window._request_customer_delete()

    window.render_rows(
        "Estoque",
        [{"id": "item-id", "name": "Peca", "quantity": "1", "minimum_quantity": "0"}],
        [("Nome", "name")],
        "inventory",
    )
    window._request_inventory_delete()

    window.set_service_order_dependencies(
        customers=[{"id": "customer-id", "name": "Cliente"}],
        equipment=[{"id": "equipment-id", "category": "Fonte"}],
        technicians=[],
    )
    window.render_rows(
        "Ordens",
        [
            {
                "id": "os-id",
                "code": "OS-1",
                "customer_id": "customer-id",
                "equipment_id": "equipment-id",
                "status": "open",
                "problem_description": "Nao liga",
            }
        ],
        [("Codigo", "code")],
        "service_orders",
    )
    window._request_service_order_delete()

    window.render_rows(
        "Setores",
        [{"id": "sector-id", "name": "Laboratorio", "description": "Bancada"}],
        [("Nome", "name")],
        "sectors",
    )
    window._request_sector_delete()

    window.render_rows(
        "Usuarios",
        [
            {
                "id": "user-id",
                "full_name": "Tecnico",
                "email": "tecnico@example.com",
                "role": "technician",
                "is_active": True,
            }
        ],
        [("Nome", "full_name")],
        "users",
    )
    window._request_user_delete()

    window.render_rows(
        "Logs",
        [{"id": "log-id", "action": "delete", "entity_type": "customers", "summary": "Teste"}],
        [("Acao", "action")],
        "audit_logs",
    )
    window._request_audit_delete()

    assert emitted == [
        ("customer", "customer-id"),
        ("inventory", "item-id"),
        ("service_order", "os-id"),
        ("sector", "sector-id"),
        ("user", "user-id"),
        ("audit", "log-id"),
    ]


def test_session_footer_shows_session_context(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.set_user(
        {
            "full_name": "Admin",
            "email": "admin@example.com",
            "role": "admin",
            "sector_name": "Diretoria",
        }
    )
    window.set_session_login_at(datetime(2026, 5, 14, 22, 25, 19))
    window._set_active_module("equipment")

    footer_text = window.session_footer_label.text()
    assert "Sessao: Administrador" in footer_text
    assert "Setor: Diretoria" in footer_text
    assert "Login: 2026-05-14 22:25:19" in footer_text
    assert window.session_module_label.text() == "Equipamentos"


def test_sidebar_collapse_keeps_fixed_lateral_rail_without_moving_content(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    initial_width = window.sidebar.width()
    initial_left_margin = window.content_layout.contentsMargins().left()

    window._set_sidebar_collapsed(True)

    assert not window.sidebar_nav_container.isHidden()
    assert not window.session_button.isHidden()
    assert not window.logout_button.isHidden()
    assert window.sidebar.width() == initial_width
    assert window.sidebar.height() > 52
    assert window.sidebar.parentWidget().objectName() == "mainArea"
    assert window.content_layout.contentsMargins().left() == initial_left_margin


def test_dashboard_applies_responsive_display_profile(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    profile = build_display_profile(1366, 768)

    window.apply_display_profile(profile)

    assert window.sidebar.minimumWidth() == profile.sidebar_width
    assert window.sidebar.maximumWidth() == profile.sidebar_width
    assert window.content_layout.contentsMargins().left() == profile.content_margin
    assert window.dashboard_grid_columns == 2


def test_sidebar_uses_icon_only_navigation(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    dashboard_button = window.module_buttons["dashboard"]

    assert dashboard_button.text() == ""
    assert not dashboard_button.icon().isNull()
    assert dashboard_button.toolTip()


def test_admin_modules_are_regular_sidebar_items_for_admin(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})

    assert "admin_area" in window.module_buttons
    assert not window.module_buttons["admin_area"].isHidden()
    assert not window.module_buttons["settings"].isHidden()
    assert window._allowed_admin_modules() == (
        "sectors",
        "users",
        "password_resets",
        "audit_logs",
        "settings",
    )


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
