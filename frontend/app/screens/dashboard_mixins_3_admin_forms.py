from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from frontend.app.core.grid import add_widget, create_grid
from frontend.app.widgets import create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardAdminFormsMixin:
    def _build_sector_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Setor")
        title.setObjectName("sectionTitle")

        self.sector_name_input = QLineEdit()
        self.sector_name_input.setPlaceholderText("Nome do setor")

        self.sector_description_input = QLineEdit()
        self.sector_description_input.setPlaceholderText("Descricao")

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Nome", self.sector_name_input)
        form_layout.addRow("Descricao", self.sector_description_input)

        sector_fields_panel = QFrame()
        sector_fields_panel.setObjectName("formSubPanel")
        sector_fields_panel_layout = QVBoxLayout(sector_fields_panel)
        sector_fields_panel_layout.setContentsMargins(12, 12, 12, 12)
        sector_fields_panel_layout.setSpacing(8)
        sector_fields_title = QLabel("DADOS DO SETOR")
        sector_fields_title.setObjectName("formGroupTitle")
        sector_fields_panel_layout.addWidget(sector_fields_title)
        sector_fields_panel_layout.addLayout(form_layout)

        sector_details_title = QLabel("DADOS COMPLETOS")
        sector_details_title.setObjectName("formGroupTitle")
        self.sector_full_summary = create_summary_text(78, 110)

        self.sector_operational_status = QLabel(
            "Status: carregue setores para revisar a estrutura operacional."
        )
        self.sector_operational_status.setObjectName("statusBanner")
        self.sector_operational_status.setProperty("level", "warning")
        self.sector_operational_status.setWordWrap(True)

        self.sector_scope_status = QLabel(
            "Escopo: administradores mantem setores; gestores consultam a estrutura."
        )
        self.sector_scope_status.setObjectName("moduleActionHint")
        self.sector_scope_status.setWordWrap(True)

        self.sector_form_status = QLabel("")
        self.sector_form_status.setObjectName("mutedText")

        self.sector_new_button = QPushButton("Novo")
        self.sector_new_button.setObjectName("secondaryButton")
        self.sector_new_button.clicked.connect(self.clear_sector_form)

        self.sector_delete_button = QPushButton("Excluir")
        self.sector_delete_button.setObjectName("dangerButton")
        self.sector_delete_button.setEnabled(False)
        self.sector_delete_button.clicked.connect(self._request_sector_delete)

        self.sector_save_button = QPushButton("Salvar setor")
        self.sector_save_button.clicked.connect(self._request_sector_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.sector_new_button)
        actions.addWidget(self.sector_delete_button)
        actions.addWidget(self.sector_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(sector_fields_panel)
        layout.addWidget(self.sector_operational_status)
        layout.addWidget(self.sector_scope_status)
        layout.addWidget(sector_details_title)
        layout.addWidget(self.sector_full_summary)
        layout.addWidget(self.sector_form_status)
        layout.addLayout(actions)

        return panel

    def _build_user_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Usuario")
        title.setObjectName("sectionTitle")

        self.user_full_name_input = QLineEdit()
        self.user_full_name_input.setPlaceholderText("Nome completo")

        self.user_email_input = QLineEdit()
        self.user_email_input.setPlaceholderText("Email de login")

        self.user_role_combo = QComboBox()
        self.user_role_combo.addItem("Administrador", "admin")
        self.user_role_combo.addItem("Gestor/Lider", "manager")
        self.user_role_combo.addItem("Tecnico", "technician")
        self.user_role_combo.addItem("Cliente", "customer")

        self.user_sector_combo = QComboBox()

        self.user_initial_password_input = QLineEdit()
        self.user_initial_password_input.setPlaceholderText("Senha inicial")
        self.user_initial_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.user_active_checkbox = QCheckBox("Usuario ativo")
        self.user_active_checkbox.setChecked(True)

        self.user_reset_password_input = QLineEdit()
        self.user_reset_password_input.setPlaceholderText("Nova senha")
        self.user_reset_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        identity_layout = QFormLayout()
        identity_layout.setSpacing(10)
        identity_layout.addRow("Nome", self.user_full_name_input)
        identity_layout.addRow("Email", self.user_email_input)
        identity_layout.addRow("Perfil", self.user_role_combo)
        identity_layout.addRow("Setor", self.user_sector_combo)
        identity_layout.addRow("", self.user_active_checkbox)

        identity_panel = QFrame()
        identity_panel.setObjectName("formSubPanel")
        identity_panel_layout = QVBoxLayout(identity_panel)
        identity_panel_layout.setContentsMargins(12, 12, 12, 12)
        identity_panel_layout.setSpacing(8)
        identity_title = QLabel("CONTA E ACESSO")
        identity_title.setObjectName("formGroupTitle")
        identity_panel_layout.addWidget(identity_title)
        identity_panel_layout.addLayout(identity_layout)

        security_layout = QFormLayout()
        security_layout.setSpacing(10)
        security_layout.addRow("Senha inicial", self.user_initial_password_input)
        security_layout.addRow("Redefinir senha", self.user_reset_password_input)

        security_panel = QFrame()
        security_panel.setObjectName("formSubPanel")
        security_panel_layout = QVBoxLayout(security_panel)
        security_panel_layout.setContentsMargins(12, 12, 12, 12)
        security_panel_layout.setSpacing(8)
        security_title = QLabel("SEGURANCA")
        security_title.setObjectName("formGroupTitle")
        security_panel_layout.addWidget(security_title)
        security_panel_layout.addLayout(security_layout)

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, identity_panel, 0, 0, 7)
        add_widget(fields_layout, security_panel, 0, 7, 5)

        user_details_title = QLabel("DADOS COMPLETOS")
        user_details_title.setObjectName("formGroupTitle")
        self.user_full_summary = create_summary_text()

        self.user_operational_status = QLabel(
            "Status: carregue usuarios para revisar contas, perfis e setores."
        )
        self.user_operational_status.setObjectName("statusBanner")
        self.user_operational_status.setProperty("level", "warning")
        self.user_operational_status.setWordWrap(True)

        self.user_security_status = QLabel(
            "Seguranca: senha inicial obrigatoria para novas contas."
        )
        self.user_security_status.setObjectName("moduleActionHint")
        self.user_security_status.setWordWrap(True)

        self.user_form_status = QLabel("")
        self.user_form_status.setObjectName("mutedText")

        self.user_new_button = QPushButton("Novo")
        self.user_new_button.setObjectName("secondaryButton")
        self.user_new_button.clicked.connect(self.clear_user_form)

        self.user_delete_button = QPushButton("Excluir")
        self.user_delete_button.setObjectName("dangerButton")
        self.user_delete_button.setEnabled(False)
        self.user_delete_button.clicked.connect(self._request_user_delete)

        self.user_reset_password_button = QPushButton("Redefinir senha")
        self.user_reset_password_button.setObjectName("secondaryButton")
        self.user_reset_password_button.clicked.connect(self._request_user_password_reset)

        self.user_save_button = QPushButton("Salvar usuario")
        self.user_save_button.clicked.connect(self._request_user_save)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.user_new_button)
        actions.addWidget(self.user_delete_button)
        actions.addWidget(self.user_reset_password_button)
        actions.addWidget(self.user_save_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addLayout(fields_layout)
        layout.addWidget(self.user_operational_status)
        layout.addWidget(self.user_security_status)
        layout.addWidget(user_details_title)
        layout.addWidget(self.user_full_summary)
        layout.addWidget(self.user_form_status)
        layout.addLayout(actions)

        return panel

    def _build_password_reset_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("SOLICITACOES DE REDEFINICAO DE SENHA")
        title.setObjectName("sectionTitle")

        self.password_reset_requester_label = QLabel("Selecione uma solicitacao.")
        self.password_reset_requester_label.setObjectName("mutedText")
        self.password_reset_requester_label.setWordWrap(True)

        self.password_reset_new_password_input = QLineEdit()
        self.password_reset_new_password_input.setPlaceholderText("Nova senha temporaria")
        self.password_reset_new_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow("Nova senha", self.password_reset_new_password_input)

        password_reset_panel = QFrame()
        password_reset_panel.setObjectName("formSubPanel")
        password_reset_panel_layout = QVBoxLayout(password_reset_panel)
        password_reset_panel_layout.setContentsMargins(12, 12, 12, 12)
        password_reset_panel_layout.setSpacing(8)
        password_reset_title = QLabel("ATENDIMENTO DA SOLICITACAO")
        password_reset_title.setObjectName("formGroupTitle")
        password_reset_panel_layout.addWidget(password_reset_title)
        password_reset_panel_layout.addWidget(self.password_reset_requester_label)
        password_reset_panel_layout.addLayout(form_layout)

        password_reset_details_title = QLabel("DADOS COMPLETOS")
        password_reset_details_title.setObjectName("formGroupTitle")
        self.password_reset_full_summary = create_summary_text(78, 110)

        self.password_reset_operational_status = QLabel(
            "Status: carregue solicitacoes para revisar recuperacoes de acesso."
        )
        self.password_reset_operational_status.setObjectName("statusBanner")
        self.password_reset_operational_status.setProperty("level", "warning")
        self.password_reset_operational_status.setWordWrap(True)

        self.password_reset_security_status = QLabel(
            "Seguranca: selecione uma solicitacao pendente para definir senha temporaria."
        )
        self.password_reset_security_status.setObjectName("moduleActionHint")
        self.password_reset_security_status.setWordWrap(True)

        self.password_reset_form_status = QLabel("")
        self.password_reset_form_status.setObjectName("mutedText")

        self.password_reset_resolve_button = QPushButton("Redefinir senha")
        self.password_reset_resolve_button.clicked.connect(self._request_password_reset_resolve)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.password_reset_resolve_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(password_reset_panel)
        layout.addWidget(self.password_reset_operational_status)
        layout.addWidget(self.password_reset_security_status)
        layout.addWidget(password_reset_details_title)
        layout.addWidget(self.password_reset_full_summary)
        layout.addWidget(self.password_reset_form_status)
        layout.addLayout(actions)

        return panel
