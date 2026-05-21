from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QTabWidget

from frontend.app.screens.dashboard import DashboardWindow, EquipmentAssetDialog


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
    assert window.tools_tabs.tabText(0) == "Eletrica"
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


def test_audit_log_selection_renders_summary(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_rows(
        "Logs/Auditoria",
        [
            {
                "id": "log-id",
                "action": "customers.delete",
                "entity_type": "customers",
                "entity_id": "customer-id",
                "summary": "Cliente removido",
                "actor_type": "staff",
            }
        ],
        [("Acao", "action")],
        "audit_logs",
    )

    summary = window.audit_full_summary.toPlainText()
    assert "Acao: customers.delete" in summary
    assert "Entidade: Clientes" in summary
    assert "Resumo: Cliente removido" in summary
    assert not window.generic_record_container.isHidden()
    assert not window.audit_form_panel.isHidden()
    assert window.audit_delete_button.isEnabled()
