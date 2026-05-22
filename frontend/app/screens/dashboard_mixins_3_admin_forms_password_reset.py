from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from frontend.app.core.grid import add_widget, create_grid
from frontend.app.widgets import create_summary_text


class DashboardAdminPasswordResetFormMixin:
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
        self.password_reset_new_password_input.setReadOnly(True)
        self.password_reset_new_password_input.setToolTip(
            "Use o botao Gerar senha para preencher a senha temporaria."
        )
        self.password_reset_generate_button = QPushButton("Gerar senha")
        self.password_reset_generate_button.setObjectName("secondaryButton")
        self.password_reset_generate_button.clicked.connect(
            self._generate_password_reset_temporary_password
        )

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        password_row = QHBoxLayout()
        password_row.setContentsMargins(0, 0, 0, 0)
        password_row.setSpacing(8)
        password_row.addWidget(self.password_reset_new_password_input, 1)
        password_row.addWidget(self.password_reset_generate_button)
        form_layout.addRow("Nova senha", password_row)

        password_reset_panel = QFrame()
        password_reset_panel.setObjectName("formSubPanel")
        password_reset_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
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
        password_reset_details_panel = self._build_admin_details_panel(
            password_reset_details_title,
            self.password_reset_full_summary,
        )

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
        self.password_reset_cancel_button = QPushButton("Ignorar solicitacao")
        self.password_reset_cancel_button.setObjectName("secondaryButton")
        self.password_reset_cancel_button.clicked.connect(self._request_password_reset_cancel)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.password_reset_cancel_button)
        actions.addWidget(self.password_reset_resolve_button)

        content_layout = create_grid(spacing=10)
        add_widget(content_layout, password_reset_panel, 0, 0, 6)
        add_widget(content_layout, password_reset_details_panel, 0, 6, 6)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.password_reset_operational_status)
        layout.addWidget(self.password_reset_security_status)
        layout.addLayout(content_layout)
        layout.addWidget(self.password_reset_form_status)
        layout.addLayout(actions)

        return panel
