from __future__ import annotations

from frontend.app.screens.dashboard import DashboardWindow


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


def test_settings_menu_keeps_all_configuration_groups_visible(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    assert window.settings_tabs.count() == 4
    assert [window.settings_tabs.tabText(index) for index in range(4)] == [
        "Empresa",
        "Aparencia",
        "Interface e backup",
        "Resumo",
    ]
    assert window.settings_company_name_input is not None
    assert window.settings_brand_name_input is not None
    assert window.settings_theme_combo.count() == 2
    assert window.settings_backup_enabled_checkbox.text() == "Backup automatico ativo"


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
