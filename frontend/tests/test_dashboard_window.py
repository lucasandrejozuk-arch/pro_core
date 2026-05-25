from __future__ import annotations

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
    assert "primeiro cliente" in window.module_guidance_label.text().lower()


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
    assert window.content_layout.getItemPosition(1) == (1, 0, 1, GRID_COLUMNS)
    assert window.content_layout.rowStretch(1) == 0
    window.render_rows("Clientes", [], [("Nome", "name")], "customers")
    assert window.content_layout.rowStretch(1) == 1
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
    assert window.record_toggle_rail.isHidden()
    assert window.generic_form_column.isHidden()
    assert window.data_title.text() == "Clientes"
    assert window.record_count_label.text() == "2 registro(s)"
    assert window.module_search_input.placeholderText() == "BUSCAR CLIENTES..."
    window.module_search_input.setText("bruno")
    assert window.table.rowCount() == 1
    assert window.table.maximumHeight() > 10000
    assert window.record_count_label.text() == "1 de 2 registro(s)"
    assert window.current_rows[0]["id"] == "customer-2"
    assert "Bruno Cliente" in window.customer_full_summary.toPlainText()
    assert not window.record_summary_panel.isHidden()
    assert "Bruno Cliente" in window.record_summary_text.toPlainText()
    assert "cliente em foco" in window.module_guidance_label.text().lower()


def test_record_module_guidance_returns_to_browse_after_clear_selection(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows(
        "Clientes",
        [{"id": "customer-1", "name": "Ana Cliente", "email": "ana@example.com"}],
        [("Nome", "name"), ("Email", "email")],
        "customers",
    )

    window._clear_current_selection()

    assert "selecione um cliente" in window.module_guidance_label.text().lower()


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
    window.command_editor_button.click()
    assert not window.generic_form_column.isHidden()
    assert window.generic_form_column.parentWidget() is window.record_editor_dialog
    assert window.record_editor_dialog is not None
    assert window.record_editor_dialog.width() >= min(window.record_editor_width, 520)
    assert window.command_editor_button.text() == "Fechar editor"
    assert window.record_toggle_rail.width() == 0
    window.command_editor_button.click()
    assert window.record_editor_collapsed is True
    assert window.generic_form_column.isHidden()
    assert window.command_editor_button.text() == "Editor"


def test_service_orders_editor_button_opens_fixed_floating_side_panel(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.resize(1680, 960)
    window.show()
    window.render_rows(
        "Ordens de Servico",
        [{"id": "so-1", "ticket": "OS-001", "status": "open"}],
        [("OS", "ticket"), ("Status", "status")],
        "service_orders",
    )

    assert not window.record_toggle_rail.isHidden()
    assert window.record_toggle_rail.parentWidget() is window
    assert window.record_editor_collapsed is True
    list_width_before = window.generic_record_container.width()

    window.command_editor_button.click()

    assert window.record_editor_collapsed is False
    assert window.record_editor_dialog is None
    assert window.generic_form_column.parentWidget() is window
    assert not window.generic_form_column.isHidden()
    assert 760 <= window.generic_form_column.width() <= 900
    assert (
        window.generic_form_column.geometry().right() < window.record_toggle_rail.geometry().left()
    )
    assert window.record_toggle_rail.geometry().right() <= window.width() - 8
    assert window.generic_record_container.width() == list_width_before
    assert window.command_editor_button.text() == "Fechar editor"

    window.command_editor_button.click()

    assert window.record_editor_collapsed is True
    assert window.generic_form_column.isHidden()
    assert window.command_editor_button.text() == "Editor"


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
    assert window.record_editor_collapsed is False
    assert window.record_editor_dialog is not None


def test_visual_density_is_compact_after_polish(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    form_margins = window.customer_form_panel.layout().contentsMargins()
    assert window.table.verticalHeader().defaultSectionSize() == 34
    assert form_margins.left() <= 10
    assert window.dashboard_cards["service_orders_open"].minimumHeight() == 88


def test_record_delete_buttons_emit_selected_ids(qtbot, monkeypatch) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})
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


def test_sidebar_collapse_keeps_fixed_lateral_rail_without_moving_content(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    initial_width = window.sidebar.width()
    initial_left_margin = window.content_layout.contentsMargins().left()
    window._set_sidebar_collapsed(True)
    assert not window.sidebar_nav_container.isHidden()
    assert not window.logout_button.isHidden()
    assert not window.exit_button.isHidden()
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


def test_dashboard_footer_backend_status_accepts_health_probe_message(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    assert window.backend_status_text.text() == "Backend: verificando"
    assert window.backend_status_dot.property("level") == "warning"
    window.set_backend_connection_status(False, "Backend: erro 500")
    assert window.backend_status_text.text() == "Backend: erro 500"
    assert window.backend_status_dot.property("level") == "error"
    window.set_backend_connection_status(False, "Backend: atualizando", level="warning")
    assert window.backend_status_text.text() == "Backend: atualizando"
    assert window.backend_status_dot.property("level") == "warning"


def test_modules_show_current_context_without_stage_badge(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_dashboard({})
    assert not hasattr(window, "command_stage_label")
    assert not hasattr(window, "command_hint_label")
    assert window.command_context_label.text() == "Dashboard"
    assert not window.command_refresh_button.isHidden()
    assert window.command_editor_button.isHidden()
    assert not hasattr(window, "session_module_label")
    window.render_rows("Clientes", [], [("Nome", "name")], "customers")
    assert window.command_context_label.text() == "Clientes"
    assert window.title_label.text() == "Clientes"
    assert window.data_title.text() == "Clientes"
    assert not window.command_editor_button.isHidden()
    assert not window.command_clear_selection_button.isHidden()
    window.render_rows("Estoque", [], [("Nome", "name")], "inventory")
    assert window.command_context_label.text() == "Estoque"
    assert window.title_label.text() == "Estoque"
    assert window.data_title.text() == "Estoque"
