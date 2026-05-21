from __future__ import annotations

from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QTabWidget

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
    assert "Equipamento selecionado" in window.equipment_operational_status.text()
    assert "1 objeto(s) vinculado(s), 1 componente(s)" in (
        window.equipment_operational_status.text()
    )
    assert "Componente selecionado" in window.equipment_hierarchy_status.text()
    assert "Placa Principal" in window.board_full_summary.toPlainText()
    assert "C100" in window.component_full_summary.toPlainText()
    copy_buttons = window.equipment_form_panel.findChildren(QPushButton, "summaryCopyButton")
    assert len(copy_buttons) == 3

    copy_buttons[0].click()

    assert QApplication.clipboard().text() == window.equipment_full_summary.toPlainText().strip()


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


def test_equipment_operational_status_handles_empty_and_filtered_states(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_rows("Equipamentos", [], [], "equipment")

    assert "nenhum equipamento cadastrado" in window.equipment_operational_status.text().lower()
    assert window.equipment_operational_status.property("level") == "warning"
    assert not window.equipment_edit_button.isEnabled()
    assert not window.board_add_button.isEnabled()

    window.render_rows(
        "Equipamentos",
        [{"id": "eq-1", "category": "Inversor", "brand": "Siemens", "boards": []}],
        [],
        "equipment",
    )
    window.equipment_search_input.setText("sem resultado")

    assert "nenhum equipamento encontrado" in window.equipment_operational_status.text().lower()
    assert "sem resultado" in window.equipment_operational_status.text()
    assert window.equipment_operational_status.property("level") == "warning"
    assert not window.equipment_edit_button.isEnabled()
    assert not window.board_add_button.isEnabled()


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
    assert window.command_stage_label.text() == "Etapa 3 de 12"
    assert "2 ferramenta" in window.tools_status_label.text()
    assert window.tools_availability_label.text() == "2 ferramentas liberadas"
    assert window.tools_specialties_label.text() == "Especialidades: Eletrica"
    assert window.tools_tabs.count() == 1
    assert window.tools_form_panel.findChildren(QTabWidget)[0] is window.tools_tabs
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


def test_tools_module_shows_empty_operational_state(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_tools([])

    assert window.active_module_key == "tools"
    assert window.tools_tabs.count() == 1
    assert window.tools_tabs.tabText(0) == "Aviso"
    assert "nenhuma ferramenta" in window.tools_status_label.text().lower()
    assert window.tools_status_label.property("level") == "warning"
    assert window.tools_availability_label.text() == "0 ferramentas liberadas"
    assert window.tools_specialties_label.text() == "Especialidades: nenhuma"


def test_equipment_hierarchy_uses_compact_full_width_sections(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_rows(
        "Equipamentos",
        [
            {
                "id": "equipment-id",
                "category": "Inversor",
                "brand": "Siemens",
                "model": "G120",
                "special_number": "ESP-1",
                "boards": [
                    {
                        "id": "board-id",
                        "name": "Placa Principal",
                        "components": [{"id": "component-id", "name": "CI"}],
                    }
                ],
            }
        ],
        [],
        "equipment",
    )

    assert window.equipment_table.maximumHeight() <= 280
    assert window.equipment_boards_table.maximumHeight() <= 280
    assert window.component_full_summary.maximumHeight() == 180


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


def test_sector_operational_status_tracks_role_and_selection(qtbot) -> None:
    admin_window = DashboardWindow()
    qtbot.addWidget(admin_window)
    admin_window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})
    admin_window.render_rows(
        "Setores",
        [
            {"id": "sector-id", "name": "Laboratorio", "description": "Bancada tecnica"},
            {"id": "sector-2", "name": "Campo", "description": "Atendimento externo"},
        ],
        [("Nome", "name")],
        "sectors",
    )

    assert admin_window.sector_operational_status.property("level") == "info"
    assert "2 setor(es) cadastrado(s)" in admin_window.sector_operational_status.text()
    assert "Admin: pode criar" in admin_window.sector_scope_status.text()

    admin_window._populate_sector_form(
        {"id": "sector-id", "name": "Laboratorio", "description": "Bancada tecnica"}
    )

    assert "Setor selecionado: Laboratorio" in admin_window.sector_operational_status.text()
    assert admin_window.sector_save_button.isEnabled()
    assert admin_window.sector_delete_button.isEnabled()

    manager_window = DashboardWindow()
    qtbot.addWidget(manager_window)
    manager_window.set_user(
        {"full_name": "Gestor", "email": "gestor@example.com", "role": "manager"}
    )
    manager_window.render_rows(
        "Setores",
        [{"id": "sector-id", "name": "Laboratorio", "description": "Bancada tecnica"}],
        [("Nome", "name")],
        "sectors",
    )
    manager_window._populate_sector_form(
        {"id": "sector-id", "name": "Laboratorio", "description": "Bancada tecnica"}
    )

    assert manager_window.sector_operational_status.property("level") == "warning"
    assert "consulta liberada" in manager_window.sector_operational_status.text()
    assert "restritas ao administrador" in manager_window.sector_scope_status.text()
    assert not manager_window.sector_save_button.isEnabled()
    assert not manager_window.sector_delete_button.isEnabled()


def test_user_operational_status_tracks_account_and_security(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})
    window.set_user_sectors([{"id": "sector-id", "name": "Laboratorio"}])
    window.render_rows(
        "Usuarios",
        [
            {
                "id": "user-id",
                "full_name": "Tecnico Teste",
                "email": "tecnico@example.com",
                "role": "technician",
                "sector_id": "sector-id",
                "is_active": False,
                "must_change_password": True,
            }
        ],
        [("Nome", "full_name")],
        "users",
    )

    assert window.user_operational_status.property("level") == "info"
    assert "1 usuario(s) carregado(s)" in window.user_operational_status.text()
    assert "senha inicial obrigatoria" in window.user_security_status.text().lower()

    window._populate_user_form(
        {
            "id": "user-id",
            "full_name": "Tecnico Teste",
            "email": "tecnico@example.com",
            "role": "technician",
            "sector_id": "sector-id",
            "is_active": False,
            "must_change_password": True,
        }
    )

    assert window.user_operational_status.property("level") == "warning"
    assert "Tecnico Teste" in window.user_operational_status.text()
    assert "Tecnico" in window.user_operational_status.text()
    assert "Laboratorio" in window.user_operational_status.text()
    assert "inativo" in window.user_operational_status.text()
    assert "Troca de senha pendente" in window.user_security_status.text()
    assert not window.user_initial_password_input.isEnabled()
    assert window.user_reset_password_button.isEnabled()


def test_password_reset_operational_status_tracks_pending_and_resolved(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.set_user({"full_name": "Gestor", "email": "gestor@example.com", "role": "manager"})
    window.render_rows(
        "Solicitacoes de senha",
        [
            {
                "id": "request-id",
                "requester_full_name": "Tecnico Teste",
                "requester_email": "tecnico@example.com",
                "requester_role": "technician",
                "status": "pending",
                "created_at": "2026-05-14T10:00:00",
            },
            {
                "id": "request-resolved",
                "requester_full_name": "Usuario Resolvido",
                "requester_email": "resolvido@example.com",
                "requester_role": "manager",
                "status": "resolved",
                "created_at": "2026-05-14T11:00:00",
            },
        ],
        [("Solicitante", "requester_full_name")],
        "password_resets",
    )

    assert window.password_reset_operational_status.property("level") == "warning"
    assert "2 solicitacao(oes) carregada(s)" in window.password_reset_operational_status.text()
    assert "1 pendente(s)" in window.password_reset_operational_status.text()

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

    assert window.password_reset_operational_status.property("level") == "warning"
    assert "Tecnico Teste" in window.password_reset_operational_status.text()
    assert "Pendente" in window.password_reset_operational_status.text()
    assert "senha temporaria" in window.password_reset_security_status.text()
    assert window.password_reset_resolve_button.isEnabled()

    window._populate_password_reset_form(
        {
            "id": "request-resolved",
            "requester_full_name": "Usuario Resolvido",
            "requester_email": "resolvido@example.com",
            "requester_role": "manager",
            "status": "resolved",
            "created_at": "2026-05-14T11:00:00",
        }
    )

    assert window.password_reset_operational_status.property("level") == "info"
    assert "Resolvida" in window.password_reset_operational_status.text()
    assert "bloqueada" in window.password_reset_security_status.text()
    assert not window.password_reset_resolve_button.isEnabled()
    assert "Status: Resolvida" in window.password_reset_full_summary.toPlainText()


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
    assert window.audit_operational_status.property("level") == "warning"
    assert "1 log(s) carregado(s)" in window.audit_operational_status.text()
    assert "1 evento(s) sensivel(is)" in window.audit_operational_status.text()
    assert "Acao: customers.delete" in summary
    assert "Entidade: Clientes" in summary
    assert "Resumo: Cliente removido" in summary
    assert "Evento sensivel: Sim" in summary
    assert not window.generic_record_container.isHidden()
    assert not window.audit_form_panel.isHidden()
    assert window.audit_delete_button.isEnabled()

    window._populate_audit_form(
        {
            "id": "log-id",
            "action": "customers.delete",
            "entity_type": "customers",
            "entity_id": "customer-id",
            "summary": "Cliente removido",
            "actor_type": "staff",
        }
    )

    assert "Evento selecionado: customers.delete" in window.audit_operational_status.text()
    assert "Retencao:" in window.audit_retention_status.text()


def test_audit_operational_status_tracks_regular_events(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_rows(
        "Logs/Auditoria",
        [
            {
                "id": "log-id",
                "action": "customers.update",
                "entity_type": "customers",
                "entity_id": "customer-id",
                "summary": "Cliente atualizado",
                "actor_type": "staff",
            }
        ],
        [("Acao", "action")],
        "audit_logs",
    )

    assert window.audit_operational_status.property("level") == "info"
    assert "1 log(s) carregado(s)" in window.audit_operational_status.text()
    window._populate_audit_form(
        {
            "id": "log-id",
            "action": "customers.update",
            "entity_type": "customers",
            "entity_id": "customer-id",
            "summary": "Cliente atualizado",
            "actor_type": "staff",
        }
    )
    assert "Evento selecionado: customers.update" in window.audit_operational_status.text()
    assert "Evento sensivel: Nao" in window.audit_full_summary.toPlainText()
