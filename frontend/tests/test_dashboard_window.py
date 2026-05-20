from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QMessageBox, QTabWidget

from frontend.app.core.display import build_display_profile
from frontend.app.core.grid import GRID_COLUMNS
from frontend.app.screens.dashboard import DashboardWindow, EquipmentAssetDialog


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
    window.financial_delete_requested.connect(lambda value: emitted.append(("financial", value)))

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
        "Financeiro",
        [
            {
                "id": "record-id",
                "record_type": "receivable",
                "description": "Receber",
                "amount": "10",
            }
        ],
        [("Descricao", "description")],
        "financial",
    )
    window._request_financial_delete()

    assert emitted == [
        ("customer", "customer-id"),
        ("inventory", "item-id"),
        ("service_order", "os-id"),
        ("financial", "record-id"),
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
        "financial",
        "reports",
        "notifications",
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


def test_equipment_populates_complete_summary_and_tree(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    rows = [
        {
            "id": "equipment-id",
            "customer_id": None,
            "category": "Notebook",
            "brand": "Dell",
            "model": "Latitude",
            "special_number": "NE-01",
            "serial_number": "SER-01",
            "unit_price": "1500.00",
            "description": "Nao liga",
            "boards": [
                {
                    "id": "board-id",
                    "name": "Placa Principal",
                    "special_number": "PL-01",
                    "model": "MAIN",
                    "revision": "A",
                    "unit_price": "500.00",
                    "components": [
                        {
                            "id": "component-id",
                            "name": "C100",
                            "category": "Capacitor",
                            "part_number": "10uF",
                            "location": "Entrada",
                            "unit_price": "5.00",
                        }
                    ],
                }
            ],
        }
    ]
    window.render_rows("Equipamentos", rows, [], "equipment")

    summary = window.equipment_full_summary.toPlainText()
    assert "Tipo: Notebook" in summary
    assert "Placas vinculadas: 1" in summary
    assert "Componentes cadastrados: 1" in summary
    assert window.equipment_table.rowCount() == 1
    assert window.equipment_boards_table.rowCount() == 1
    assert window.equipment_components_table.rowCount() == 1
    assert "Placa Principal" in window.board_full_summary.toPlainText()
    assert "C100" in window.component_full_summary.toPlainText()


def test_equipment_search_filters_hierarchy(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows(
        "Equipamentos",
        [
            {"id": "eq-1", "category": "Inversor", "brand": "Siemens", "boards": []},
            {"id": "eq-2", "category": "Fonte", "brand": "WEG", "boards": []},
        ],
        [],
        "equipment",
    )

    window.equipment_search_input.setText("weg")

    assert window.equipment_table.rowCount() == 1
    assert window.equipment_visible_rows[0]["id"] == "eq-2"


def test_equipment_import_export_and_defect_case_buttons_emit(qtbot, monkeypatch) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows(
        "Equipamentos",
        [{"id": "eq-1", "category": "Fonte", "brand": "WEG", "boards": []}],
        [],
        "equipment",
    )
    emitted_cases: list[str] = []
    emitted_exports: list[tuple[str, str]] = []
    emitted_imports: list[tuple[str, bool]] = []
    window.equipment_defect_cases_requested.connect(emitted_cases.append)
    window.equipment_export_requested.connect(
        lambda export_format, path: emitted_exports.append((export_format, path))
    )
    window.equipment_import_requested.connect(
        lambda path, replace: emitted_imports.append((path, replace))
    )
    monkeypatch.setattr(
        "frontend.app.screens.dashboard.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: ("C:/tmp/equipamentos.csv", "CSV"),
    )
    monkeypatch.setattr(
        "frontend.app.screens.dashboard.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: ("C:/tmp/equipamentos.csv", "CSV"),
    )
    monkeypatch.setattr(
        "frontend.app.screens.dashboard.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    window._request_equipment_defect_cases_open()
    window._request_equipment_export("csv")
    window._request_equipment_import()

    assert emitted_cases == ["eq-1"]
    assert emitted_exports == [("csv", "C:/tmp/equipamentos.csv")]
    assert emitted_imports == [("C:/tmp/equipamentos.csv", False)]


def test_equipment_asset_dialog_normalizes_money(qtbot) -> None:
    dialog = EquipmentAssetDialog(
        "NOVO EQUIPAMENTO",
        DashboardWindow._equipment_dialog_fields(),
    )
    qtbot.addWidget(dialog)

    dialog.inputs["category"].setText("Inversor")  # type: ignore[union-attr]
    dialog.inputs["unit_price"].setText("1.499,90")  # type: ignore[union-attr]
    dialog._accept()

    assert dialog.payload()["category"] == "Inversor"
    assert dialog.payload()["unit_price"] == "1499.90"


def test_tools_module_renders_role_filtered_calculators(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_tools(
        [
            {"id": "ohm", "name": "Lei de Ohm"},
            {"id": "awg", "name": "AWG/mm2"},
        ]
    )

    assert window.active_module_key == "tools"
    assert not window.tools_form_panel.isHidden()
    assert window.tools_tabs.count() == 1
    assert window.tools_tabs.tabText(0) == "eletrica"
    specialty_tabs = window.tools_tabs.widget(0).findChild(QTabWidget, "specialtyTabs")
    assert specialty_tabs is not None
    assert specialty_tabs.count() == 2
    assert specialty_tabs.tabText(0) == "Lei de Ohm"

    window.ohm_target_combo.setCurrentIndex(0)
    window.ohm_current_input.setText("2")
    window.ohm_resistance_input.setText("10")
    window._calculate_ohm_tool()

    assert "20 V" in window.ohm_result.toPlainText()


def test_ui_scale_slider_emits_live_scale(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[float] = []
    window.ui_scale_changed.connect(emitted.append)

    window.configure_ui_scale(0.86, 1.14, 1.0)
    window.settings_ui_scale_slider.setValue(108)

    assert emitted[-1] == 1.08
    assert window.settings_ui_scale_label.text() == "108%"


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
            "color_palette": "green",
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
    assert "Paleta: Verde operacional" in summary
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
    assert not window.generic_record_container.isHidden()
    assert not window.report_form_panel.isHidden()
    assert window.module_search_input.isHidden()


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
    window._select_combo_value(window.settings_color_palette_combo, "green")
    window.settings_backup_interval_input.setText("24")
    window.settings_backup_path_input.setText("backups")

    window._request_settings_save()

    assert emitted[0]["brand_name"] == "Pro Assist"
    assert emitted[0]["brand_subtitle"] == "Laboratorio tecnico"
    assert emitted[0]["color_palette"] == "green"
    assert "primary_color" not in emitted[0]


def test_settings_save_uses_default_palette(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_backup_interval_input.setText("24")
    window.settings_backup_path_input.setText("backups")

    window._request_settings_save()

    assert emitted[0]["color_palette"] == "blue"


def test_report_view_emits_selected_module(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[str] = []
    window.report_view_requested.connect(lambda module_key: emitted.append(module_key))
    window._select_combo_value(window.report_module_combo, "inventory")

    window._request_report_view()

    assert emitted == ["inventory"]
