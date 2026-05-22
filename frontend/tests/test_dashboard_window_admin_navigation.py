from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt

from frontend.app.screens.dashboard import DashboardWindow


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
    assert not hasattr(window, "session_module_label")


def test_sidebar_settings_admin_logout_and_exit_icons_are_distinct(qtbot) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)

    assert window.module_icon_names["admin_area"] == "admin"
    assert window.module_icon_names["settings"] == "settings"
    assert window.sidebar_buttons_by_icon[window.logout_button] == "logout"
    assert window.sidebar_buttons_by_icon[window.exit_button] == "exit"


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
        "resource_access",
        "password_resets",
        "audit_logs",
        "settings",
    )


def test_admin_area_shows_role_scope_and_available_modules(qtbot) -> None:
    admin_window = DashboardWindow()
    qtbot.addWidget(admin_window)
    admin_window.set_user({"full_name": "Admin", "email": "admin@example.com", "role": "admin"})
    admin_window.render_admin_area()

    assert admin_window.admin_area_status_label.property("level") == "info"
    assert "Administrador" in admin_window.admin_area_status_label.text()
    assert "Setores" in admin_window.admin_area_scope_label.text()
    assert "Acessos de recursos" in admin_window.admin_area_scope_label.text()
    assert "Logs/Auditoria" in admin_window.admin_area_scope_label.text()
    assert admin_window.admin_area_panel.layout().alignment() & Qt.AlignmentFlag.AlignTop
    assert admin_window.admin_area_status_label.maximumHeight() == 42
    assert admin_window.admin_area_actions_panel.objectName() == "formSubPanel"
    assert admin_window.admin_area_actions_layout.getItemPosition(0) == (0, 0, 1, 12)
    assert admin_window.admin_area_actions_layout.getItemPosition(1) == (0, 6, 1, 6)
    assert admin_window.admin_area_actions_layout.getItemPosition(2) == (1, 0, 1, 6)
    assert admin_window.admin_area_actions_layout.getItemPosition(3) == (1, 6, 1, 6)
    admin_actions_text = [
        admin_window.admin_area_actions_layout.itemAt(index).widget().text()
        for index in range(admin_window.admin_area_actions_layout.count())
    ]
    assert "Portal do cliente (navegador)" in admin_actions_text

    manager_window = DashboardWindow()
    qtbot.addWidget(manager_window)
    manager_window.set_user(
        {"full_name": "Gestor", "email": "gestor@example.com", "role": "manager"}
    )
    manager_window.render_admin_area()

    assert manager_window.admin_area_status_label.property("level") == "info"
    assert "Gestor" in manager_window.admin_area_status_label.text()
    assert "Setores" in manager_window.admin_area_scope_label.text()
    assert "Acessos de recursos" in manager_window.admin_area_scope_label.text()
    assert "Solicitacoes de senha" in manager_window.admin_area_scope_label.text()
    assert "Logs/Auditoria" not in manager_window.admin_area_scope_label.text()
    manager_actions_text = [
        manager_window.admin_area_actions_layout.itemAt(index).widget().text()
        for index in range(manager_window.admin_area_actions_layout.count())
    ]
    assert "Portal do cliente (navegador)" not in manager_actions_text

    technician_window = DashboardWindow()
    qtbot.addWidget(technician_window)
    technician_window.set_user(
        {"full_name": "Tecnico", "email": "tecnico@example.com", "role": "technician"}
    )
    technician_window.render_admin_area()

    assert technician_window.admin_area_status_label.property("level") == "error"
    assert "nao possui acesso" in technician_window.admin_area_status_label.text()
    assert "nenhum" in technician_window.admin_area_scope_label.text()
