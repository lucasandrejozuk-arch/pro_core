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
    assert window.settings_form_status.text() == ""
    assert "1 e 720" in window.footer_message_label.text()


def test_settings_menu_keeps_all_configuration_groups_visible(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    assert window.settings_tabs.count() == 3
    assert [window.settings_tabs.tabText(index) for index in range(3)] == [
        "Empresa",
        "Aparencia e interface",
        "Backup",
    ]
    assert window.settings_company_name_input is not None
    assert window.settings_brand_name_input is not None
    assert window.settings_theme_combo.count() == 2
    assert window.settings_language_combo.count() == 2
    assert window.settings_backup_enabled_checkbox.text() == "Backup automatico ativo"


def test_settings_operational_status_tracks_identity_interface_and_backup(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    window.configure_ui_scale(0.82, 1.18, 1.08)

    window._populate_settings_form(
        {
            "company_name": "PRO CORE Lab",
            "trade_name": "Assistencia Teste",
            "brand_name": "Pro Assist",
            "brand_subtitle": "Bancada premium",
            "color_palette": "green",
            "theme": "dark",
            "language": "pt-BR",
            "backup_enabled": True,
            "backup_interval_hours": 12,
            "backup_storage_path": "D:/backups",
            "backup_last_run_at": "2026-05-14T10:00:00",
        }
    )

    assert window.settings_operational_status.property("level") == "info"
    assert "Pro Assist" in window.settings_operational_status.text()
    assert "PRO CORE Lab" in window.settings_operational_status.text()
    assert "Escala: 108%" in window.settings_operational_status.text()
    assert "backup: ativo" in window.settings_backup_status.text().lower()
    assert "intervalo 12h" in window.settings_backup_status.text()
    assert "D:/backups" in window.settings_backup_status.text()

    window.settings_ui_scale_slider.setValue(112)

    assert "Escala: 112%" in window.settings_operational_status.text()


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
    assert emitted[0]["language"] == "en-US"
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


def test_settings_save_rejects_invalid_company_email(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_email_input.setText("contato sem arroba")
    window.settings_backup_interval_input.setText("24")
    window.settings_backup_path_input.setText("backups")

    window._request_settings_save()

    assert emitted == []
    assert "email valido" in window.footer_message_label.text().lower()
