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

    assert window.admin_menu_button.isHidden()


def test_sidebar_collapse_does_not_resize_sidebar(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    initial_min_width = window.sidebar.minimumWidth()
    initial_max_width = window.sidebar.maximumWidth()

    window._set_sidebar_collapsed(True)

    assert window.sidebar_nav_container.isHidden()
    assert not window.sidebar_collapsed_label.isHidden()
    assert window.sidebar.minimumWidth() == initial_min_width
    assert window.sidebar.maximumWidth() == initial_max_width


def test_admin_modules_open_from_dedicated_menu(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})

    assert "users" not in window.module_buttons
    assert not window.admin_menu_button.isHidden()
    assert window._allowed_admin_modules() == (
        "financial",
        "notifications",
        "sectors",
        "users",
        "password_resets",
        "settings",
        "reports",
        "audit_logs",
    )


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


def test_equipment_populates_complete_summary_and_tree(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_equipment_customers([{"id": "customer-id", "name": "Cliente Teste"}])

    window._populate_equipment_form(
        {
            "id": "equipment-id",
            "customer_id": "customer-id",
            "category": "Notebook",
            "brand": "Dell",
            "model": "Latitude",
            "special_number": "NE-01",
            "serial_number": "SER-01",
            "description": "Nao liga",
            "boards": [
                {
                    "id": "board-id",
                    "name": "Placa Principal",
                    "special_number": "PL-01",
                    "model": "MAIN",
                    "revision": "A",
                    "components": [
                        {
                            "id": "component-id",
                            "name": "C100",
                            "category": "Capacitor",
                            "part_number": "10uF",
                            "location": "Entrada",
                        }
                    ],
                }
            ],
        }
    )

    summary = window.equipment_full_summary.toPlainText()
    assert "Cliente: Cliente Teste" in summary
    assert "Placas vinculadas: 1" in summary
    assert "Componentes cadastrados: 1" in summary
    assert window.equipment_objects_tree.topLevelItemCount() == 1


def test_inventory_populates_summary_and_low_stock_status(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_inventory_form(
        {
            "id": "inventory-id",
            "sku": "SSD-001",
            "name": "SSD 480GB",
            "category": "Armazenamento",
            "quantity": "1",
            "minimum_quantity": "2",
            "unit_cost": "180.50",
        }
    )

    summary = window.inventory_full_summary.toPlainText()
    assert "SKU: SSD-001" in summary
    assert "Status: Critico" in summary
    assert window.inventory_stock_status.property("level") == "error"


def test_settings_populates_operational_summary(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_settings_form(
        {
            "company_name": "PRO CORE Lab",
            "trade_name": "Assistencia Teste",
            "brand_name": "Pro Assist",
            "brand_subtitle": "Bancada premium",
            "primary_color": "#0f766e",
            "theme": "dark",
            "backup_enabled": True,
            "backup_interval_hours": 12,
            "backup_storage_path": "D:/backups",
            "backup_last_run_at": "2026-05-14T10:00:00",
        }
    )

    summary = window.settings_full_summary.toPlainText()
    assert "Empresa: PRO CORE Lab" in summary
    assert "Nome exibido: Pro Assist" in summary
    assert window.sidebar_title.text() == "Pro Assist"
    assert window.sidebar_text.text() == "Bancada premium"
    assert "Tema: Escuro" in summary
    assert "Backup automatico: Ativo" in summary


def test_admin_forms_populate_complete_summaries(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.current_user_role = "admin"
    window.set_user_sectors([{"id": "sector-id", "name": "Laboratorio"}])

    window._populate_sector_form(
        {"id": "sector-id", "name": "Laboratorio", "description": "Bancada tecnica"}
    )
    window._populate_user_form(
        {
            "id": "user-id",
            "full_name": "Tecnico Teste",
            "email": "tecnico@example.com",
            "role": "technician",
            "sector_id": "sector-id",
            "is_active": True,
            "must_change_password": True,
        }
    )
    window._populate_password_reset_form(
        {
            "id": "request-id",
            "requester_full_name": "Tecnico Teste",
            "requester_email": "tecnico@example.com",
            "requester_role": "technician",
            "status": "pending",
            "created_at": "2026-05-14T10:00:00",
        }
    )

    assert "Nome: Laboratorio" in window.sector_full_summary.toPlainText()
    assert "Setor: Laboratorio" in window.user_full_summary.toPlainText()
    assert "Status: Pendente" in window.password_reset_full_summary.toPlainText()


def test_report_renders_overview_summary(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_report(
        {
            "module": "customers",
            "title": "Relatorio de Clientes",
            "total_records": 1,
            "columns": [{"key": "name", "label": "Nome"}],
            "rows": [{"name": "Cliente Teste"}],
        }
    )

    summary = window.report_full_summary.toPlainText()
    assert "Titulo: Relatorio de Clientes" in summary
    assert "Modulo: Clientes" in summary
    assert "Formatos disponiveis: CSV, XLSX e PDF" in summary


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
    assert "telefone" in window.customer_form_status.text().lower()


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


def test_financial_save_emits_payload(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.financial_create_requested.connect(lambda payload: emitted.append(payload))

    window.financial_description_input.setText("Recebimento OS-000001")
    window.financial_amount_input.setText("300,00")
    window.financial_due_date_input.setText("2026-05-20")
    window.financial_notes_input.setText("Aprovado pelo cliente")

    window._request_financial_save()

    assert emitted == [
        {
            "record_type": "receivable",
            "description": "Recebimento OS-000001",
            "amount": "300.00",
            "due_date": "2026-05-20",
            "notes": "Aprovado pelo cliente",
        }
    ]


def test_financial_populates_summary_and_actions(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_financial_form(
        {
            "id": "record-id",
            "record_type": "receivable",
            "status": "open",
            "description": "Recebimento OS-000001",
            "amount": "300.00",
            "due_date": "2026-05-20",
            "paid_at": None,
            "service_order_id": "service-order-id",
            "notes": "Aprovado",
        }
    )

    assert "Recebimento OS-000001" in window.financial_full_summary.toPlainText()
    assert window.financial_paid_button.isEnabled()


def test_settings_save_rejects_invalid_backup_interval(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_backup_interval_input.setText("0")
    window.settings_backup_path_input.setText("backups")

    window._request_settings_save()

    assert emitted == []
    assert "1 e 720" in window.settings_form_status.text()


def test_settings_save_emits_branding_payload(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_brand_name_input.setText("Pro Assist")
    window.settings_brand_subtitle_input.setText("Laboratorio tecnico")
    window.settings_primary_color_input.setText("#0f766e")
    window.settings_backup_interval_input.setText("24")
    window.settings_backup_path_input.setText("backups")

    window._request_settings_save()

    assert emitted[0]["brand_name"] == "Pro Assist"
    assert emitted[0]["brand_subtitle"] == "Laboratorio tecnico"
    assert emitted[0]["primary_color"] == "#0f766e"


def test_settings_save_rejects_invalid_primary_color(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_primary_color_input.setText("azul")
    window.settings_backup_interval_input.setText("24")
    window.settings_backup_path_input.setText("backups")

    window._request_settings_save()

    assert emitted == []
    assert "#RRGGBB" in window.settings_form_status.text()


def test_report_view_emits_selected_module(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[str] = []
    window.report_view_requested.connect(lambda module_key: emitted.append(module_key))
    window._select_combo_value(window.report_module_combo, "inventory")

    window._request_report_view()

    assert emitted == ["inventory"]
