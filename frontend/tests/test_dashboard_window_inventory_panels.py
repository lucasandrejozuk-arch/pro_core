from __future__ import annotations

from frontend.app.screens.dashboard import DashboardWindow


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
    assert "Reposicao necessaria: 1" in summary
    assert "Valor em estoque: R$ 180.5" in summary
    assert window.inventory_stock_status.property("level") == "error"
    assert window.inventory_reorder_status.property("level") == "error"
    assert "1 unidade" in window.inventory_reorder_status.text()
    assert "R$ 180.5" in window.inventory_reorder_status.text()


def test_inventory_operational_status_handles_surplus_and_missing_minimum(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_inventory_form(
        {
            "id": "inventory-ok",
            "sku": "FONTE-001",
            "name": "Fonte 24V",
            "quantity": "8",
            "minimum_quantity": "2",
            "unit_cost": "50",
        }
    )

    assert window.inventory_stock_status.property("level") == "info"
    assert window.inventory_reorder_status.property("level") == "info"
    assert "6 unidade" in window.inventory_reorder_status.text()
    assert "R$ 400" in window.inventory_reorder_status.text()

    window._populate_inventory_form(
        {
            "id": "inventory-no-minimum",
            "name": "Cabo",
            "quantity": "3",
            "minimum_quantity": "0",
            "unit_cost": "10",
        }
    )

    assert window.inventory_stock_status.property("level") == "info"
    assert window.inventory_reorder_status.property("level") == "warning"
    assert "sem minimo configurado" in window.inventory_reorder_status.text().lower()


def test_inventory_documents_are_listed_in_step_3(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_inventory_form(
        {
            "id": "inventory-doc-id",
            "name": "Transformador",
            "category": "Transformadores",
            "quantity": "2",
            "minimum_quantity": "1",
            "unit_cost": "10",
            "documents": [
                {"file_name": "datasheet_A.pdf", "document_type": "pdf"},
                {"file_name": "manual_B.pdf", "document_type": "pdf"},
            ],
        }
    )

    listed = window.inventory_documents_summary.toPlainText()
    assert "datasheet_A.pdf" in listed
    assert "manual_B.pdf" in listed
    assert window.inventory_documents_buttons_layout.count() == 2


def test_inventory_transformer_required_fields_validation(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._select_inventory_stock_group("components")
    window.inventory_category_input.setCurrentText("Transformadores")
    window.inventory_name_input.setText("Transformador teste")
    window.inventory_quantity_input.setText("1")
    window.inventory_minimum_quantity_input.setText("0")
    window.inventory_unit_cost_input.setText("1")

    assert (
        window._validate_inventory_category_specific_fields(
            "Transformadores",
            {
                "primary_voltage": "220V",
                "secondary_voltage": "",
                "power": "",
            },
        )
        is False
    )


def test_settings_populates_operational_state(qtbot) -> None:
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

    assert window.sidebar_title.text() == "Pro Assist"
    assert window.sidebar_text.text() == "Bancada premium"
    assert "Pro Assist" in window.settings_operational_status.text()
    assert "Escuro" in window.settings_operational_status.text()
    assert "backup: ativo" in window.settings_backup_status.text().lower()


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
