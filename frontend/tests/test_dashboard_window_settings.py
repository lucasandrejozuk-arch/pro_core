from __future__ import annotations

from PySide6.QtCore import QSettings

from frontend.app.screens.dashboard import DashboardWindow


def test_settings_backup_interval_respects_maximum_for_selected_unit(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.settings_tabs.setCurrentIndex(3)
    window._select_combo_value(window.settings_backup_interval_unit_combo, "weeks")
    window.settings_backup_interval_input.setValue(5)

    assert window.settings_backup_interval_input.maximum() == 4
    assert window.settings_backup_interval_input.value() == 4


def test_settings_menu_keeps_all_configuration_groups_visible(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    assert window.settings_tabs.count() == 4
    assert [window.settings_tabs.tabText(index) for index in range(4)] == [
        "Empresa",
        "Aparencia",
        "Interface",
        "Backup",
    ]
    assert window.settings_company_name_input is not None
    assert window.settings_brand_name_input is not None
    assert window.settings_theme_combo.count() == 2
    assert window.settings_language_combo.count() == 2
    assert window.settings_login_cover_preset_combo.count() == 5
    assert window.settings_backup_enabled_checkbox.text() == "Backup automatico ativo"
    assert window.settings_backup_interval_unit_combo.count() == 3
    assert window.settings_backup_destination_mode_combo.count() == 2


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
            "login_cover_preset": "precision_grid",
            "login_cover_image_data_url": None,
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

    window.settings_tabs.setCurrentIndex(1)
    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_brand_name_input.setText("Pro Assist")
    window.settings_brand_subtitle_input.setText("Laboratorio tecnico")
    window._select_combo_value(window.settings_color_palette_combo, "green")
    window._select_combo_value(window.settings_theme_combo, "dark")

    window._request_settings_save()

    assert emitted[0]["brand_name"] == "Pro Assist"
    assert emitted[0]["brand_subtitle"] == "Laboratorio tecnico"
    assert emitted[0]["color_palette"] == "green"
    assert emitted[0]["theme"] == "dark"
    assert "primary_color" not in emitted[0]


def test_settings_save_uses_default_palette(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_tabs.setCurrentIndex(0)
    window.settings_company_name_input.setText("PRO CORE Lab")

    window._request_settings_save()

    assert emitted[0]["company_name"] == "PRO CORE Lab"
    assert "color_palette" not in emitted[0]


def test_settings_save_allows_appearance_only_changes(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_tabs.setCurrentIndex(1)
    window._select_combo_value(window.settings_color_palette_combo, "green")
    window._select_combo_value(window.settings_theme_combo, "dark")

    window._request_settings_save()

    assert emitted == [
        {
            "color_palette": "green",
            "theme": "dark",
        }
    ]


def test_render_settings_preserves_existing_fields_on_partial_update(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window.render_settings(
        {
            "company_name": "PRO CORE Lab",
            "trade_name": "Assistencia Teste",
            "document_number": "12.345.678/0001-90",
            "email": "contato@procore.test",
            "phone": "(11) 99999-0000",
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "blue",
            "theme": "light",
            "language": "pt-BR",
            "login_cover_preset": "precision_grid",
            "login_cover_image_data_url": None,
            "backup_enabled": True,
            "backup_interval_hours": 12,
            "backup_storage_path": "D:/backups",
            "backup_last_run_at": "2026-05-14T10:00:00",
        }
    )

    window.render_settings(
        {
            "color_palette": "green",
            "theme": "dark",
            "language": "en-US",
            "login_cover_preset": "original",
        }
    )

    assert window.settings_company_name_input.text() == "PRO CORE Lab"
    assert window.settings_trade_name_input.text() == "Assistencia Teste"
    assert window.settings_email_input.text() == "contato@procore.test"
    assert window.settings_backup_interval_input.value() == 12
    assert window.settings_backup_path_input.text() == "D:/backups"
    assert window.settings_backup_destination_mode_combo.currentData() == "custom"
    assert window.settings_brand_name_input.text() == "Pro Assist"
    assert window.settings_theme_combo.currentData() == "dark"
    assert window.settings_color_palette_combo.currentData() == "green"


def test_settings_save_requires_image_for_custom_login_cover(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_tabs.setCurrentIndex(1)
    window._select_combo_value(window.settings_login_cover_preset_combo, "custom")

    window._request_settings_save()

    assert emitted == []
    assert "capa customizada" in window.footer_message_label.text().lower()


def test_settings_save_emits_custom_login_cover_payload(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))
    image_data_url = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhg"
        "GAWjR9awAAAABJRU5ErkJggg=="
    )

    window.settings_login_cover_image_data_url = image_data_url
    window.settings_tabs.setCurrentIndex(1)
    window._select_combo_value(window.settings_login_cover_preset_combo, "custom")

    window._request_settings_save()

    assert emitted[0]["login_cover_preset"] == "custom"
    assert emitted[0]["login_cover_image_data_url"] == image_data_url


def test_settings_save_rejects_invalid_company_email(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))
    QSettings("PRO CORE", "PRO CORE").setValue("appearance/language", "pt-BR")

    window.settings_tabs.setCurrentIndex(0)
    window.settings_company_name_input.setText("PRO CORE Lab")
    window.settings_email_input.setText("contato sem arroba")

    window._request_settings_save()

    assert emitted == []
    assert "email valido" in window.footer_message_label.text().lower()


def test_settings_save_ignores_unchanged_invalid_company_email_on_appearance_update(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window._populate_settings_form(
        {
            "company_name": "PRO CORE Lab",
            "trade_name": "Assistencia Teste",
            "document_number": "12.345.678/0001-90",
            "email": "contato sem arroba",
            "phone": "(11) 99999-0000",
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "blue",
            "theme": "light",
            "language": "pt-BR",
            "login_cover_preset": "original",
            "login_cover_image_data_url": None,
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "backup_storage_path": "backups",
            "backup_last_run_at": None,
        }
    )
    window.settings_tabs.setCurrentIndex(1)
    window._select_combo_value(window.settings_color_palette_combo, "green")
    window._select_combo_value(window.settings_theme_combo, "dark")

    window._request_settings_save()

    assert emitted == [
        {
            "color_palette": "green",
            "theme": "dark",
        }
    ]


def test_settings_save_uses_form_snapshot_when_current_settings_is_stale(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window._populate_settings_form(
        {
            "company_name": "PRO CORE Lab",
            "trade_name": "Assistencia Teste",
            "document_number": "12.345.678/0001-90",
            "email": "contato@procore.test",
            "phone": "(11) 99999-0000",
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "blue",
            "theme": "light",
            "language": "pt-BR",
            "login_cover_preset": "original",
            "login_cover_image_data_url": None,
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "backup_storage_path": "backups",
            "backup_last_run_at": None,
        }
    )
    window.current_settings = {}
    window.settings_tabs.setCurrentIndex(1)
    window._select_combo_value(window.settings_color_palette_combo, "green")
    window._select_combo_value(window.settings_theme_combo, "dark")

    window._request_settings_save()

    assert emitted == [
        {
            "color_palette": "green",
            "theme": "dark",
        }
    ]


def test_settings_save_allows_language_only_change_without_company_validation(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window._populate_settings_form(
        {
            "company_name": "PRO CORE Lab",
            "trade_name": "Assistencia Teste",
            "document_number": "12.345.678/0001-90",
            "email": "contato sem arroba",
            "phone": "(11) 99999-0000",
            "brand_name": "Pro Assist",
            "brand_subtitle": "Laboratorio tecnico",
            "color_palette": "blue",
            "theme": "light",
            "language": "pt-BR",
            "login_cover_preset": "original",
            "login_cover_image_data_url": None,
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "backup_storage_path": "backups",
            "backup_last_run_at": None,
        }
    )
    window.settings_tabs.setCurrentIndex(2)
    window._select_combo_value(window.settings_language_combo, "en-US")

    window._request_settings_save()

    assert emitted == [{"language": "en-US"}]


def test_settings_backup_tab_supports_time_scale_and_destination_modes(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[dict] = []
    window.settings_update_requested.connect(lambda payload: emitted.append(payload))

    window.settings_tabs.setCurrentIndex(3)
    window._select_combo_value(window.settings_backup_interval_unit_combo, "days")
    window.settings_backup_interval_input.setValue(3)
    window._select_combo_value(window.settings_backup_destination_mode_combo, "custom")
    window.settings_backup_path_input.setText("D:/pro-core/backups")

    window._request_settings_save()

    assert emitted == [
        {
            "backup_interval_hours": 72,
            "backup_storage_path": "D:/pro-core/backups",
        }
    ]


def test_settings_backup_internal_destination_locks_default_path(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._select_combo_value(window.settings_backup_destination_mode_combo, "internal")

    assert window.settings_backup_path_input.isReadOnly() is True
    assert window.settings_backup_browse_button.isEnabled() is False
    assert window.settings_backup_path_input.text() == "backups"


def test_settings_form_backup_texts_translate_to_english(qtbot) -> None:
    settings = QSettings("PRO CORE", "PRO CORE")
    settings.setValue("appearance/language", "en-US")
    window = DashboardWindow()
    qtbot.addWidget(window)

    window._populate_settings_form(
        {
            "company_name": "PRO CORE Lab",
            "brand_name": "Pro Assist",
            "theme": "dark",
            "language": "en-US",
            "backup_enabled": True,
            "backup_interval_hours": 48,
            "backup_storage_path": "backups",
            "backup_last_run_at": None,
        }
    )
    from frontend.app.core.i18n import apply_language_to_widgets

    apply_language_to_widgets("en-US", window)

    assert window.settings_tabs.tabText(3) == "Backup"
    assert window.settings_backup_enabled_checkbox.text() == "Automatic backup enabled"
    assert window.settings_backup_interval_unit_combo.itemText(1) == "Days"
    assert window.settings_backup_destination_mode_combo.itemText(0) == "Internal Pro Core folder"
    assert "Identity" in window.settings_operational_status.text()
