from __future__ import annotations

from frontend.app.screens.dashboard import DashboardWindow


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
    assert window.password_reset_new_password_input.isReadOnly()
    assert window.password_reset_generate_button.isEnabled()
    assert window.password_reset_cancel_button.isEnabled()
    assert not window.password_reset_resolve_button.isEnabled()

    window._generate_password_reset_temporary_password()

    generated_password = window.password_reset_new_password_input.text()
    assert window._is_valid_temporary_password(generated_password)
    assert len(generated_password) == 6
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
    assert "bloqueadas" in window.password_reset_security_status.text()
    assert not window.password_reset_generate_button.isEnabled()
    assert not window.password_reset_cancel_button.isEnabled()
    assert not window.password_reset_resolve_button.isEnabled()
    assert "Status: Resolvida" in window.password_reset_full_summary.toPlainText()


def test_password_reset_cancel_action_emits_selected_request(qtbot, monkeypatch) -> None:
    window = DashboardWindow()
    qtbot.addWidget(window)
    emitted: list[str] = []
    window.password_reset_cancel_requested.connect(emitted.append)
    monkeypatch.setattr(
        "frontend.app.screens.dashboard.confirm_destructive_action",
        lambda *args, **kwargs: True,
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

    window._request_password_reset_cancel()

    assert emitted == ["request-id"]


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
