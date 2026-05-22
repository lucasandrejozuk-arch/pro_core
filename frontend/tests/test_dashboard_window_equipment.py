from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox, QPushButton, QTabWidget

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
    assert window.equipment_operational_status.isHidden()
    assert window.equipment_hierarchy_status.isHidden()
    assert window.equipment_count_badge.text() == "1 item"
    assert window.board_count_badge.text() == "1 item"
    assert window.component_count_badge.text() == "1 item"
    assert (
        window.equipment_context_label.text() == "Equipamento: Notebook - Dell - Latitude - NE-01"
    )
    assert window.board_context_label.text() == "Objeto: Placa Principal"
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
    assert window.equipment_count_badge.text() == "1 item"


def test_equipment_operational_status_handles_empty_and_filtered_states(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows("Equipamentos", [], [], "equipment")
    assert "nenhum equipamento cadastrado" in window.equipment_operational_status.text().lower()
    assert window.equipment_operational_status.property("level") == "warning"
    assert not window.equipment_edit_button.isEnabled()
    assert not window.board_add_button.isEnabled()
    assert window.equipment_count_badge.text() == "0 itens"
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
    assert window.equipment_count_badge.text() == "0 itens"


def test_equipment_empty_click_clears_hierarchy_from_clicked_level(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.render_rows(
        "Equipamentos",
        [
            {
                "id": "equipment-id",
                "category": "Notebook",
                "brand": "Dell",
                "boards": [
                    {
                        "id": "board-id",
                        "name": "Placa Principal",
                        "components": [{"id": "component-id", "name": "C100"}],
                    }
                ],
            }
        ],
        [],
        "equipment",
    )
    window._clear_equipment_board_selection()
    assert window.selected_equipment_id == "equipment-id"
    assert window.selected_equipment_board_id is None
    assert window.selected_equipment_component_id is None
    assert window.equipment_boards_table.rowCount() == 1
    assert window.equipment_components_table.rowCount() == 0
    assert window.board_count_badge.text() == "1 item"
    assert window.component_count_badge.text() == "0 itens"
    window.equipment_boards_table.selectRow(0)
    window._clear_equipment_selection()
    assert window.selected_equipment_id is None
    assert window.selected_equipment_board_id is None
    assert window.selected_equipment_component_id is None
    assert window.equipment_boards_table.rowCount() == 0
    assert window.equipment_components_table.rowCount() == 0


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
    assert not hasattr(window, "command_stage_label")
    assert "2 ferramenta" in window.tools_status_label.text()
    assert window.tools_availability_label.text() == "2 liberadas"
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
    assert window.tools_availability_label.text() == "0 liberadas"
    assert window.tools_specialties_label.text() == "Especialidades: nenhuma"


def test_tools_resistor_assoc_requires_count_match(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    with pytest.raises(ValueError) as exc_info:
        window._calculate_resistor_assoc_tool(
            {
                "association_type": QLineEdit("paralelo"),
                "count": QLineEdit("3"),
                "values": QLineEdit("10,20"),
            }
        )
    assert "Quantidade informada" in str(exc_info.value)


def test_tools_resistor_color_supports_5_bands_and_tolerance(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    result = window._calculate_resistor_color_tool(
        {
            "bands": QLineEdit("5"),
            "digit_1": QLineEdit("1"),
            "digit_2": QLineEdit("2"),
            "digit_3": QLineEdit("3"),
            "multiplier": QLineEdit("10"),
            "tolerance": QLineEdit("1"),
        }
    )
    assert "1230" in result
    assert "Tolerancia: 1%" in result


def test_tools_awg_supports_mm2_to_awg_conversion(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    result = window._calculate_awg_tool(
        {
            "scale": QLineEdit("mm2"),
            "value": QLineEdit("2.5"),
        }
    )
    assert "AWG aproximado" in result


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
    assert (
        window.component_full_summary.maximumHeight() > window.equipment_components_table.height()
    )
    assert (
        window.component_full_summary.minimumHeight()
        >= window.equipment_components_table.minimumHeight()
    )


def test_ui_scale_slider_emits_live_scale(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[float] = []
    window.ui_scale_changed.connect(emitted.append)
    window.configure_ui_scale(0.86, 1.14, 1.0)
    window.settings_ui_scale_slider.setValue(108)
    assert emitted[-1] == 1.08
    assert window.settings_ui_scale_label.text() == "108%"
